import os
import json
import uuid
import re
import io
import time
import zipfile
import openai
import requests
from flask import Blueprint, render_template, request, redirect, url_for, session, abort, send_file
from weasyprint import HTML, CSS

# --- Blueprint Setup ---
fiction_bp = Blueprint('fiction', __name__,
                       template_folder='templates',
                       url_prefix='/fiction')

# --- Config and Helpers ---
LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY", "user-provided-key")
LEONARDO_API_URL = "https://cloud.leonardo.ai/api/rest/v1"
LEONARDO_ENABLED = LEONARDO_API_KEY != "user-provided-key"
# Correctly navigate up two directories from routes.py to get to ai_booksmith/, then down to projects/
PROJECTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'projects'))

def load_project(project_id):
    filepath = os.path.join(PROJECTS_DIR, f"{project_id}.json")
    if not os.path.exists(filepath): return None
    with open(filepath, 'r', encoding='utf-8') as f: return json.load(f)

def save_project(project_data):
    filepath = os.path.join(PROJECTS_DIR, f"{project_data['id']}.json")
    with open(filepath, 'w', encoding='utf-8') as f: json.dump(project_data, f, indent=4, ensure_ascii=False)

def parse_chapters_from_synopsis(synopsis):
    chapters = re.findall(r'#+\s*Chapter\s*\d+[:\s]*(.*)', synopsis)
    return [title.strip() for title in chapters]

def generate_images_for_chapter(project, chapter_index):
    if not LEONARDO_ENABLED:
        print("Leonardo API not configured. Skipping image generation.")
        return
    chapter_text = project['chapters'][chapter_index]['text']
    art_style = project['art_style']
    is_bw = project.get('final_settings', {}).get('interior_color') == 'bw'
    scene_prompt = f'Read the following chapter. Identify 3 visually interesting scenes to illustrate. Return a JSON object: {{"scenes": ["scene1", "scene2", "scene3"]}}'
    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": scene_prompt + f"---{chapter_text[:4000]}---"}])
        scenes = json.loads(response.choices[0].message['content']).get('scenes', [])
    except Exception as e:
        print(f"Error generating image prompts: {e}")
        return
    headers = {"accept": "application/json", "content-type": "application/json", "authorization": f"Bearer {LEONARDO_API_KEY}"}
    generated_images = []
    for scene_desc in scenes:
        bw_prompt = "black and white, grayscale, monochrome, " if is_bw else ""
        payload = {"prompt": f"{scene_desc}, {bw_prompt}in the style of {art_style}", "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3", "width": 512, "height": 768, "num_images": 1, "guidance_scale": 7, "photoReal": (not is_bw), "alchemy": True, "presetStyle": "CINEMATIC" if not is_bw else "NONE"}
        try:
            response = requests.post(f"{LEONARDO_API_URL}/generations", json=payload, headers=headers)
            response.raise_for_status()
            generation_id = response.json()['sdGenerationJob']['generationId']
            for _ in range(10):
                time.sleep(6)
                get_response = requests.get(f"{LEONARDO_API_URL}/generations/{generation_id}", headers=headers)
                get_response.raise_for_status()
                job_status = get_response.json()['generations_by_pk']['status']
                if job_status == 'COMPLETE':
                    image_url = get_response.json()['generations_by_pk']['generated_images'][0]['url']
                    generated_images.append({"prompt": scene_desc, "url": image_url})
                    break
            else: generated_images.append({"prompt": scene_desc, "url": f"https://placehold.co/512x768?text=Timeout"})
        except Exception as e:
            print(f"Error generating image with Leonardo: {e}")
            generated_images.append({"prompt": scene_desc, "url": f"https://placehold.co/512x768?text=API+Error"})
    project['chapters'][chapter_index]['images'] = generated_images
    save_project(project)

def generate_kdp_metadata(project):
    language = project.get('language', 'English')
    prompt = f"You are a book marketing expert. For a book with title '{project['title']}' and description '{project.get('final_settings',{}).get('description', project['logline'])}', generate KDP metadata. Provide JSON with keys: 'keywords' (list of 7 strings) and 'categories' (list of 2 strings). Provide keywords in {language}."
    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": prompt}])
        metadata = json.loads(response.choices[0].message['content'])
        return f"Keywords:\n- " + "\n- ".join(metadata.get('keywords', [])) + "\n\nCategories:\n- " + "\n- ".join(metadata.get('categories', []))
    except Exception as e: return f"Error generating metadata: {e}"

# --- Routes ---
@fiction_bp.route('/new')
def new_project_form():
    # Pre-fill form with data from the brainstorming session
    theme = session.get('selected_theme', {})
    return render_template('idea_form.html', theme=theme)

