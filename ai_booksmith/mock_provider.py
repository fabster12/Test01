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
    """
    A mock function that returns realistic, structured data based on the prompt.
    """
    prompt = ""
    # In the new OpenAI API versions, `messages` is a list of dicts
    if isinstance(messages, list) and messages:
        prompt = messages[-1]['content']

    # For generating book ideas
    if "generate 10 book ideas" in prompt:
        mock_data = {
            "ideas": [
                {"title": "The Quantum Thief", "logline": "A master thief steals memories in a futuristic city.", "writing_style": "Hard-boiled sci-fi noir", "art_style": "Cyberpunk anime"},
                {"title": "The Last Garden", "logline": "In a world covered by desert, a young girl discovers the last patch of green.", "writing_style": "Hopeful post-apocalyptic", "art_style": "Studio Ghibli inspired"},
                {"title": "The Alchemist's Daughter", "logline": "A young woman must complete her father's work to save her city from a magical plague.", "writing_style": "High fantasy with a focus on magic systems", "art_style": "Classic fantasy illustration"},
                {"title": "The Star Sailors", "logline": "A crew of explorers sails the cosmos on solar-powered ships.", "writing_style": "Optimistic space opera", "art_style": "Colorful retro-futurism"},
                {"title": "The Whispering Woods", "logline": "A group of children get lost in an enchanted forest where the trees have secrets.", "writing_style": "Dark fairytale", "art_style": "Tim Burton-esque"}
            ]
        }
        return MockCompletion(json.dumps(mock_data))

    # For generating a book blueprint (synopsis and blurb)
    elif "generate a detailed, multi-chapter synopsis" in prompt:
        mock_data = {
            "synopsis": """
# Chapter 1: The Discovery
Our hero, a young archivist, finds a hidden map in a dusty tome.
# Chapter 2: The Journey Begins
Following the map, they venture into the forbidden lands.
# Chapter 3: The First Trial
They overcome a great obstacle and learn a valuable lesson.
# Chapter 4: The Betrayal
A trusted companion reveals their true intentions.
# Chapter 5: The Final Confrontation
The hero confronts the antagonist and saves the day.
            """,
            "back_cover_blurb": "In a world of forgotten lore, one archivist's discovery will change everything. A perilous journey, a shocking betrayal, and a destiny to be fulfilled. Will they be able to unlock the secrets of the past before it's too late?"
        }
        return MockCompletion(json.dumps(mock_data))

    # For generating image prompts from a chapter
    elif "visually interesting scenes to illustrate" in prompt:
        mock_data = {
            "scenes": [
                "The hero holding the glowing map in the dark library.",
                "A wide shot of the hero looking out over the vast, forbidden lands.",
                "A close-up of the hero's face as they realize their companion's betrayal."
            ]
        }
        return MockCompletion(json.dumps(mock_data))

    # For generating KDP metadata
    elif "generate KDP metadata" in prompt:
        mock_data = {
            "keywords": ["fantasy", "adventure", "magic", "ancient secrets", "epic journey", "betrayal", "hero's quest"],
            "categories": ["Fiction > Fantasy > Epic", "Fiction > Fantasy > Action & Adventure"]
        }
        return MockCompletion(json.dumps(mock_data))

    # For brainstorming coloring book themes
    elif "coloring book themes" in prompt:
        mock_data = {
            "suggestions": ["Mystical Forest Creatures", "Cute Baby Animals", "Under the Sea Adventures", "Magical Castles and Dragons", "Robots and Spaceships"]
        }
        return MockCompletion(json.dumps(mock_data))

    # For brainstorming coloring book subjects
    elif "subjects for a children's coloring book" in prompt:
        mock_data = {
            "subjects": ["a friendly lion", "a smiling sunflower", "a curious robot", "a brave knight", "a magical unicorn", "a cheerful octopus", "a racing car", "a soaring dragon"]
        }
        return MockCompletion(json.dumps(mock_data))

    # Fallback for any other prompt
    else:
        return MockCompletion(json.dumps({"text": "This is a generic mock response for an unrecognized prompt."}))


def mock_leonardo_image_generation(prompt, model_id=None):
    # This mock can remain simple as it just needs to return a plausible image URL.
    return {
        "generations_by_pk": {
            "generated_images": [
                {
                    "url": "https://cdn.leonardo.ai/users/25b682e5-5598-4434-916c-2e6b6680459c/generations/a45e7da2-b44f-6e45-3d0a-dece5d83d6ec/Default_A_simple_clean_line_art_coloring_book_page_for_child_0.jpg"
                }
            ]
        }
    }
