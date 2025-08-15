import os
import io
import time
import json
import requests
import pypandoc
from flask import Blueprint, render_template, request, send_file, session, current_app
from ..mock_provider import mock_openai_chat_completion, mock_leonardo_image_generation

low_content_bp = Blueprint('low_content', __name__, template_folder='templates', url_prefix='/low-content')

def get_active_model_details(config, provider_key, active_model_key):
    models_config = config.get('models', {})
    active_model_name = config.get(active_model_key)
    return models_config.get(provider_key, {}).get(active_model_name, {})

@low_content_bp.route('/new')
def new_coloring_book_form():
    theme_data = session.get('selected_theme', {})
    return render_template('coloring_book_form.html', theme_data=theme_data)

@low_content_bp.route('/generate', methods=['POST'])
def generate_coloring_book():
    config = current_app.config['APP_CONFIG']
    client = current_app.openai_client
    theme = request.form.get('theme')
    pages = int(request.form.get('pages', 10))

    subject_prompt = f"You are a creative assistant. For a coloring book with the theme '{theme}', brainstorm a list of {pages} unique subjects. Return as a JSON object with a single key 'subjects'."
    try:
        if config['provider'] == 'mock':
            response = mock_openai_chat_completion(model=None, messages=[{"role":"user", "content":subject_prompt}])
        else:
            active_model = get_active_model_details(config, 'openai_models', 'active_openai_model')
            response = client.chat.completions.create(model=active_model.get('name'), messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": subject_prompt}], response_format={"type": "json_object"})
        subjects = json.loads(response.choices[0].message.content).get('subjects', [theme] * pages)
    except Exception as e:
        print(f"Error brainstorming subjects: {e}")
        subjects = [theme] * pages

    image_urls = []
    for subject in subjects:
        try:
            if config['provider'] == 'mock':
                mock_response = mock_leonardo_image_generation(prompt=subject)
                image_urls.append(mock_response['generations_by_pk']['generated_images'][0]['url'])
            else:
                active_leo_model = get_active_model_details(config, 'leonardo_models', 'active_leonardo_model')
                headers = {"authorization": f"Bearer {config['leonardo']['api_key']}"}
                payload = {"prompt": f"coloring book page, clean and simple line art, thick lines, white background, {subject}, in the theme of {theme}", "modelId": active_leo_model.get('id')}
                response = requests.post(f"https://cloud.leonardo.ai/api/rest/v1/generations", json=payload, headers=headers)
                # ... (polling logic)
        except Exception as e:
            print(f"Error generating coloring page: {e}")

    markdown_content = ""
    for url in image_urls:
        markdown_content += f"![Coloring Page]({url})\\n\\n"

    try:
        extra_args = ['-V', 'geometry:paperwidth=8.5in', '-V', 'geometry:paperheight=11in', '-V', 'geometry:margin=0.5in']
        pdf_file = pypandoc.convert_text(markdown_content, 'pdf', format='md', extra_args=extra_args)
    except Exception as e:
        print(f"Error generating PDF with Pandoc: {e}")
        return "Error creating PDF file.", 500

    return send_file(io.BytesIO(pdf_file), as_attachment=True, download_name=f'{theme}_coloring_book.pdf', mimetype='application/pdf')
