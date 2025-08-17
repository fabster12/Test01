import json
import random

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
    """
    A mock function that returns realistic, structured data based on the prompt.
    """
    prompt = ""
    if isinstance(messages, list) and messages:
        prompt = messages[-1]['content']

    # For generating book ideas
    if "generate 10 book ideas" in prompt:
        mock_data = {
            "ideas": [
                {"title": "The Quantum Thief", "logline": "A master thief steals memories in a futuristic city.", "writing_style": "Hard-boiled sci-fi noir", "art_style": "Cyberpunk anime"},
                {"title": "The Last Garden", "logline": "In a world covered by desert, a young girl discovers the last patch of green.", "writing_style": "Hopeful post-apocalyptic", "art_style": "Studio Ghibli inspired"},
            ]
        }
        return MockCompletion(json.dumps(mock_data))

    # For generating a book blueprint (synopsis and blurb)
    elif "generate a detailed, multi-chapter synopsis" in prompt:
        mock_data = {
            "synopsis": """
# Chapter 1: The Discovery
Our hero finds a map. {{image here of a hero finding a map in a library}}
# Chapter 2: The Journey
The hero travels to a new land. {{image here of a hero on a boat}}
            """,
            "back_cover_blurb": "A mock blurb for an exciting adventure."
        }
        return MockCompletion(json.dumps(mock_data))

    # For generating chapter text
    elif "Write the full text for Chapter" in prompt:
        mock_text = """
This is the mock text for the chapter. It is a long and winding road that leads to the castle.
{{image here of a long and winding road leading to a castle}}
The hero was brave and strong, and they were not afraid of the dark.
{{image here of the hero looking brave}}
        """
        return MockCompletion(mock_text)

    # For generating image prompts from a chapter
    elif "visually interesting scenes to illustrate" in prompt:
        mock_data = {
            "scenes": [
                "The hero holding a glowing map.",
                "A wide shot of the hero looking out over the forbidden lands."
            ]
        }
        return MockCompletion(json.dumps(mock_data))

    # For generating KDP metadata
    elif "generate KDP metadata" in prompt:
        mock_data = {
            "keywords": ["mock fantasy", "mock adventure", "mock magic"],
            "categories": ["Fiction > Mock > Epic", "Fiction > Mock > Test"]
        }
        return MockCompletion(json.dumps(mock_data))

    # For brainstorming coloring book themes
    elif "coloring book themes" in prompt:
        mock_data = {
            "suggestions": ["Mystical Forest Creatures", "Cute Baby Animals", "Under the Sea Adventures"]
        }
        return MockCompletion(json.dumps(mock_data))

    # For brainstorming coloring book subjects
    elif "subjects for a children's coloring book" in prompt:
        mock_data = {
            "subjects": ["a friendly lion", "a smiling sunflower", "a curious robot", "a brave knight"]
        }
        return MockCompletion(json.dumps(mock_data))

    # Fallback for any other prompt
    else:
        return MockCompletion(json.dumps({"text": "This is a generic mock response for an unrecognized prompt."}))


def mock_leonardo_image_generation(prompt, model_id=None):
    # Use a placeholder image service for more variety
    width = 1024
    height = 768
    seed = random.randint(1, 1000)
    image_url = f"https://picsum.photos/seed/{seed}/{width}/{height}"

    return {
        "generations_by_pk": {
            "generated_images": [
                {
                    "url": image_url
                }
            ]
        }
    }
