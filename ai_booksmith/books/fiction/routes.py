import os
import json
import uuid
import re
import io
import time
import zipfile
import requests
import pypandoc
from flask import Blueprint, render_template, request, redirect, url_for, session, abort, send_file, current_app, jsonify
from ai_booksmith.mock_provider import mock_openai_chat_completion, mock_leonardo_image_generation
from ai_booksmith.config_manager import get_config, get_model_config
from ai_booksmith.llm_provider import get_llm_client
from ai_booksmith.image_gen_provider import get_image_gen_client

fiction_bp = Blueprint('fiction', __name__, template_folder='templates/fiction', url_prefix='/fiction')

PROJECTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'projects'))

def load_project(project_id):
    filepath = os.path.join(PROJECTS_DIR, f"{project_id}.json")
    if not os.path.exists(filepath): return None
    with open(filepath, 'r', encoding='utf-8') as f: return json.load(f)

def save_project(project_data):
    # Ensure the projects directory exists
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    filepath = os.path.join(PROJECTS_DIR, f"{project_data['id']}.json")
    with open(filepath, 'w', encoding='utf-8') as f: json.dump(project_data, f, indent=4, ensure_ascii=False)

def parse_chapters_from_synopsis(synopsis):
    return re.findall(r'#+\s*Chapter\s*\d+[:\s]*(.*)', synopsis)

