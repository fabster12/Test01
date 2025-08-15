import os
import json
import yaml
from flask import Flask, render_template, request, redirect, url_for, session
from openai import OpenAI

# Import blueprints and mock provider
from books.fiction.routes import fiction_bp
from books.low_content.routes import low_content_bp
from books.mock_provider import mock_openai_chat_completion

def load_config():
    """Loads the YAML configuration file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if not os.path.exists(config_path):
        print("WARNING: config.yaml not found. Using mock provider by default.")
        return {"provider": "mock", "openai": {"api_key": "mock"}, "leonardo": {"api_key": "mock"}, "flask": {"secret_key": "mock-secret"}}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_app(config):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = config.get('flask', {}).get('secret_key', 'a-strong-default-secret-key')

    app.config['APP_CONFIG'] = config

    client = OpenAI(api_key=config.get('openai', {}).get('api_key'))
    app.openai_client = client

    projects_dir = os.path.join(os.path.dirname(__file__), 'projects')
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)

    app.register_blueprint(fiction_bp)
    app.register_blueprint(low_content_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/brainstorm/<book_type>')
    def brainstorm(book_type):
        return render_template('brainstorm.html', book_type=book_type)

    @app.route('/generate_themes/<book_type>', methods=['POST'])
    def generate_themes(book_type):
        topic = request.form.get('topic')
        is_niche = request.form.get('find_niche') == 'true'
        niche_instruction = "focus on profitable, low-competition niches. " if is_niche else ""
        prompt = f"You are a KDP expert. For a '{book_type}' book about '{topic}', brainstorm 5 themes. {niche_instruction}For each, provide a 'title', 'description', and 'reasoning'. Return JSON with a key 'themes'."

        try:
            if config['provider'] == 'mock':
                response = mock_openai_chat_completion(model=None, messages=[{"role":"user", "content":prompt}])
            else:
                response = app.openai_client.chat.completions.create(
                    model="gpt-4-turbo",
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
        """Handles theme selection and redirects to the correct blueprint."""
        book_type = request.form.get('book_type')
        theme_index = int(request.form.get('selected_theme_index', 0))

        themes = session.get('brainstorm_results', [])

        if theme_index >= len(themes):
            return "Error: Invalid theme selected.", 400

        session['selected_theme'] = themes[theme_index]

        if book_type == 'fiction':
            return redirect(url_for('fiction.new_project_form'))
        elif book_type == 'low_content':
            return redirect(url_for('low_content.new_coloring_book_form'))
        else:
            return redirect(url_for('index'))

    return app

if __name__ == '__main__':
    config = load_config()
    app = create_app(config)
    app.run(debug=True, host='0.0.0.0', port=5003)
