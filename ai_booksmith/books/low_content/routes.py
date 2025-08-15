import os
import io
import time
import json
import requests
import pypandoc
from flask import Blueprint, render_template, request, send_file, session, current_app
from ..mock_provider import mock_openai_chat_completion, mock_leonardo_image_generation

# --- Blueprint Setup ---
low_content_bp = Blueprint('low_content', __name__,
                           template_folder='templates',
                           url_prefix='/low-content')

# --- Routes ---
@low_content_bp.route('/new')
def new_coloring_book_form():
    """Renders the form to create a new coloring book, pre-filled with a theme."""
    theme_data = session.get('selected_theme', {})
    return render_template('coloring_book_form.html', theme_data=theme_data)

@low_content_bp.route('/generate', methods=['POST'])
def generate_coloring_book():
    """Generates and returns a coloring book PDF."""
    config = current_app.config['APP_CONFIG']
    client = current_app.openai_client

    theme = request.form.get('theme')
    pages = int(request.form.get('pages', 10))

    # 1. Brainstorm subjects
    subject_prompt = f"You are a creative assistant. For a coloring book with the theme '{theme}', brainstorm a list of {pages} unique subjects. Return as a JSON object with a single key 'subjects', which is a list of strings."
    try:
        if config['provider'] == 'mock':
            response = mock_openai_chat_completion(model=None, messages=[{"role":"user", "content":subject_prompt}])
        else:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": subject_prompt}],
                response_format={"type": "json_object"}
            )
        subjects = json.loads(response.choices[0].message.content).get('subjects', [theme] * pages)
    except Exception as e:
        print(f"Error brainstorming subjects: {e}")
        subjects = [theme] * pages

    # 2. Generate images
    image_urls = []
    for subject in subjects:
        try:
            if config['provider'] == 'mock':
                mock_response = mock_leonardo_image_generation(prompt=subject)
                image_urls.append(mock_response['generations_by_pk']['generated_images'][0]['url'])
            else:
                # ... (Real Leonardo API call logic)
                pass
        except Exception as e:
            print(f"Error generating coloring page: {e}")

    # 3. Compile images into a PDF using Pandoc
    markdown_content = ""
    for url in image_urls:
        markdown_content += f"![Coloring Page]({url})\n\n"

    try:
        # Using standard 8.5x11 inch paper for coloring books
        extra_args = ['-V', 'geometry:paperwidth=8.5in', '-V', 'geometry:paperheight=11in', '-V', 'geometry:margin=0.5in']
        pdf_file = pypandoc.convert_text(markdown_content, 'pdf', format='md', extra_args=extra_args)
    except Exception as e:
        print(f"Error generating PDF with Pandoc: {e}")
        return "Error creating PDF file.", 500

    # 4. Return the PDF
    return send_file(
        io.BytesIO(pdf_file),
        as_attachment=True,
        download_name=f'{theme}_coloring_book.pdf',
        mimetype='application/pdf'
    )
