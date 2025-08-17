from ...llm_provider import get_llm_client
from ...image_gen_provider import get_image_gen_client
from ...config_manager import get_config, get_model_config

def generate_cover_image():
    """
    Generates a cover image for the garden planner using Leonardo.
    """
    config = get_config()
    model_config = get_model_config()
    image_gen_client = get_image_gen_client()
    prompt = "A beautiful watercolor illustration of a lush urban balcony garden teeming with bees, butterflies, and hummingbirds visiting colorful flowers. The style should be soft and inviting, suitable for a book cover. The title 'The Urban Pollinator Garden Planner' should be integrated gracefully into the design."

    active_leonardo_model_name = config.get('active_leonardo_model')
    leonardo_model_id = next((m['id'] for m in model_config.get('leonardo', []) if m['name'] == active_leonardo_model_name), None)

    try:
        generation_id = image_gen_client.generate(prompt, model_id=leonardo_model_id)
        image_url = image_gen_client.poll_for_image(generation_id)
        return image_url
    except Exception as e:
        print(f"Error generating cover image: {e}")
        return None

def generate_introduction():
    """Generates the introduction section as an HTML string."""
    config = get_config()
    model_config = get_model_config()
    llm_client = get_llm_client()
    prompt = "Write a brief, welcoming introduction for 'The Urban Pollinator Garden Planner'. Explain why pollinator-friendly gardens are important, especially in urban areas. Keep it to one or two short paragraphs."

    active_openai_model_name = config.get('active_openai_model')
    openai_model_id = next((m['id'] for m in model_config.get('openai', []) if m['name'] == active_openai_model_name), None)

    try:
        response = llm_client.chat.completions.create(
            model=openai_model_id,
            messages=[{"role": "user", "content": prompt}]
        )
        intro_text = response.choices[0].message.content.replace('\n', '<br>')
    except Exception as e:
        print(f"Error generating intro: {e}")
        intro_text = "Welcome to your Urban Pollinator Garden Planner! Let's get started on creating a beautiful garden that helps our buzzing friends thrive."

    return f"""
    <div class="page">
        <h1>Introduction</h1>
        <p>{intro_text}</p>
        <h2>How to Use This Planner</h2>
        <p>This planner is designed to help you create a thriving garden that supports bees, butterflies, and hummingbirds. Use the following sections to plan your year, track your plants, and observe the wonderful wildlife that visits your garden.</p>
        <ul>
            <li><strong>Yearly Overview:</strong> Plan your major goals for the year.</li>
            <li><strong>Monthly Planners:</strong> Keep track of tasks, blooms, and pollinator visits each month.</li>
            <li><strong>Garden Bed Planning:</strong> Sketch out your garden layouts.</li>
            <li><strong>Plant Profiles:</strong> Keep detailed records of each plant.</li>
            <li><strong>Notes & Resources:</strong> Extra space for your thoughts and helpful checklists.</li>
        </ul>
    </div>
    """

def generate_yearly_overview():
    """Generates the yearly overview pages as an HTML string."""
    return """
    <div class="page">
        <h1>Yearly Overview</h1>
        <h2>Annual Planting Calendar</h2>
        <p>Use this space to note your key planting dates for the year.</p>
        <div class="notes-box" style="height: 300px;"></div>
        <h2>Pollinator Activity Tracker</h2>
        <p>Track the first and last sightings of your favorite pollinators.</p>
        <table class="table">
            <thead>
                <tr>
                    <th>Pollinator</th>
                    <th>First Sighting</th>
                    <th>Last Sighting</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>Bee</td><td></td><td></td><td></td></tr>
                <tr><td>Butterfly</td><td></td><td></td><td></td></tr>
                <tr><td>Hummingbird</td><td></td><td></td><td></td></tr>
                <tr><td>Other</td><td></td><td></td><td></td></tr>
            </tbody>
        </table>
    </div>
    """

def generate_monthly_planner_pages():
    """Generates 12 monthly planner pages as an HTML string."""
    html = ""
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for month in months:
        html += f"""
        <div class="page">
            <h1>{month}</h1>
            <h2>Monthly To-Do List</h2>
            <ul class="checklist">
                <li><input type="checkbox"> Pruning</li>
                <li><input type="checkbox"> Planting</li>
                <li><input type="checkbox"> Fertilizing</li>
                <li><input type="checkbox"> Watering</li>
            </ul>
            <h2>Bloom Calendar</h2>
            <div class="notes-box" style="height: 150px;"></div>
            <h2>Pollinator Observation Log</h2>
            <p><em>Which flowers attracted the most pollinators this month?</em></p>
            <div class="notes-box" style="height: 150px;"></div>
        </div>
        """
    return html

def generate_garden_bed_planning_pages():
    """Generates garden bed planning grid pages as an HTML string."""
    html = ""
    for i in range(4): # 4 grid pages
        html += f"""
        <div class="page">
            <h1>Garden Bed Plan {i+1}</h1>
            <div class="grid-container">
                {'<div class="grid-item"></div>' * 100}
            </div>
        </div>
        """
    return html

def generate_plant_profile_pages():
    """Generates plant profile pages as an HTML string."""
    html = ""
    for i in range(10): # 10 profile pages
        html += """
        <div class="page">
            <h1>Plant Profile</h1>
            <p><strong>Plant Name:</strong> _________________________</p>
            <p><strong>Sunlight:</strong> ☐ Full Sun ☐ Partial Shade ☐ Shade</p>
            <p><strong>Water Needs:</strong> ☐ Low ☐ Medium ☐ High</p>
            <p><strong>Bloom Time:</strong> _________________________</p>
            <p><strong>Pollinators Attracted:</strong> _________________</p>
            <p><strong>Notes:</strong></p>
            <div class="notes-box" style="height: 400px;"></div>
        </div>
        """
    return html

def generate_notes_pages():
    """Generates lined notes pages as an HTML string."""
    return """
    <div class="page">
        <h1>Notes & Sketches</h1>
        <div class="lined-paper"></div>
    </div>
    """ * 4 # 4 notes pages

def generate_planner_html_content():
    """
    Generates the full content of the garden planner book as an HTML string.
    """
    html_parts = []
    html_parts.append(generate_introduction())
    html_parts.append(generate_yearly_overview())
    html_parts.append(generate_monthly_planner_pages())
    html_parts.append(generate_garden_bed_planning_pages())
    html_parts.append(generate_plant_profile_pages())
    html_parts.append(generate_notes_pages())

    return "".join(html_parts)
