import json

class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)

class MockMessage:
    def __init__(self, content):
        self.content = content

class MockCompletion:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

def mock_openai_chat_completion(model, messages, response_format=None):
    # Simulate a response for brainstorming subjects
    if "brainstorm a list" in messages[0]['content']:
        subjects = ["friendly robot", "curious alien", "magical castle", "flying car", "talking animal"]
        return MockCompletion(json.dumps(subjects))
    # Simulate a response for generating themes
    elif "brainstorm 5 themes" in messages[0]['content']:
        themes = {
            "themes": [
                {"title": "The Last Starship", "description": "A generation ship on a final, desperate voyage.", "reasoning": "High-concept sci-fi with strong emotional stakes."},
                {"title": "The Clockwork Detective", "description": "A steampunk mystery set in Victorian London.", "reasoning": "Combines two popular genres with a unique aesthetic."},
                {"title": "The Dragon's Heir", "description": "A young orphan discovers they are the last of a powerful lineage.", "reasoning": "Classic fantasy trope with strong potential for world-building."},
                {"title": "The City of Whispers", "description": "A noir thriller set in a city where secrets are currency.", "reasoning": "Atmospheric and suspenseful, with a unique aural twist."},
                {"title": "The Gastronomist", "description": "A culinary adventure through a fantastical world.", "reasoning": "A lighthearted and sensory-rich story with a unique focus."}
            ]
        }
        return MockCompletion(json.dumps(themes))
    else:
        return MockCompletion("This is a mock response.")

def mock_leonardo_image_generation(prompt, model_id=None):
    return {
        "generations_by_pk": {
            "generated_images": [
                {
                    "url": "https://cdn.leonardo.ai/users/25b682e5-5598-4434-916c-2e6b6680459c/generations/a45e7da2-b44f-6e45-3d0a-dece5d83d6ec/Default_A_simple_clean_line_art_coloring_book_page_for_child_0.jpg"
                }
            ]
        }
    }
