from flask import Flask, render_template, g, current_app
from .books.fiction.routes import fiction_bp
from .books.low_content.routes import low_content_bp
from .config_manager import load_config, get_config, get_model_config
from .llm_provider import init_llm_client
from .image_gen_provider import init_image_gen_client
import os

def create_app():
    app = Flask(__name__)

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

    @app.route('/system')
    def system_info():
        config = get_config()
        model_config = get_model_config()
        return render_template('system.html', config=config, model_config=model_config)

    return app
