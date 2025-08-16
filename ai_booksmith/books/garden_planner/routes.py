from flask import Blueprint, render_template, request
from .planner_content import generate_planner_content, generate_cover_image
import markdown

garden_planner_bp = Blueprint('garden_planner', __name__,
                               template_folder='templates',
                               url_prefix='/garden_planner')

@garden_planner_bp.route('/')
def index():
    return render_template('garden_planner/index.html')

@garden_planner_bp.route('/generate', methods=['POST'])
def generate_planner():
    # Generate the planner content and cover image
    planner_markdown = generate_planner_content()
    cover_image_url = generate_cover_image()

    # Convert markdown to HTML
    planner_content_html = markdown.markdown(planner_markdown)

    return render_template('garden_planner/planner.html',
                           planner_content=planner_content_html,
                           cover_image_url=cover_image_url)
