import os
from dotenv import load_dotenv
from openai import OpenAI

def test_openai_connection():
    """
    Tests the connection to the OpenAI API and a simple chat completion.
    """
    print("--- Running OpenAI LLM Test ---")

    # Load environment variables from .env file
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    ssl_cert_file = os.getenv("SSL_CERT_FILE")

    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

    print(f"Using SSL_CERT_FILE: {ssl_cert_file if ssl_cert_file else 'Not set, using default.'}")

    try:
        # The OpenAI client, via httpx, will automatically use the SSL_CERT_FILE
        # environment variable if it is set.
        client = OpenAI(api_key=api_key)

        print("Sending request to OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Hello, this is a test. What is 1 + 1?"}
            ]
        )

        print("Successfully received response from OpenAI.")
        print("Response:", response.choices[0].message.content)

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check your API key, network connection, and SSL certificate path if applicable.")

if __name__ == "__main__":
    test_openai_connection()
