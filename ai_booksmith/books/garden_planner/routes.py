from flask import Blueprint, request, send_file, current_app
import pypandoc
from .planner_content import generate_planner_html_content, generate_cover_image
import io
import os

garden_planner_bp = Blueprint('garden_planner', __name__,
                               template_folder='templates',
                               url_prefix='/garden_planner')

@garden_planner_bp.route('/')
def index():
    # The index route now just needs to render the button
    from flask import render_template
    return render_template('garden_planner/index.html')

@garden_planner_bp.route('/generate', methods=['POST'])
def generate_planner():
    # Generate the planner content and cover image
    planner_html_content = generate_planner_html_content()
    cover_image_url = generate_cover_image()

    # Construct the full HTML for Pandoc
    # We need to embed the cover image and link to the CSS
    # Note: Pandoc needs absolute paths or URLs for resources.
    css_path = os.path.join(current_app.static_folder, 'planner_style.css')

    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>The Urban Pollinator Garden Planner</title>
        <link rel="stylesheet" href="{css_path}">
    </head>
    <body>
        <div class="page cover">
            <img src="{cover_image_url}" alt="Cover Image" style="width:100%; height:100vh; object-fit:cover;">
        </div>
        {planner_html_content}
    </body>
    </html>
    """

    # Create PDF using pypandoc
    try:
        output_pdf = pypandoc.convert_text(
            full_html,
            'pdf',
            format='html',
            extra_args=['--css', css_path, '--metadata', 'title="The Urban Pollinator Garden Planner"']
        )
        pdf_buffer = io.BytesIO(output_pdf)
    except Exception as e:
        print(f"Error generating PDF with Pandoc: {e}")
        # Fallback to sending the HTML if PDF generation fails
        return f"<h1>Error generating PDF</h1><p>{e}</p>", 500

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name='urban_pollinator_garden_planner.pdf',
        mimetype='application/pdf'
    )
