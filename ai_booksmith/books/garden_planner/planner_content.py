from ...llm_provider import get_llm_client
from ...image_gen_provider import get_image_gen_client

def generate_cover_image():
    """
    Generates a cover image for the garden planner using Leonardo.
    """
    image_gen_client = get_image_gen_client()
    prompt = "beautiful watercolor illustration of a lush garden with vegetables and flowers, book cover, award winning, professional"

    try:
        generation_id = image_gen_client.generate(prompt)
        image_url = image_gen_client.poll_for_image(generation_id)
        return image_url
    except Exception as e:
        print(f"Error generating cover image: {e}")
        return None

def generate_planner_content():
    """
    Generates the full content of the garden planner book in Markdown format.
    """
    content = []
    content.append("# My Garden Planner")
    content.append(generate_companion_planting_guide())
    content.append(generate_garden_layout_pages())
    content.append(generate_planting_calendar())
    content.append(generate_plant_log_pages())
    return "\n\n".join(content)

def generate_companion_planting_guide():
    """
    Generates a companion planting guide using an LLM.
    """
    llm_client = get_llm_client()
    prompt = "Generate a concise companion planting guide for common vegetables. Include a brief explanation of what companion planting is. Format it as a markdown table."

    try:
        response = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a gardening expert."},
                {"role": "user", "content": prompt}
            ]
        )
        return "## Companion Planting Guide\n\n" + response.choices[0].message.content
    except Exception as e:
        # In a real app, you'd want more robust error handling and logging
        print(f"Error generating companion planting guide: {e}")
        return "## Companion Planting Guide\n\nCould not generate content at this time."

def generate_garden_layout_pages():
    """
    Generates markdown for grid-style garden layout pages.
    """
    layout_pages = "## Garden Layouts\n\n"
    layout_pages += "Use the grids below to sketch out your garden plans.\n\n"
    for i in range(4):  # Generate 4 layout pages
        layout_pages += f"### Garden Layout Plan {i+1}\n\n"
        # Create a simple markdown grid
        header = "| " + " | ".join([" "] * 10) + " |"
        separator = "|---" * 11 + "|"
        row = "| " + " | ".join(["   "] * 10) + " |"

        layout_pages += header + "\n"
        layout_pages += separator + "\n"
        for _ in range(15): # 15 rows in the grid
            layout_pages += row + "\n"
        layout_pages += "\n\n"
    return layout_pages

def generate_planting_calendar():
    """
    Generates a generic, undated 12-month planting calendar section.
    """
    calendar = "## Planting Calendar\n\n"
    calendar += "Use this calendar to track your planting schedule throughout the year.\n\n"
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for month in months:
        calendar += f"### {month}\n\n"
        calendar += "**Seeds to Sow Indoors:**\n\n"
        calendar += "- \n" * 3
        calendar += "\n**Seeds to Sow Outdoors:**\n\n"
        calendar += "- \n" * 3
        calendar += "\n**Notes:**\n\n\n---\n\n"
    return calendar

def generate_plant_log_pages():
    """
    Generates pages for logging details about specific plants.
    """
    plant_log = "## Plant Logs\n\n"
    plant_log += "Keep a detailed record of each plant in your garden.\n\n"
    for i in range(10):  # Generate 10 plant log pages
        plant_log += f"### Plant Record\n\n"
        plant_log += "**Plant Name:** ____________________\n\n"
        plant_log += "**Variety:** ____________________\n\n"
        plant_log += "**Date Planted:** ____________\n\n"
        plant_log += "**Germination Date:** ____________\n\n"
        plant_log += "**Transplant Date:** ____________\n\n"
        plant_log += "**Source (Seed Co., Nursery, etc.):** ____________________\n\n"
        plant_log += "**Watering Schedule:**\n\n\n"
        plant_log += "**Fertilizing Schedule:**\n\n\n"
        plant_log += "**Notes & Observations (e.g., pests, diseases, growth milestones):**\n\n\n\n"
        plant_log += "---\n\n"
    return plant_log
