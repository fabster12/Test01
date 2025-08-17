from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, jsonify
from ai_booksmith.config_manager import get_config, get_model_config
from ai_booksmith.llm_provider import get_llm_client
from ai_booksmith.image_gen_provider import get_image_gen_client
from ai_booksmith.mock_provider import mock_openai_chat_completion, mock_leonardo_image_generation
import os
import uuid
import json
import requests
from ... import book_generator

low_content_bp = Blueprint('low_content', __name__,
                           template_folder='templates/low_content',
                           static_folder='static',
                           url_prefix='/low_content')

# In-memory storage for generated content
generated_coloring_books = {}

def _extract_list_from_json(response_data):
    """Extracts the first list found in a dictionary from a JSON response."""
    if isinstance(response_data, list):
        return response_data
    if isinstance(response_data, dict):
        for key, value in response_data.items():
            if isinstance(value, list):
                return value
    return []

def _get_model_id(provider):
    """Gets the model ID for a given provider, with case-insensitive name matching."""
    config = get_config()
    model_config = get_model_config()
    active_model_name_key = f'active_{provider}_model'
    active_model_name = config.get(active_model_name_key, '').lower()

    if not active_model_name:
        return None

    model_list = model_config.get(provider, [])
    model_id = next((m['id'] for m in model_list if m['name'].lower() == active_model_name), None)

    print(f"DEBUG: Active {provider.capitalize()} Model Name: {config.get(active_model_name_key)}")
    print(f"DEBUG: Found {provider.capitalize()} Model ID: {model_id}")
    if not model_id:
        print(f"ERROR: Could not find a matching model ID for name '{config.get(active_model_name_key)}' in models.yaml")

    return model_id

@low_content_bp.route('/coloring_book', methods=['GET'])
def coloring_book_home():
    """Displays the new idea brainstorming form."""
    return render_template('idea_form.html')

