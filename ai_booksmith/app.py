from flask import Flask, render_template, g, current_app, request
from jinja2 import Markup
import re
from .books.fiction.routes import fiction_bp
from .books.low_content.routes import low_content_bp
from .config_manager import load_config, get_config, get_model_config
from .llm_provider import init_llm_client, get_llm_client
from .image_gen_provider import init_image_gen_client, get_image_gen_client
import os

def mask_key(key):
    """Masks an API key, showing only the first and last 4 characters."""
    if not key or len(key) < 8:
        return "Not Set or Too Short"
    return f"{key[:4]}...{key[-4:]}"

def create_app():
    app = Flask(__name__)

    # Register custom Jinja2 filter
    @app.template_filter('nl2br')
    def nl2br(s):
        return Markup(re.sub(r'\n', '<br>\n', s))

    # Load configuration
    config = load_config()
    app.config['BOOKSMITH_CONFIG'] = config
    app.secret_key = config.get('flask_secret_key', 'a_default_secret_key')

    # Ensure the generated_books directory exists
    generated_books_dir = config.get('generated_books_dir', 'generated_books')
    if not os.path.isabs(generated_books_dir):
        generated_books_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), generated_books_dir)

    if not os.path.exists(generated_books_dir):
        os.makedirs(generated_books_dir)

    # Update the config with the absolute path
    config['generated_books_dir'] = generated_books_dir

    @app.before_request
    def before_request():
        g.config = current_app.config['BOOKSMITH_CONFIG']
        # Initialize API clients and store them in the app context
        init_llm_client()
        init_image_gen_client()

    # Register the blueprints for different book types
    app.register_blueprint(fiction_bp)
    app.register_blueprint(low_content_bp)
    from .books.garden_planner.routes import garden_planner_bp
    app.register_blueprint(garden_planner_bp)

    # Main application routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/system', methods=['GET', 'POST'])
    def system_info():
        config = get_config()
        model_config = get_model_config()
        llm_response = None
        image_url = None

        if request.method == 'POST':
            test_type = request.form.get('test_type')
            prompt = request.form.get('prompt')

            if test_type == 'llm':
                try:
                    llm_client = get_llm_client()
                    response = llm_client.chat.completions.create(
                        model=config.get('active_openai_model'),
                        messages=[{"role": "user", "content": prompt}]
                    )
                    llm_response = response.choices[0].message.content
                except Exception as e:
                    llm_response = f"Error: {e}"

            elif test_type == 'image':
                try:
                    image_gen_client = get_image_gen_client()
                    generation_id = image_gen_client.generate(prompt, model_id=config.get('active_leonardo_model'))
                    image_url = image_gen_client.poll_for_image(generation_id)
                    if not image_url:
                        image_url = "Image generation timed out or failed."
                except Exception as e:
                    # This is not a user-facing variable, so we just print it
                    print(f"Error generating image: {e}")
                    image_url = "An error occurred while generating the image."

        masked_openai_key = mask_key(config.get('openai_api_key'))
        masked_leonardo_key = mask_key(config.get('leonardo_api_key'))

        return render_template('system.html',
                               config=config,
                               model_config=model_config,
                               masked_openai_key=masked_openai_key,
                               masked_leonardo_key=masked_leonardo_key,
                               llm_response=llm_response,
                               image_url=image_url)

    return app
