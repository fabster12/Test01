from flask import Blueprint, render_template, request
from ...llm_provider import get_llm_client

garden_planner_bp = Blueprint('garden_planner', __name__,
                               template_folder='templates',
                               url_prefix='/garden_planner')

@garden_planner_bp.route('/')
def index():
    return render_template('garden_planner/index.html')

@garden_planner_bp.route('/generate', methods=['POST'])
def generate_planner():
    llm_client = get_llm_client()
    garden_size = request.form.get('garden_size')
    sunlight = request.form.get('sunlight')
    plant_preferences = request.form.get('plant_preferences')

    prompt = f"""
    Create a detailed garden plan for a {garden_size} garden with {sunlight}.
    The user has expressed a preference for the following plants: {plant_preferences}.

    The plan should include:
    - A suggested layout for the garden.
    - A planting schedule for the year.
    - Tips for soil preparation and maintenance.
    - Companion planting suggestions.

    Format the output as a markdown document.
    """

    response = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a master gardener and landscape architect."},
            {"role": "user", "content": prompt}
        ]
    )

    planner_content = response.choices[0].message.content

    return render_template('garden_planner/planner.html', planner_content=planner_content)
