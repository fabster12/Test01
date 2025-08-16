from flask import Blueprint, render_template, request, send_file
from weasyprint import HTML, CSS
from .planner_content import generate_planner_html_content, generate_cover_image
import io

garden_planner_bp = Blueprint('garden_planner', __name__,
                               template_folder='templates',
                               url_prefix='/garden_planner')

@garden_planner_bp.route('/')
def index():
    return render_template('garden_planner/index.html')

@garden_planner_bp.route('/generate', methods=['POST'])
def generate_planner():
    # Generate the planner content and cover image
    planner_content = generate_planner_html_content()
    cover_image_url = generate_cover_image()

    # Render the HTML template for the PDF
    html_out = render_template('garden_planner/planner_render.html',
                               planner_content=planner_content,
                               cover_image_url=cover_image_url)

    # Create PDF
    pdf_buffer = io.BytesIO()
    HTML(string=html_out, base_url=request.base_url).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name='urban_pollinator_garden_planner.pdf',
        mimetype='application/pdf'
    )
