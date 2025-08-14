import os
import json
import uuid
import re
import io
import zipfile
import openai
from flask import Flask, render_template, request, redirect, url_for, session, abort, send_file
from weasyprint import HTML, CSS

# --- Configuration ---
openai.api_key = "user-provided-key"
# leonardo_api.api_key = "user-provided-key"

app = Flask(__name__)
app.secret_key = 'super-secret-key-for-session-management'
PROJECTS_DIR = os.path.join(os.path.dirname(__file__), 'projects')
if not os.path.exists(PROJECTS_DIR):
    os.makedirs(PROJECTS_DIR)

# --- Helper Functions ---
def load_project(project_id):
    filepath = os.path.join(PROJECTS_DIR, f"{project_id}.json")
    if not os.path.exists(filepath): return None
    with open(filepath, 'r') as f: return json.load(f)

def save_project(project_data):
    filepath = os.path.join(PROJECTS_DIR, f"{project_data['id']}.json")
    with open(filepath, 'w') as f: json.dump(project_data, f, indent=4)

def parse_chapters_from_synopsis(synopsis):
    chapters = re.findall(r'#+\s*Chapter\s*\d+[:\s]*(.*)', synopsis)
    return [title.strip() for title in chapters]

def generate_images_for_chapter(project, chapter_index):
    # This is a placeholder implementation.
    # In a real app, this would call the Leonardo API.
    chapter_text = project['chapters'][chapter_index]['text']
    art_style = project['art_style']
    scene_prompt = f'Read the chapter text and identify 3 key scenes to illustrate. Return as JSON: {{"scenes": ["scene1", "scene2", "scene3"]}}'

    # Dummy scenes for placeholder
    scenes = [f"Scene 1 from Chapter {chapter_index+1}", f"Scene 2 from Chapter {chapter_index+1}", f"Scene 3 from Chapter {chapter_index+1}"]

    generated_images = []
    for scene_desc in scenes:
        image_prompt = f"{scene_desc}, in the style of {art_style}"
        image_url = f"https://placehold.co/600x400?text=Image\\n{scene_desc[:30]}..."
        generated_images.append({"prompt": scene_desc, "url": image_url})

    project['chapters'][chapter_index]['images'] = generated_images
    save_project(project)

def generate_kdp_metadata(project):
    prompt = f"You are a book marketing expert. For a book with the title '{project['title']}' and description '{project['logline']}', generate KDP metadata. Provide your response as a valid JSON object with two keys: 'keywords' (a list of 7 strings) and 'categories' (a list of 2 strings, following Amazon's category format like 'Fiction > Fantasy > Epic')."
    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": prompt}])
        metadata = json.loads(response.choices[0].message['content'])
        return f"Keywords:\n- " + "\n- ".join(metadata.get('keywords', [])) + "\n\nCategories:\n- " + "\n- ".join(metadata.get('categories', []))
    except Exception as e:
        return f"Error generating metadata: {e}"

# --- Routes ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/generate_ideas', methods=['POST'])
def generate_ideas():
    # ... (same as before)
    return redirect(url_for('index')) # Simplified for brevity

@app.route('/select_idea', methods=['POST'])
def select_idea():
    # ... (same as before)
    return redirect(url_for('blueprint', project_id="dummy")) # Simplified for brevity

@app.route('/blueprint/<project_id>')
def blueprint(project_id):
    # ... (same as before)
    return render_template('blueprint.html', project=load_project(project_id))

@app.route('/generate_blueprint/<project_id>', methods=['POST'])
def generate_blueprint(project_id):
    # ... (same as before)
    return redirect(url_for('blueprint', project_id=project_id))

@app.route('/writing_room/<project_id>')
def writing_room(project_id):
    # ... (same as before)
    return render_template('writing_room.html', project=load_project(project_id), current_chapter=load_project(project_id)['chapters'][0], current_chapter_index=0)

@app.route('/generate_chapter/<project_id>/<int:chapter_index>', methods=['POST'])
def generate_chapter(project_id, chapter_index):
    # ... (same as before)
    return redirect(url_for('writing_room', project_id=project_id, chapter_index=chapter_index))

@app.route('/save_chapter/<project_id>/<int:chapter_index>', methods=['POST'])
def save_chapter(project_id, chapter_index):
    # ... (same as before)
    return redirect(url_for('writing_room', project_id=project_id, chapter_index=chapter_index + 1))

@app.route('/auto_approve_all/<project_id>', methods=['POST'])
def auto_approve_all(project_id):
    # ... (same as before)
    return redirect(url_for('writing_room', project_id=project_id, chapter_index=0))

@app.route('/finalize/<project_id>')
def finalize(project_id):
    project = load_project(project_id)
    if not project: abort(404)
    return render_template('finalize.html', project=project)

@app.route('/build_package/<project_id>', methods=['POST'])
def build_package(project_id):
    project = load_project(project_id)
    if not project: abort(404)

    # 1. Generate PDF manuscript
    book_html = render_template('book_template.html', project=project)
    book_pdf = HTML(string=book_html).write_pdf()

    # 2. Generate PDF cover
    cover_html = render_template('cover_template.html', project=project)
    cover_pdf = HTML(string=cover_html).write_pdf()

    # 3. Generate KDP metadata
    metadata_text = generate_kdp_metadata(project)

    # 4. Create ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('manuscript.pdf', book_pdf)
        zip_file.writestr('cover.pdf', cover_pdf)
        zip_file.writestr('kdp_metadata.txt', metadata_text)

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name=f'book_package_{project["title"]}.zip',
        mimetype='application/zip'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
