from playwright.sync_api import sync_playwright, Page, expect

def run_verification(page: Page):
    """
    Navigates to the running application and takes a screenshot.
    """
    # Navigate to the local development server.
    page.goto("http://localhost:3000")

    # Wait for the main app container to be visible.
    # We use the '.app' class we defined in App.css.
    app_container = page.locator('.app')
    expect(app_container).to_be_visible(timeout=10000) # Increased timeout for initial load

    # Wait for the canvas to be ready, as it might load asynchronously
    canvas = page.locator('.react-flow__viewport')
    expect(canvas).to_be_visible()

    # Take a screenshot of the page.
    page.screenshot(path="jules-scratch/verification/verification.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        run_verification(page)
        browser.close()
