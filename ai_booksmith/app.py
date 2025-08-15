import os
from flask import Flask, render_template, request, redirect, url_for, session
import openai
import json

# Import blueprints
from books.fiction.routes import fiction_bp
from books.low_content.routes import low_content_bp

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "a-strong-default-secret-key")
    openai.api_key = os.getenv("OPENAI_API_KEY", "user-provided-key")

    # Create the projects directory if it doesn't exist
    projects_dir = os.path.join(os.path.dirname(__file__), 'projects')
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)

    # Register blueprints
    app.register_blueprint(fiction_bp)
    app.register_blueprint(low_content_bp)

    @app.route('/')
    def index():
        """Render the main landing page."""
        return render_template('index.html')

    @app.route('/brainstorm/<book_type>')
    def brainstorm(book_type):
        """Renders the brainstorming page."""
        return render_template('brainstorm.html', book_type=book_type)

    @app.route('/generate_themes/<book_type>', methods=['POST'])
    def generate_themes(book_type):
        """Generates niche themes based on a topic."""
        topic = request.form.get('topic')
        is_niche = request.form.get('find_niche') == 'true'

        niche_instruction = "focus on finding profitable, low-competition niche ideas. " if is_niche else ""

        prompt = f"""
        You are a KDP market research expert. A user wants to create a '{book_type}' book about '{topic}'.
        Your task is to brainstorm 5 specific, creative themes.
        {niche_instruction}
        For each theme, provide a 'title', a short 'description', and a 'reason' explaining why it's a good niche.
        Return as a valid JSON object with a single key "themes".
        """
        try:
            response = openai.ChatCompletion.create(model="gpt-4-turbo", messages=[{"role": "system", "content": "You only respond in JSON."}, {"role": "user", "content": prompt}])
            themes = json.loads(response.choices[0].message['content']).get('themes', [])
        except Exception as e:
            print(f"Error generating themes: {e}")
            themes = [] # Handle error gracefully

        session['brainstorm_results'] = themes
        return render_template('themes.html', themes=themes, book_type=book_type)

    @app.route('/select_theme', methods=['POST'])
    def select_theme():
        """Redirects to the correct creation form after a theme is selected."""
        book_type = request.form.get('book_type')
        # Store the selected theme details to pre-fill the next form
        session['selected_theme'] = {
            "title": request.form.get('selected_theme_title'),
            "description": request.form.get('selected_theme_description')
        }

        if book_type == 'fiction':
            return redirect(url_for('fiction.new_project_form'))
        elif book_type == 'low_content':
            return redirect(url_for('low_content.new_coloring_book_form'))
        else:
            return redirect(url_for('index'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5003)
