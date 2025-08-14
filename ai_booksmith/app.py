import os
import json
import uuid
import re
import io
import zipfile
import openai
from flask import Flask, render_template, request, redirect, url_for, session, abort, send_file
from weasyprint import HTML, CSS

# --- Graceful SDK Import ---
try:
    from leonardo_api import Leonardo
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY", "user-provided-key")
    leonardo = Leonardo(auth_token=LEONARDO_API_KEY)
    LEONARDO_ENABLED = LEONARDO_API_KEY != "user-provided-key"
except ImportError:
    print("WARNING: Leonardo SDK not found. Image generation will be disabled.")
    LEONARDO_ENABLED = False

# --- Configuration ---
openai.api_key = os.getenv("OPENAI_API_KEY", "user-provided-key")
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "a-strong-default-secret-key")
PROJECTS_DIR = os.path.join(os.path.dirname(__file__), 'projects')
if not os.path.exists(PROJECTS_DIR):
    os.makedirs(PROJECTS_DIR)

# --- Helper Functions ---
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
    chapter_text = project['chapters'][chapter_index]['text']
    art_style = project['art_style']
    scene_prompt = f"""Read the following book chapter. Identify 3 distinct, visually interesting, and important scenes to illustrate. For each scene, provide a detailed, one-sentence description suitable as a prompt for an AI image generator. Return the output as a valid JSON object with a single key "scenes", which is a list of strings.
    Chapter Text: --- {chapter_text[:4000]} --- """
    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": scene_prompt}])
        scenes = json.loads(response.choices[0].message['content']).get('scenes', [])
    except Exception as e:
        print(f"Error generating image prompts: {e}")
        return
    generated_images = []
    for scene_desc in scenes:
        try:
            image_prompt = f"{scene_desc}, in the style of {art_style}"
            if LEONARDO_ENABLED:
                generation_response = leonardo.create_generation(prompt=image_prompt, model_id="6bef9f1b-29cb-40c7-b9df-32b51c1f67d3", num_images=1, width=512, height=512, guidance_scale=7)
                image_url = generation_response.get_images()[0].get_url() if generation_response.get_images() else None
                if image_url: generated_images.append({"prompt": scene_desc, "url": image_url})
                else: raise Exception("API returned no image.")
            else:
                print("Leonardo SDK not enabled. Using placeholder images.")
                image_url = f"https://placehold.co/512x512?text=Image+Gen+Disabled\\n{scene_desc[:20]}..."
                generated_images.append({"prompt": scene_desc, "url": image_url})
        except Exception as e:
            print(f"Error generating image: {e}")
            generated_images.append({"prompt": scene_desc, "url": f"https://placehold.co/512x512?text=API+Error"})
    project['chapters'][chapter_index]['images'] = generated_images
    save_project(project)

def generate_kdp_metadata(project):
    language = project.get('language', 'English')
    prompt = f"You are a book marketing expert. For a book with title '{project['title']}' and description '{project['logline']}', generate KDP metadata. Provide a JSON object with keys: 'keywords' (a list of 7 strings) and 'categories' (a list of 2 strings). Provide the keywords in {language}."
    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": prompt}])
        metadata = json.loads(response.choices[0].message['content'])
        return f"Keywords:\n- " + "\n- ".join(metadata.get('keywords', [])) + "\n\nCategories:\n- " + "\n- ".join(metadata.get('categories', []))
    except Exception as e:
        return f"Error generating metadata: {e}"

# --- Routes ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/new/<book_type>')
def new_project(book_type):
    if book_type != 'fiction': return "This book type is not yet supported.", 404
    return render_template('idea_form.html', book_type=book_type)

