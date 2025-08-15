import os
import json
import yaml
import httpx
from flask import Flask, render_template, request, redirect, url_for, session
from openai import OpenAI

from ai_booksmith.books.fiction.routes import fiction_bp
from ai_booksmith.books.low_content.routes import low_content_bp
from ai_booksmith.books.mock_provider import mock_openai_chat_completion

def load_app_config():
    config = {}
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

    config['provider'] = os.getenv('PROVIDER', config.get('provider', 'mock'))
    config.setdefault('openai', {})['api_key'] = os.getenv('OPENAI_API_KEY', config.get('openai', {}).get('api_key'))
    config.setdefault('leonardo', {})['api_key'] = os.getenv('LEONARDO_API_KEY', config.get('leonardo', {}).get('api_key'))
    config.setdefault('flask', {})['secret_key'] = os.getenv('FLASK_SECRET_KEY', config.get('flask', {}).get('secret_key'))
    config['ssl_cert_file'] = os.getenv('SSL_CERT_FILE', config.get('ssl_cert_file'))

    models_path = os.path.join(os.path.dirname(__file__), 'models.yaml')
    if os.path.exists(models_path):
        with open(models_path, 'r') as f:
            config['models'] = yaml.safe_load(f)
    else:
        config['models'] = {}

    return config

def create_app(config):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = config.get('flask', {}).get('secret_key')
    app.config['APP_CONFIG'] = config

    ssl_cert_path = config.get('ssl_cert_file')
    http_client = httpx.Client(verify=ssl_cert_path) if ssl_cert_path else None

    client = OpenAI(api_key=config.get('openai', {}).get('api_key'), http_client=http_client)
    app.openai_client = client

    projects_dir = os.path.join(os.path.dirname(__file__), 'projects')
    if not os.path.exists(projects_dir): os.makedirs(projects_dir)

    app.register_blueprint(fiction_bp)
    app.register_blueprint(low_content_bp)

    @app.route('/')
    def index(): return render_template('index.html')

    @app.route('/brainstorm/<book_type>')
    def brainstorm(book_type): return render_template('brainstorm.html', book_type=book_type)

    @app.route('/generate_themes/<book_type>', methods=['POST'])
    def generate_themes(book_type):
        topic = request.form.get('topic')
        is_niche = request.form.get('find_niche') == 'true'
        niche_instruction = "focus on profitable, low-competition niches. " if is_niche else ""
        prompt = f"You are a KDP expert..."

        try:
            if config['provider'] == 'mock':
                response = mock_openai_chat_completion(model=None, messages=[{"role":"user", "content":prompt}])
            else:
                active_model_key = config.get('active_openai_model', 'gpt-4o-mini')
                model_name = config.get('models', {}).get('openai_models', {}).get(active_model_key, {}).get('name', 'gpt-4o-mini')
                response = app.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
            themes = json.loads(response.choices[0].message.content).get('themes', [])
        except Exception as e:
            print(f"Error generating themes: {e}")
            themes = []

        session['brainstorm_results'] = themes
        return render_template('themes.html', themes=themes, book_type=book_type)

    @app.route('/select_theme', methods=['POST'])
    def select_theme():
        book_type = request.form.get('book_type')
        session['selected_theme'] = json.loads(request.form.get('selected_theme_json'))
        if book_type == 'fiction':
            return redirect(url_for('fiction.new_project_form'))
        elif book_type == 'low_content':
            return redirect(url_for('low_content.new_coloring_book_form'))
        else:
            return redirect(url_for('index'))

    return app