@fiction_bp.route('/generate_ideas', methods=['POST'])
def generate_ideas():
    form_data = request.form.to_dict()
    if not all(k in form_data for k in ['language', 'genre', 'description', 'word_count']): return redirect(url_for('.new_project_form'))
    if openai.api_key == "user-provided-key": return "ERROR: OpenAI API key is not set."
    prompt = f'You are a creative assistant. Based on Genre: "{form_data["genre"]}" and Description: "{form_data["description"]}", generate 10 book ideas. The target word count is {form_data["word_count"]}. For each, provide: "title", "logline", "writing_style", "art_style". Return as JSON with a key "ideas". Write all text content in {form_data["language"]}.'
    try:
        response = openai.ChatCompletion.create(model="gpt-4-turbo", messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": prompt}])
        ideas = json.loads(response.choices[0].message['content']).get('ideas', [])
    except Exception as e: return f"An error occurred: {e}"
    if not ideas: return "Error: Could not generate ideas."
    session['ideas'] = ideas
    session['project_context'] = form_data
    return render_template('ideas.html', ideas=ideas)

@fiction_bp.route('/select_idea', methods=['POST'])
def select_idea():
    selected_index = int(request.form.get('selected_idea_index'))
    ideas, context = session.get('ideas'), session.get('project_context', {})
    if not ideas or selected_index >= len(ideas): return redirect(url_for('index'))
    selected_idea = ideas[selected_index]
    project_id = str(uuid.uuid4())
    project_data = {
        "id": project_id, "book_type": 'fiction', "language": context.get('language'),
        "genre": context.get('genre'), "description": context.get('description'), "word_count": context.get('word_count'),
        "title": selected_idea.get('title'), "logline": selected_idea.get('logline'),
        "writing_style": selected_idea.get('writing_style'), "art_style": selected_idea.get('art_style'),
        "synopsis": "", "back_cover_blurb": "", "chapters": []
    }
    save_project(project_data)
    return redirect(url_for('.blueprint', project_id=project_id))

@fiction_bp.route('/<project_id>/blueprint')
def blueprint(project_id):
    project = load_project(project_id)
    if not project: abort(404)
    return render_template('blueprint.html', project=project)

@fiction_bp.route('/<project_id>/generate_blueprint', methods=['POST'])
def generate_blueprint(project_id):
    project = load_project(project_id)
    if not project: abort(404)
    language = project.get('language', 'English')
    word_count = project.get('word_count', 20000)
    prompt = f"You are a master storyteller. For a {word_count}-word book titled '{project['title']}', generate a detailed, multi-chapter synopsis and a compelling back cover blurb. Return as JSON with keys 'synopsis' and 'back_cover_blurb'. Write all text content in {language}."
    try:
        response = openai.ChatCompletion.create(model="gpt-4-turbo", messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": prompt}])
        data = json.loads(response.choices[0].message['content'])
        project['synopsis'], project['back_cover_blurb'] = data.get('synopsis', 'Error.'), data.get('back_cover_blurb', 'Error.')
    except Exception as e:
        project['synopsis'], project['back_cover_blurb'] = f"An error occurred: {e}", f"An error occurred: {e}"
    save_project(project)
    return redirect(url_for('.blueprint', project_id=project_id))

@fiction_bp.route('/<project_id>/writing_room')
def writing_room(project_id):
    project = load_project(project_id)
    if not project: abort(404)
    if not project.get('chapters') and project.get('synopsis'):
        chapter_titles = parse_chapters_from_synopsis(project['synopsis'])
        project['chapters'] = [{"title": title, "status": "Not Generated", "text": "", "images": []} for title in chapter_titles]
        save_project(project)
    chapter_index = request.args.get('chapter_index', 0, type=int)
    if not project.get('chapters') or chapter_index >= len(project['chapters']): return "Please generate a synopsis and chapters first."
    current_chapter = project['chapters'][chapter_index]
    return render_template('writing_room.html', project=project, current_chapter=current_chapter, current_chapter_index=chapter_index)

@fiction_bp.route('/<project_id>/generate_chapter/<int:chapter_index>', methods=['POST'])
def generate_chapter(project_id, chapter_index):
    project = load_project(project_id)
    if not project or chapter_index >= len(project['chapters']): abort(404)
    language = project.get('language', 'English')
    num_chapters = len(project['chapters'])
    words_per_chapter = int(project.get('word_count', 20000)) / num_chapters if num_chapters > 0 else 2000
    previous_chapters_text = "\\n\\n".join([ch['text'] for i, ch in enumerate(project['chapters']) if i < chapter_index and ch['status'] == 'Approved'])
    context_summary = f"Summary of previous chapters:\\n{previous_chapters_text[:5000]}..." if previous_chapters_text else "This is the first chapter."
    prompt = f"You are a novelist. Write the full text for Chapter {chapter_index + 1}: {project['chapters'][chapter_index]['title']}. The chapter should be approximately {words_per_chapter:.0f} words long. Write in {language}. Context: {context_summary}. Overall Synopsis: {project['synopsis']}. Writing Style: {project['writing_style']}"
    try:
        response = openai.ChatCompletion.create(model="gpt-4-turbo", messages=[{"role": "user", "content": prompt}])
        project['chapters'][chapter_index]['text'] = response.choices[0].message['content']
        project['chapters'][chapter_index]['status'] = 'Generated'
        save_project(project)
    except Exception as e: print(f"Error generating chapter: {e}")
    return redirect(url_for('.writing_room', project_id=project_id, chapter_index=chapter_index))

@fiction_bp.route('/<project_id>/save_chapter/<int:chapter_index>', methods=['POST'])
def save_chapter(project_id, chapter_index):
    project = load_project(project_id)
    if not project or chapter_index >= len(project['chapters']): abort(404)
    project['chapters'][chapter_index]['text'] = request.form.get('chapter_text')
    project['chapters'][chapter_index]['status'] = 'Approved'
    save_project(project)
    generate_images_for_chapter(project, chapter_index)
    next_chapter_index = chapter_index + 1
    if next_chapter_index >= len(project['chapters']):
        return redirect(url_for('.finalize', project_id=project_id))
    return redirect(url_for('.writing_room', project_id=project_id, chapter_index=next_chapter_index))

@fiction_bp.route('/<project_id>/auto_approve_all', methods=['POST'])
def auto_approve_all(project_id):
    project = load_project(project_id)
    if not project: abort(404)
    language = project.get('language', 'English')
    num_chapters = len(project['chapters'])
    words_per_chapter = int(project.get('word_count', 20000)) / num_chapters if num_chapters > 0 else 2000
    for i, chapter in enumerate(project['chapters']):
        if chapter['status'] != 'Approved':
            print(f"Auto-generating chapter {i+1}...")
            previous_chapters_text = "\\n\\n".join([ch['text'] for idx, ch in enumerate(project['chapters']) if idx < i and ch['status'] == 'Approved'])
            context_summary = f"Summary of previous chapters:\\n{previous_chapters_text[:5000]}..." if previous_chapters_text else "This is the first chapter."
            prompt = f"You are a novelist. Write the full text for Chapter {i + 1}: {chapter['title']}. Write in {language}. The chapter should be approximately {words_per_chapter:.0f} words long. Context: {context_summary}."
            try:
                response = openai.ChatCompletion.create(model="gpt-4-turbo", messages=[{"role": "user", "content": prompt}])
                project['chapters'][i]['text'] = response.choices[0].message['content']
                project['chapters'][i]['status'] = 'Approved'
                save_project(project)
                print(f"Auto-generating images for chapter {i+1}...")
                generate_images_for_chapter(project, i)
            except Exception as e:
                print(f"Error auto-generating chapter {i+1} text: {e}")
                continue
    last_chapter_index = len(project['chapters']) - 1
    return redirect(url_for('.writing_room', project_id=project_id, chapter_index=last_chapter_index))

@fiction_bp.route('/<project_id>/finalize')
def finalize(project_id):
    project = load_project(project_id)
    if not project: abort(404)
    return render_template('finalize.html', project=project)

@fiction_bp.route('/<project_id>/build_package', methods=['POST'])
def build_package(project_id):
    project = load_project(project_id)
    if not project: abort(404)
    settings = request.form.to_dict()
    project['final_settings'] = settings
    save_project(project)

    # Generate PDFs
    book_html = render_template('book_template.html', project=project, settings=settings)
    cover_html = render_template('cover_template.html', project=project, settings=settings)

    # ... more complex PDF generation logic with bleed and dynamic size would go here ...
    book_pdf = HTML(string=book_html).write_pdf()
    cover_pdf = HTML(string=cover_html).write_pdf()

    # Generate Metadata
    metadata_text = generate_kdp_metadata(project)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(f'{project["title"]}_manuscript.pdf', book_pdf)
        zip_file.writestr(f'{project["title"]}_cover.pdf', cover_pdf)
        zip_file.writestr('kdp_metadata.txt', metadata_text)

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name=f'book_package_{project["title"]}.zip', mimetype='application/zip')
