import requests
import re
import json

BASE_URL = "http://127.0.0.1:5003"
session = requests.Session()

def test_step(name, method, url, **kwargs):
    print(f"--- Testing: {name} ---")
    try:
        response = session.request(method, url, **kwargs)
        response.raise_for_status()
        print(f"  - SUCCESS: Status Code {response.status_code}")
        return response, response.text
    except requests.exceptions.RequestException as e:
        print(f"  - FAILED: {e}")
        return None, None

def run_fiction_flow():
    print(">>> Starting Fiction Book Test Flow...")

    steps = [
        ("Visit Homepage", "GET", f"{BASE_URL}/"),
        ("Go to Brainstorming", "GET", f"{BASE_URL}/brainstorm/fiction"),
        ("Generate Themes", "POST", f"{BASE_URL}/generate_themes/fiction", {'data': {'topic': 'space opera', 'find_niche': 'true'}}),
    ]
    for name, method, url, kwargs in [(s[0], s[1], s[2], s[3] if len(s) > 3 else {}) for s in steps]:
        resp, _ = test_step(name, method, url, **kwargs)
        if not resp: return

    # Step 4: Select a theme
    mock_themes = get_mock_themes()
    payload = {'book_type': 'fiction', 'selected_theme_json': json.dumps(mock_themes['themes'][0])}
    resp, _ = test_step("Select Theme", "POST", f"{BASE_URL}/select_theme", data=payload, allow_redirects=True)
    if not resp: return

    # Step 5: Generate Ideas
    payload = {'language': 'English', 'genre': 'Sci-Fi', 'description': 'A test description', 'word_count': '10000'}
    resp, _ = test_step("Generate Ideas", "POST", f"{BASE_URL}/fiction/generate_ideas", data=payload)
    if not resp: return

    # Step 6: Select an idea
    payload = {'selected_idea_index': '0'}
    resp, _ = test_step("Select Idea", "POST", f"{BASE_URL}/fiction/select_idea", data=payload, allow_redirects=False)
    if not resp or not (redirect_url := resp.headers.get('Location')): return

    project_id = re.search(r'/fiction/([\w-]+)/blueprint', redirect_url).group(1)
    print(f"  - INFO: Created project with ID: {project_id}")

    # Step 7: Generate Blueprint and initialize chapters
    test_step("Generate Blueprint", "POST", f"{BASE_URL}/fiction/{project_id}/generate_blueprint")
    test_step("Visit Writing Room (Initializes Chapters)", "GET", f"{BASE_URL}/fiction/{project_id}/writing_room")

    # Step 8: Generate and Save Chapter 0
    test_step("Generate Chapter 0", "POST", f"{BASE_URL}/fiction/{project_id}/generate_chapter/0")
    test_step("Save Chapter 0", "POST", f"{BASE_URL}/fiction/{project_id}/save_chapter/0", data={'chapter_text': '...'})

    # Step 9: Build Final Package
    payload = {'author_name': 'Test Author', 'trim_width_mm': '152', 'trim_height_mm': '229'}
    resp, body = test_step("Build Final Package", "POST", f"{BASE_URL}/fiction/{project_id}/build_package", data=payload)
    if not resp: return

    if resp.headers.get('Content-Type') == 'application/zip':
        print("  - SUCCESS: Received ZIP file.")
    else:
        print(f"  - FAILED: Expected ZIP file, but got {resp.headers.get('Content-Type')}")

    print(">>> Fiction Book Test Flow COMPLETED.")

def get_mock_themes():
    return {"themes": [{"title": "Mock Theme 1", "description": "Mock Desc"}]}

if __name__ == '__main__':
    run_fiction_flow()