def generate_images_for_chapter(project, chapter_index):
    config = get_config()
    model_config = get_model_config()
    llm_client = get_llm_client()
    image_gen_client = get_image_gen_client()

    chapter_text = project['chapters'][chapter_index]['text']
    art_style = project['art_style']
    is_bw = project.get('final_settings', {}).get('interior_color') == 'bw'
    scene_prompt = f'Read the following chapter. Identify 3 visually interesting scenes to illustrate. Return a JSON object: {{"scenes": ["scene1", "scene2", "scene3"]}}'

    active_openai_model_name = config.get('active_openai_model')
    openai_model_id = next((m['id'] for m in model_config['openai'] if m['name'] == active_openai_model_name), None)

    try:
        if config['provider'] == 'mock':
            response = mock_openai_chat_completion(model=None, messages=[{"role":"user", "content":scene_prompt}])
        else:
            response = llm_client.chat.completions.create(model=openai_model_id, messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": scene_prompt + f"---{chapter_text[:4000]}---"}], response_format={"type": "json_object"})
        scenes = json.loads(response.choices[0].message.content).get('scenes', [])
    except Exception as e:
        print(f"Error generating image prompts: {e}")
        scenes = []

    generated_images = []
    active_leonardo_model_name = config.get('active_leonardo_model')
    leonardo_model_id = next((m['id'] for m in model_config['leonardo'] if m['name'] == active_leonardo_model_name), None)

    for scene_desc in scenes:
        try:
            if config['provider'] == 'mock':
                mock_response = mock_leonardo_image_generation(prompt=scene_desc)
                image_url = mock_response['generations_by_pk']['generated_images'][0]['url']
                generated_images.append({"prompt": scene_desc, "url": image_url})
            else:
                bw_prompt = "black and white, grayscale, " if is_bw else ""
                image_prompt = f"{scene_desc}, {bw_prompt}in the style of {art_style}"
                generation_id = image_gen_client.generate(image_prompt, model_id=leonardo_model_id)
                image_url = image_gen_client.poll_for_image(generation_id)
                if image_url:
                    generated_images.append({"prompt": scene_desc, "url": image_url})
        except Exception as e: print(f"Error generating image: {e}")
    project['chapters'][chapter_index]['images'] = generated_images
    save_project(project)

def generate_kdp_metadata(project):
    config = get_config()
    model_config = get_model_config()
    llm_client = get_llm_client()
    language = project.get('language', 'English')
    prompt = f"You are a book marketing expert for Amazon KDP. For a book with title '{project['title']}' and description '{project.get('final_settings',{}).get('description', project['logline'])}', generate KDP metadata. Provide JSON with keys: 'keywords' (a list of 7 relevant strings) and 'categories' (a list of 2 relevant strings from the official KDP category list). Provide keywords in {language}."

    active_openai_model_name = config.get('active_openai_model')
    openai_model_id = next((m['id'] for m in model_config['openai'] if m['name'] == active_openai_model_name), None)

    try:
        if config['provider'] == 'mock':
            response = mock_openai_chat_completion(model=None, messages=[{"role":"user", "content":prompt}])
        else:
            response = llm_client.chat.completions.create(model=openai_model_id, messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": prompt}], response_format={"type": "json_object"})
        metadata = json.loads(response.choices[0].message.content)
        return f"Keywords:\n- " + "\n- ".join(metadata.get('keywords', [])) + "\n\nCategories:\n- " + "\n- ".join(metadata.get('categories', []))
    except Exception as e: return f"Error generating metadata: {e}"

@fiction_bp.route('/')
def fiction_dashboard():
    return render_template('dashboard.html')

@fiction_bp.route('/new')
def new_project_form():
    theme_data = session.get('selected_theme', {})
    return render_template('idea_form.html', theme_data=theme_data)

@fiction_bp.route('/generate_ideas', methods=['POST'])
def generate_ideas():
    config = get_config()
    model_config = get_model_config()
    llm_client = get_llm_client()
    form_data = request.form.to_dict()
    prompt = f'You are a creative assistant. Based on Genre: "{form_data["genre"]}" and Description: "{form_data["description"]}", generate 10 book ideas. Target word count is {form_data["word_count"]}. For each, provide: "title", "logline", "writing_style", "art_style". Return as JSON. Write all text in {form_data["language"]}.'

    active_openai_model_name = config.get('active_openai_model')
    openai_model_id = next((m['id'] for m in model_config['openai'] if m['name'] == active_openai_model_name), None)

    try:
        if config['provider'] == 'mock':
            response = mock_openai_chat_completion(model=None, messages=[{"role":"user", "content":prompt}])
        else:
            response = llm_client.chat.completions.create(model=openai_model_id, messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
        ideas = json.loads(response.choices[0].message.content).get('ideas', [])
    except Exception as e: ideas = []
    session['ideas'] = ideas
    session['project_context'] = form_data
    return render_template('ideas.html', ideas=ideas)

@fiction_bp.route('/select_idea', methods=['POST'])
def select_idea():
    selected_index = int(request.form.get('selected_idea_index'))
    ideas, context = session.get('ideas'), session.get('project_context', {})
    selected_idea = ideas[selected_index]
    project_id = str(uuid.uuid4())
    project_data = {"id": project_id, "book_type": 'fiction', **context, **selected_idea, "synopsis": "", "back_cover_blurb": "", "chapters": []}
    save_project(project_data)
    return redirect(url_for('.blueprint', project_id=project_id))

@fiction_bp.route('/<project_id>/blueprint')
def blueprint(project_id):
    return render_template('blueprint.html', project=load_project(project_id))

@fiction_bp.route('/<project_id>/generate_blueprint', methods=['POST'])
def generate_blueprint(project_id):
    config = get_config()
    model_config = get_model_config()
    llm_client = get_llm_client()
    project = load_project(project_id)
    language = project.get('language', 'English')
    word_count = project.get('word_count', 20000)
    prompt = f"You are a master storyteller. For a {word_count}-word book titled '{project['title']}', generate a detailed, multi-chapter synopsis and a compelling back cover blurb. Return as JSON with keys 'synopsis' and 'back_cover_blurb'. Write all text content in {language}."

    active_openai_model_name = config.get('active_openai_model')
    openai_model_id = next((m['id'] for m in model_config['openai'] if m['name'] == active_openai_model_name), None)

    try:
        if config['provider'] == 'mock':
            response = mock_openai_chat_completion(model=None, messages=[{"role":"user", "content":prompt}])
        else:
            response = llm_client.chat.completions.create(model=openai_model_id, messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": prompt}], response_format={"type": "json_object"})
        data = json.loads(response.choices[0].message.content)
        project['synopsis'], project['back_cover_blurb'] = data.get('synopsis', 'Error.'), data.get('back_cover_blurb', 'Error.')
    except Exception as e:
        project['synopsis'], project['back_cover_blurb'] = f"An error occurred: {e}", f"An error occurred: {e}"
    save_project(project)
    return redirect(url_for('.blueprint', project_id=project_id))

@fiction_bp.route('/<project_id>/writing_room')
def writing_room(project_id):
    project = load_project(project_id)
    if not project.get('chapters') and project.get('synopsis'):
        project['chapters'] = [{"title": title, "status": "Not Generated", "text": "", "images": []} for title in parse_chapters_from_synopsis(project['synopsis'])]
        save_project(project)
    chapter_index = request.args.get('chapter_index', 0, type=int)
    current_chapter = project['chapters'][chapter_index]
    return render_template('writing_room.html', project=project, current_chapter=current_chapter, current_chapter_index=chapter_index)

@fiction_bp.route('/<project_id>/generate_chapter/<int:chapter_index>', methods=['POST'])
def generate_chapter(project_id, chapter_index):
    config = get_config()
    model_config = get_model_config()
    llm_client = get_llm_client()
    project = load_project(project_id)
    language = project.get('language', 'English')
    num_chapters = len(project['chapters'])
    words_per_chapter = int(project.get('word_count', 20000)) / num_chapters if num_chapters > 0 else 2000
    previous_chapters_text = "\\n\\n".join([ch['text'] for i, ch in enumerate(project['chapters']) if i < chapter_index and ch['status'] == 'Approved'])
    context_summary = f"Summary of previous chapters:\\n{previous_chapters_text[:5000]}..." if previous_chapters_text else "This is the first chapter."
    prompt = f"You are a novelist. Write the full text for Chapter {chapter_index + 1}: {project['chapters'][chapter_index]['title']}. Chapter should be ~{words_per_chapter:.0f} words. Write in {language}. Context: {context_summary}."

    active_openai_model_name = config.get('active_openai_model')
    openai_model_id = next((m['id'] for m in model_config['openai'] if m['name'] == active_openai_model_name), None)

    try:
        if config['provider'] == 'mock':
            response = mock_openai_chat_completion(model=None, messages=[{"role":"user", "content":prompt}])
        else:
            response = llm_client.chat.completions.create(model=openai_model_id, messages=[{"role": "user", "content": prompt}])
        project['chapters'][chapter_index]['text'] = response.choices[0].message.content
        project['chapters'][chapter_index]['status'] = 'Generated'
        save_project(project)
    except Exception as e: print(f"Error generating chapter: {e}")
    return redirect(url_for('.writing_room', project_id=project_id, chapter_index=chapter_index))

@fiction_bp.route('/<project_id>/save_chapter/<int:chapter_index>', methods=['POST'])
def save_chapter(project_id, chapter_index):
    project = load_project(project_id)
    project['chapters'][chapter_index]['text'] = request.form.get('chapter_text')
    project['chapters'][chapter_index]['status'] = 'Approved'
    save_project(project)
    # Redirect back to the same chapter page
    return redirect(url_for('.writing_room', project_id=project_id, chapter_index=chapter_index))

@fiction_bp.route('/<project_id>/<int:chapter_index>/generate_images', methods=['POST'])
def generate_images_for_chapter_route(project_id, chapter_index):
    project = load_project(project_id)
    generate_images_for_chapter(project, chapter_index)
    return redirect(url_for('.writing_room', project_id=project_id, chapter_index=chapter_index))

@fiction_bp.route('/<project_id>/auto_approve_all', methods=['POST'])
def auto_approve_all(project_id):
    # This would be a background task in a real app
    return redirect(url_for('.writing_room', project_id=project_id))

@fiction_bp.route('/<project_id>/finalize')
def finalize(project_id):
    return render_template('finalize.html', project=load_project(project_id))

@fiction_bp.route('/<project_id>/build_package', methods=['POST'])
def build_package(project_id):
    project = load_project(project_id)
    settings = request.form.to_dict()
    project['final_settings'] = settings
    save_project(project)

    author = settings.get('author_name', 'A.I. Author')
    title = project.get('title', 'Untitled Book')

    markdown_content = f"---\ntitle: {title}\nauthor: {author}\n---\n\n"
    for i, chapter in enumerate(project['chapters']):
        markdown_content += f"# Chapter {i+1}: {chapter['title']}\n\n"
        markdown_content += chapter['text'] + "\n\n"
        for image in chapter.get('images', []):
            markdown_content += f"![{image['prompt']}]({image['url']})\n\n"

    try:
        width_mm = settings.get('trim_width_mm', '152')
        height_mm = settings.get('trim_height_mm', '229')
        extra_args = ['-V', f'geometry:paperwidth={width_mm}mm', '-V', f'geometry:paperheight={height_mm}mm', '-V', 'geometry:margin=1in']
        output_pdf = pypandoc.convert_text(markdown_content, 'pdf', format='md', extra_args=extra_args)
    except Exception as e:
        print(f"Error generating PDF with Pandoc: {e}")
        output_pdf = markdown_content.encode('utf-8')
        return send_file(io.BytesIO(output_pdf), as_attachment=True, download_name='book_content.md', mimetype='text/markdown')

    cover_md = f"---\ntitle: {title}\nauthor: {author}\n---\n"
    cover_pdf = pypandoc.convert_text(cover_md, 'pdf', format='md', extra_args=extra_args)
    metadata_text = generate_kdp_metadata(project)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(f'{title}_manuscript.pdf', output_pdf)
        zip_file.writestr(f'{title}_cover.pdf', cover_pdf)
        zip_file.writestr('kdp_metadata.txt', metadata_text)

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name=f'book_package_{title}.zip', mimetype='application/zip')

@fiction_bp.route('/brainstorm_themes', methods=['POST'])
def brainstorm_themes():
    """
    Calls the LLM to brainstorm a few genre/theme pairs and returns them as JSON.
    """
    llm_client = get_llm_client()
    config = get_config()

    prompt = "Brainstorm 5 interesting and unique genre-and-theme pairs for a new fiction book. For each, provide a 'genre' and a 'theme' (which is a short, evocative description). Return as a JSON object with a single key 'suggestions' which is a list of these pairs."

    try:
        if config['provider'] == 'mock':
            # In a real mock, you'd have structured data here.
            # For now, let's create some plausible mock suggestions.
            suggestions = {
                "suggestions": [
                    {"genre": "Steampunk", "theme": "A clockwork detective solves a murder in a city powered by steam and secrets."},
                    {"genre": "Biopunk", "theme": "A group of rebels uses illegal genetic modifications to fight a corporate dystopia."},
                    {"genre": "Mythic Fantasy", "theme": "A young cartographer discovers that the maps of the old gods are real and lead to other worlds."},
                    {"genre": "Solarpunk", "theme": "A community of architects builds a sustainable city in harmony with nature after an ecological collapse."},
                    {"genre": "Gothic Romance", "theme": "A governess in a remote, crumbling manor discovers her employer is haunted by a beautiful, tragic ghost."}
                ]
            }
            response_json = json.dumps(suggestions)
        else:
            response = llm_client.chat.completions.create(
                model=config.get('active_openai_model'),
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            response_json = response.choices[0].message.content

        return jsonify(json.loads(response_json))

    except Exception as e:
        print(f"Error brainstorming themes: {e}")
        return jsonify({"error": "Failed to brainstorm themes."}), 500
