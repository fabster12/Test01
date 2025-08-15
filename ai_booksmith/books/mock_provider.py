import json
import time
import uuid

def get_mock_themes():
    return {
        "themes": [
            {"title": "Mock Theme 1: The Last Cyber-Knight", "description": "A mock description about a knight in a cyber world.", "reasoning": "This is a good niche because cyberpunk is popular."},
            {"title": "Mock Theme 2: The Haunted Victorian Manor", "description": "A mock description about a spooky house.", "reasoning": "Gothic horror is a classic, evergreen niche."},
        ]
    }

def get_mock_ideas():
    return {
        "ideas": [
            {"title": "Mock Idea 1: Galactic Echoes", "logline": "A mock logline about space.", "writing_style": "Fast-paced.", "art_style": "Sci-fi concept art."},
            {"title": "Mock Idea 2: The Baker of Quiet Street", "logline": "A mock logline about a baker.", "writing_style": "Cozy and warm.", "art_style": "Ghibli-esque watercolor."},
        ]
    }

def get_mock_blueprint():
    return {
        "synopsis": "### Chapter 1: The Mock Beginning\n\nThis is the mock synopsis for the first chapter.\n\n### Chapter 2: The Mock Middle\n\nThis is the mock synopsis for the second chapter.",
        "back_cover_blurb": "This is a thrilling mock back cover blurb that will surely sell millions of copies."
    }

def get_mock_chapter_text():
    return "This is the full text for a mock chapter. It is very engaging and well-written, following all the instructions from the prompt perfectly. The story advances, characters are developed, and the plot thickens."

def get_mock_image_subjects():
    return {
        "scenes": ["A brave hero facing a dragon", "A quiet village by the sea", "A futuristic cityscape at night"]
    }

def mock_openai_chat_completion(model, messages, **kwargs):
    """Simulates the OpenAI Chat Completion response."""
    # A simple way to decide which mock data to return
    prompt_content = messages[-1]['content'].lower()
    if "brainstorm 5" in prompt_content:
        data = get_mock_themes()
    elif "generate 10 book ideas" in prompt_content:
        data = get_mock_ideas()
    elif "synopsis" in prompt_content and "blurb" in prompt_content:
        data = get_mock_blueprint()
    elif "identify 3" in prompt_content: # For image scene prompts
        data = get_mock_image_subjects()
    else: # Default to chapter text
        data = {"content": get_mock_chapter_text()}

    # Mimic the structure of the actual OpenAI response object
    class MockChoice:
        def __init__(self, content):
            class MockMessage:
                def __init__(self, content):
                    self.content = content
            self.message = MockMessage(content)

    class MockResponse:
        def __init__(self, choices):
            self.choices = choices

    if "content" in data: # For simple text generation
         return MockResponse([MockChoice(data["content"])])
    else: # For JSON generation
        return MockResponse([MockChoice(json.dumps(data))])


def mock_leonardo_image_generation(prompt, **kwargs):
    """Simulates the two-step Leonardo image generation process."""
    print(f"MOCK: Starting image generation for prompt: '{prompt}'")
    generation_id = str(uuid.uuid4())

    # Simulate the polling process
    print("MOCK: Polling for generation result...")
    time.sleep(1) # Simulate network delay

    print("MOCK: Generation complete.")
    return {
        "generations_by_pk": {
            "status": "COMPLETE",
            "generated_images": [
                {"url": f"https://placehold.co/512x768?text=Mock+Image\\n{prompt[:30]}..."}
            ]
        }
    }