@low_content_bp.route('/brainstorm_themes', methods=['POST'])
def brainstorm_themes():
    """Handles brainstorming requests from the idea form."""
    data = request.get_json()
    topic = data.get('topic', '')
    llm_client = get_llm_client()
    config = get_config()

    if topic:
        prompt = f"Brainstorm 5 specific, marketable coloring book themes based on the broad topic of '{topic}'. Return as a JSON object with a 'suggestions' key, which is a list of strings."
    else:
        prompt = "Brainstorm 5 interesting and unique themes for a children's coloring book from scratch. Return as a JSON object with a 'suggestions' key, which is a list of strings."

    openai_model_id = _get_model_id('openai')

    try:
        if config['provider'] == 'mock':
            response = mock_openai_chat_completion(model=None, messages=[{"role": "user", "content": prompt}])
        else:
            response = llm_client.chat.completions.create(
                model=openai_model_id,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
        response_data = json.loads(response.choices[0].message.content)
        suggestions = _extract_list_from_json(response_data)
        return jsonify({"suggestions": suggestions})
    except Exception as e:
        current_app.logger.error(f"Error brainstorming themes: {e}")
        return jsonify({"error": "Failed to brainstorm themes."}), 500

@low_content_bp.route('/start_generation', methods=['POST'])
def start_generation():
    config = get_config()
    session['book_title'] = request.form.get('book_title')
    session['book_theme'] = request.form.get('book_theme')
    session['num_pages'] = int(request.form.get('num_pages', 20))
    session['book_type'] = 'coloring_book'
    session['session_id'] = str(uuid.uuid4())

    session_dir = os.path.join(config['generated_books_dir'], session['session_id'])
    os.makedirs(session_dir, exist_ok=True)
    session['session_dir'] = session_dir

    # Clear any previous book data for this session
    session['generated_subjects'] = []

    return redirect(url_for('low_content.preview_pages'))

@low_content_bp.route('/preview')
def preview_pages():
    if 'session_id' not in session:
        return redirect(url_for('low_content.coloring_book_home'))

    return render_template('preview.html',
                           book_title=session.get('book_title'),
                           book_theme=session.get('book_theme'),
                           session_id=session.get('session_id'))

@low_content_bp.route('/api/generate_preview_task')
def generate_preview_task():
    if 'session_id' not in session:
        return jsonify({"status": "error", "message": "Session not found."}), 400

    image_paths, subjects = _generate_coloring_pages(num_pages=4)
    session['generated_subjects'] = subjects

    generated_coloring_books[session['session_id']] = {
        'image_paths': image_paths,
        'subjects': subjects,
        'title': session.get('book_title')
    }

    relative_paths = [os.path.relpath(p, current_app.static_folder) for p in image_paths]
    return jsonify({"status": "success", "image_paths": relative_paths})

@low_content_bp.route('/generate_full_book_task', methods=['POST'])
def generate_full_book_task():
    if 'session_id' not in session:
        return redirect(url_for('low_content.coloring_book_home'))

    num_remaining_pages = session.get('num_pages', 20) - 4
    if num_remaining_pages > 0:
        new_image_paths, all_subjects = _generate_coloring_pages(num_pages=num_remaining_pages)

        # Append new data to the existing book data
        book_data = generated_coloring_books[session['session_id']]
        book_data['image_paths'].extend(new_image_paths)
        book_data['subjects'] = all_subjects
        session['generated_subjects'] = all_subjects

    return redirect(url_for('low_content.build_coloring_book'))


def _generate_coloring_pages(num_pages):
    config = get_config()
    llm_client = get_llm_client()
    image_gen_client = get_image_gen_client()

    book_theme = session.get('book_theme')
    existing_subjects = session.get('generated_subjects', [])

    prompt = f"Brainstorm a list of {num_pages} unique and simple subjects for a children's coloring book with the theme '{book_theme}'. The subjects should be single objects or characters. Do not include any of the following subjects: {', '.join(existing_subjects)}. Return the list as a JSON object with a 'subjects' key, which is an array of strings."

    openai_model_id = _get_model_id('openai')

    try:
        if config['provider'] == 'mock':
            response = mock_openai_chat_completion(model=None, messages=[{"role": "user", "content": prompt}])
        else:
            response = llm_client.chat.completions.create(
                model=openai_model_id,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
        response_data = json.loads(response.choices[0].message.content)
        new_subjects = _extract_list_from_json(response_data)
    except Exception as e:
        current_app.logger.error(f"Error brainstorming subjects: {e}")
        return [], existing_subjects

    image_paths = []
    leonardo_model_id = _get_model_id('leonardo')

    for subject in new_subjects:
        try:
            if config['provider'] == 'mock':
                image_url = mock_leonardo_image_generation(prompt=None)['generations_by_pk']['generated_images'][0]['url']
            else:
                image_prompt = f"A simple, clean line art coloring book page for children featuring a {subject}. The lines should be thick and clear, on a pure white background."
                generation_id = image_gen_client.generate(image_prompt, model_id=leonardo_model_id)
                image_url = image_gen_client.poll_for_image(generation_id)

            if image_url:
                if config['provider'] == 'mock':
                    image_paths.append(image_url)
                else:
                    image_data = requests.get(image_url).content
                    static_session_dir = os.path.join(current_app.static_folder, session['session_id'])
                    os.makedirs(static_session_dir, exist_ok=True)
                    image_path = os.path.join(static_session_dir, f"{subject.replace(' ', '_').lower()}.png")

                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    image_paths.append(image_path)
        except Exception as e:
            current_app.logger.error(f"Error generating image for subject '{subject}': {e}")

    return image_paths, existing_subjects + new_subjects

@low_content_bp.route('/build_coloring_book')
def build_coloring_book():
    if 'session_id' not in session or session['session_id'] not in generated_coloring_books:
        return redirect(url_for('low_content.coloring_book_home'))

    session_id = session['session_id']
    book_data = generated_coloring_books[session_id]

    pdf_path = book_generator.create_coloring_book_pdf(
        title=book_data['title'],
        image_paths=book_data['image_paths'],
        subjects=book_data['subjects'],
        output_dir=session.get('session_dir')
    )

    return render_template('build_coloring_book.html',
                           pdf_path=os.path.basename(pdf_path),
                           session_id=session_id)
