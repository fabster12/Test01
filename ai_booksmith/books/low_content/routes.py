from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, jsonify
from ai_booksmith.config_manager import get_config, get_model_config, get_available_models
from ai_booksmith.llm_provider import get_llm_client
from ai_booksmith.image_gen_provider import get_image_gen_client
import os
import uuid
import json
import requests
from ...book_generator import create_coloring_book_pdf

low_content_bp = Blueprint('low_content', __name__,
                           template_folder='templates',
                           static_folder='static',
                           url_prefix='/low_content')

# In-memory storage for generated content (for simplicity)
# In a real app, you'd use a database or file-based storage.
generated_coloring_books = {}


@low_content_bp.route('/coloring_book', methods=['GET', 'POST'])
def coloring_book_generator():
    config = get_config()
    if request.method == 'POST':
        session['book_title'] = request.form.get('book_title')
        session['book_theme'] = request.form.get('book_theme')
        session['num_pages'] = int(request.form.get('num_pages', 10))
        session['book_type'] = 'coloring_book'
        session['session_id'] = str(uuid.uuid4())

        # Create a directory for the session
        session_dir = os.path.join(config['generated_books_dir'], session['session_id'])
        os.makedirs(session_dir, exist_ok=True)
        session['session_dir'] = session_dir

        return redirect(url_for('low_content.generate_coloring_pages'))

    return render_template('low_content/coloring_book_generator.html',
                           openai_models=get_available_models('openai'),
                           leonardo_models=get_available_models('leonardo'))


@low_content_bp.route('/generate_coloring_pages')
def generate_coloring_pages():
    if 'session_id' not in session:
        return redirect(url_for('low_content.coloring_book_generator'))

    book_title = session.get('book_title', 'My Coloring Book')
    book_theme = session.get('book_theme', 'Animals')
    num_pages = session.get('num_pages', 10)

    return render_template('low_content/generate_coloring_pages.html',
                           book_title=book_title,
                           book_theme=book_theme,
                           num_pages=num_pages,
                           session_id=session['session_id'])


@low_content_bp.route('/api/generate_coloring_pages_task')
def generate_coloring_pages_task():
    if 'session_id' not in session:
        return jsonify({"status": "error", "message": "Session not found."}), 400

    config = get_config()
    model_config = get_model_config()
    llm_client = get_llm_client()
    image_gen_client = get_image_gen_client()

    book_theme = session.get('book_theme')
    num_pages = session.get('num_pages')
    session_dir = session.get('session_dir')

    active_openai_model_name = config.get('active_openai_model')
    active_leonardo_model_name = config.get('active_leonardo_model')

    openai_model_id = next((m['id'] for m in model_config['openai'] if m['name'] == active_openai_model_name), None)
    leonardo_model_id = next((m['id'] for m in model_config['leonardo'] if m['name'] == active_leonardo_model_name), None)

    if not openai_model_id or not leonardo_model_id:
        return jsonify({"status": "error", "message": "Active model not found in models.yaml"}), 500

    # Step 1: Brainstorm subjects for the coloring book pages
    prompt = f"Brainstorm a list of {num_pages} unique and simple subjects for a children's coloring book with the theme '{book_theme}'. The subjects should be single objects or characters. Return the list as a JSON array of strings."

    try:
        response = llm_client.chat.completions.create(
            model=openai_model_id,
            messages=[
                {"role": "system", "content": "You are a creative assistant that only outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        subjects = json.loads(response.choices[0].message.content)
    except Exception as e:
        current_app.logger.error(f"Error brainstorming subjects: {e}")
        return jsonify({"status": "error", "message": "Error brainstorming subjects."}), 500

    # Step 2: Generate an image for each subject
    image_paths = []
    for subject in subjects:
        try:
            image_prompt = f"A simple, clean line art coloring book page for children featuring a {subject}. The lines should be thick and clear, on a pure white background."
            generation_id = image_gen_client.generate(image_prompt, model_id=leonardo_model_id)
            image_url = image_gen_client.poll_for_image(generation_id)

            if image_url:
                image_data = requests.get(image_url).content
                image_path = os.path.join(session_dir, f"{subject.replace(' ', '_').lower()}.png")
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                image_paths.append(image_path)
        except Exception as e:
            current_app.logger.error(f"Error generating image for subject '{subject}': {e}")
            # Continue to next subject

    generated_coloring_books[session['session_id']] = {
        'image_paths': image_paths,
        'title': session.get('book_title')
    }
    return jsonify({"status": "success", "image_paths": image_paths})


@low_content_bp.route('/build_coloring_book')
def build_coloring_book():
    if 'session_id' not in session or session['session_id'] not in generated_coloring_books:
        return redirect(url_for('low_content.coloring_book_generator'))

    session_id = session['session_id']
    book_data = generated_coloring_books[session_id]
    session_dir = session.get('session_dir')

    pdf_path = create_coloring_book_pdf(
        title=book_data['title'],
        image_paths=book_data['image_paths'],
        output_dir=session_dir
    )

    return render_template('low_content/build_coloring_book.html',
                           pdf_path=os.path.basename(pdf_path),
                           session_id=session_id)
