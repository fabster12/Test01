import os
import io
import time
import openai
import requests
from flask import Blueprint, render_template, request, send_file, abort
from weasyprint import HTML

# --- Blueprint Setup ---
low_content_bp = Blueprint('low_content', __name__,
                           template_folder='templates',
                           url_prefix='/low-content')

# --- Config ---
LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY", "user-provided-key")
LEONARDO_API_URL = "https://cloud.leonardo.ai/api/rest/v1"
LEONARDO_ENABLED = LEONARDO_API_KEY != "user-provided-key"

# --- Routes ---
@low_content_bp.route('/new')
def new_coloring_book_form():
    """Renders the form to create a new coloring book."""
    theme = session.get('selected_theme', {})
    return render_template('coloring_book_form.html', theme=theme)

@low_content_bp.route('/generate', methods=['POST'])
def generate_coloring_book():
    """Generates and returns a coloring book PDF."""
    if not LEONARDO_ENABLED:
        return "Leonardo API is not configured. This feature is disabled.", 500

    theme = request.form.get('theme')
    pages = int(request.form.get('pages', 10))

    # 1. Brainstorm subjects for variety
    subject_prompt = f"You are a creative assistant. For a coloring book with the theme '{theme}', brainstorm a list of {pages} unique and specific subjects or scenes. Return as a JSON object with a single key 'subjects', which is a list of strings."
    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": subject_prompt}])
        subjects = json.loads(response.choices[0].message['content']).get('subjects', [theme] * pages)
    except Exception as e:
        print(f"Error brainstorming subjects: {e}")
        subjects = [theme] * pages

    # 2. Generate an image for each subject
    headers = {"accept": "application/json", "content-type": "application/json", "authorization": f"Bearer {LEONARDO_API_KEY}"}
    image_urls = []

    for subject in subjects:
        payload = {
            "prompt": f"coloring book page, clean and simple line art, thick lines, white background, {subject}, in the theme of {theme}",
            "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3", # SD 2.1 is good for this
            "width": 512, "height": 768, "num_images": 1, "guidance_scale": 7,
            "photoReal": False, "alchemy": False # Important for line art
        }
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
                    image_urls.append(get_response.json()['generations_by_pk']['generated_images'][0]['url'])
                    break
            else:
                image_urls.append("https://placehold.co/512x768?text=Timeout")
        except Exception as e:
            print(f"Error generating coloring page: {e}")
            image_urls.append("https://placehold.co/512x768?text=API+Error")

    # 3. Compile images into a PDF
    pdf_html = render_template('coloring_book_template.html', images=image_urls)
    pdf_file = HTML(string=pdf_html).write_pdf()

    # 4. Return the PDF as a download
    return send_file(
        io.BytesIO(pdf_file),
        as_attachment=True,
        download_name=f'{theme}_coloring_book.pdf',
        mimetype='application/pdf'
    )
