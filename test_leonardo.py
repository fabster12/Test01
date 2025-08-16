import os
from dotenv import load_dotenv
from ai_booksmith.image_gen_provider import LeonardoAPI

def test_leonardo_connection():
    """
    Tests the connection to the Leonardo API and a simple image generation.
    """
    print("--- Running Leonardo Image Generation Test ---")

    # Load environment variables from .env file
    load_dotenv()

    api_key = os.getenv("LEONARDO_API_KEY")
    ssl_cert_file = os.getenv("SSL_CERT_FILE")

    if not api_key:
        print("Error: LEONARDO_API_KEY environment variable not set.")
        return

    print(f"Using SSL_CERT_FILE: {ssl_cert_file if ssl_cert_file else 'Not set, using default.'}")

    try:
        # The LeonardoAPI client is written to accept the path to the SSL cert file
        client = LeonardoAPI(api_key=api_key, ssl_cert_file=ssl_cert_file)

        prompt = "A high-resolution photo of a single red rose"
        print(f"Sending request to Leonardo API with prompt: '{prompt}'...")

        # Using a specific, known-good model for testing if possible.
        # This is the default from the main app.
        model_id = "b7aa9931-a3e3-433e-b7a1-34358514a362"

        generation_id = client.generate(prompt, model_id=model_id)
        print(f"Generation job started with ID: {generation_id}. Polling for result...")

        image_url = client.poll_for_image(generation_id)

        if image_url:
            print("Successfully generated image.")
            print("Image URL:", image_url)
        else:
            print("Image generation failed or timed out.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check your API key, network connection, and SSL certificate path if applicable.")

if __name__ == "__main__":
    test_leonardo_connection()