@app.route('/generate_ideas/<book_type>', methods=['POST'])
def generate_ideas(book_type):
    language = request.form.get('language')
    genre = request.form.get('genre')
    description = request.form.get('description')
    if not all([language, genre, description]): return redirect(url_for('new_project', book_type=book_type))
    if openai.api_key == "user-provided-key": return "ERROR: OpenAI API key is not set."
    prompt = f'You are a creative assistant. Based on Genre: "{genre}" and Description: "{description}", generate 10 book ideas. For each, provide: "title", "logline", "writing_style", "art_style". Return as JSON with a key "ideas". Write all text content in {language}.'
    try:
        response = openai.ChatCompletion.create(model="gpt-4-turbo", messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": prompt}])
        ideas = json.loads(response.choices[0].message['content']).get('ideas', [])
    except Exception as e: return f"An error occurred: {e}"
    if not ideas: return "Error: Could not generate ideas."
    session['ideas'] = ideas
    session['project_context'] = {'book_type': book_type, 'language': language, 'genre': genre, 'description': description}
    return render_template('ideas.html', ideas=ideas)

@app.route('/select_idea', methods=['POST'])
def select_idea():
    selected_index = int(request.form.get('selected_idea_index'))
    ideas, context = session.get('ideas'), session.get('project_context', {})
    if not ideas or selected_index >= len(ideas): return redirect(url_for('index'))
    selected_idea = ideas[selected_index]
    project_id = str(uuid.uuid4())
    project_data = {
        "id": project_id, "book_type": context.get('book_type'), "language": context.get('language'),
        "genre": context.get('genre'), "description": context.get('description'), "title": selected_idea.get('title'),
        "logline": selected_idea.get('logline'), "writing_style": selected_idea.get('writing_style'),
        "art_style": selected_idea.get('art_style'), "synopsis": "", "back_cover_blurb": "", "chapters": []
    }
    save_project(project_data)
    return redirect(url_for('blueprint', project_id=project_id))

@app.route('/blueprint/<project_id>')
def blueprint(project_id):
    project = load_project(project_id)
    if not project: abort(404)
    return render_template('blueprint.html', project=project)

@app.route('/generate_blueprint/<project_id>', methods=['POST'])
def generate_blueprint(project_id):
    project = load_project(project_id)
    if not project: abort(404)
    language = project.get('language', 'English')
    prompt = f"You are a master storyteller. Based on the book concept (Title: {project['title']}), generate a detailed, multi-chapter synopsis and a compelling back cover blurb. Return as JSON with keys 'synopsis' and 'back_cover_blurb'. Write all text content in {language}."
    try:
        response = openai.ChatCompletion.create(model="gpt-4-turbo", messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": prompt}])
        data = json.loads(response.choices[0].message['content'])
        project['synopsis'], project['back_cover_blurb'] = data.get('synopsis', 'Error.'), data.get('back_cover_blurb', 'Error.')
    except Exception as e:
        project['synopsis'], project['back_cover_blurb'] = f"An error occurred: {e}", f"An error occurred: {e}"
    save_project(project)
    return redirect(url_for('blueprint', project_id=project_id))

@app.route('/writing_room/<project_id>')
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

@app.route('/generate_chapter/<project_id>/<int:chapter_index>', methods=['POST'])
def generate_chapter(project_id, chapter_index):
    project = load_project(project_id)
    if not project or chapter_index >= len(project['chapters']): abort(404)
    language = project.get('language', 'English')
    previous_chapters_text = "\\n\\n".join([ch['text'] for i, ch in enumerate(project['chapters']) if i < chapter_index and ch['status'] == 'Approved'])
    context_summary = f"Summary of previous chapters:\\n{previous_chapters_text[:5000]}..." if previous_chapters_text else "This is the first chapter."
    prompt = f"You are a novelist. Write the full text for Chapter {chapter_index + 1}: {project['chapters'][chapter_index]['title']}. Write in {language}. Context: {context_summary}. Overall Synopsis: {project['synopsis']}. Writing Style: {project['writing_style']}"
    try:
        response = openai.ChatCompletion.create(model="gpt-4-turbo", messages=[{"role": "user", "content": prompt}])
        project['chapters'][chapter_index]['text'] = response.choices[0].message['content']
        project['chapters'][chapter_index]['status'] = 'Generated'
        save_project(project)
    except Exception as e: print(f"Error generating chapter: {e}")
    return redirect(url_for('writing_room', project_id=project_id, chapter_index=chapter_index))

@app.route('/save_chapter/<project_id>/<int:chapter_index>', methods=['POST'])
def save_chapter(project_id, chapter_index):
    project = load_project(project_id)
    if not project or chapter_index >= len(project['chapters']): abort(404)
    project['chapters'][chapter_index]['text'] = request.form.get('chapter_text')
    project['chapters'][chapter_index]['status'] = 'Approved'
    save_project(project)
    generate_images_for_chapter(project, chapter_index)
    next_chapter_index = chapter_index + 1
    if next_chapter_index >= len(project['chapters']):
        return redirect(url_for('finalize', project_id=project_id))
    return redirect(url_for('writing_room', project_id=project_id, chapter_index=next_chapter_index))

@app.route('/auto_approve_all/<project_id>', methods=['POST'])
def auto_approve_all(project_id):
    project = load_project(project_id)
    if not project: abort(404)
    language = project.get('language', 'English')
    for i, chapter in enumerate(project['chapters']):
        if chapter['status'] != 'Approved':
            print(f"Auto-generating chapter {i+1}...")
            previous_chapters_text = "\\n\\n".join([ch['text'] for idx, ch in enumerate(project['chapters']) if idx < i and ch['status'] == 'Approved'])
            context_summary = f"Summary of previous chapters:\\n{previous_chapters_text[:5000]}..." if previous_chapters_text else "This is the first chapter."
            prompt = f"You are a novelist. Write the full text for Chapter {i + 1}: {chapter['title']}. Write in {language}. Context: {context_summary}."
            try:
                response = openai.ChatCompletion.create(model="gpt-4-turbo", messages=[{"role": "user", "content": prompt}])
                project['chapters'][i]['text'] = response.choices[0].message['content']
                project['chapters'][i]['status'] = 'Approved'
                save_project(project) # Save after each chapter text generation
                print(f"Auto-generating images for chapter {i+1}...")
                generate_images_for_chapter(project, i) # This function saves the project again
            except Exception as e:
                print(f"Error auto-generating chapter {i+1} text: {e}")
                continue
    last_chapter_index = len(project['chapters']) - 1
    return redirect(url_for('writing_room', project_id=project_id, chapter_index=last_chapter_index))

@app.route('/finalize/<project_id>')
def finalize(project_id):
    project = load_project(project_id)
    if not project: abort(404)
    return render_template('finalize.html', project=project)

@app.route('/build_package/<project_id>', methods=['POST'])
def build_package(project_id):
    project = load_project(project_id)
    if not project: abort(404)
    book_html = render_template('book_template.html', project=project)
    book_pdf = HTML(string=book_html).write_pdf()
    cover_html = render_template('cover_template.html', project=project)
    cover_pdf = HTML(string=cover_html).write_pdf()
    metadata_text = generate_kdp_metadata(project)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('manuscript.pdf', book_pdf)
        zip_file.writestr('cover.pdf', cover_pdf)
        zip_file.writestr('kdp_metadata.txt', metadata_text)
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name=f'book_package_{project["title"]}.zip', mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
