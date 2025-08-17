import os
import pypandoc
from .llm_provider import get_llm_client
from .config_manager import get_config, get_model_config

def create_coloring_book_pdf(title, image_paths, subjects, output_dir):
    """
    Creates a PDF for a coloring book from a list of image paths,
    with a blank page or a fact on the left side of each coloring page.
    """
    llm_client = get_llm_client()
    config = get_config()
    model_config = get_model_config()
    markdown_content = f"---\ntitle: {title}\n---\n\n"

    # Add a title page
    markdown_content += f"# {title}\n\n"
    markdown_content += "\\newpage\n\n"

    for i, image_path in enumerate(image_paths):
        # Add content for the left-hand page (which will be blank or have a fact)
        # First, add a blank page to ensure the coloring page is on the right
        markdown_content += "\\newpage\n\n"

        # Add a fun fact on the left page
        subject = subjects[i]
        fact_prompt = f"Tell me one single, interesting, and simple fun fact about a {subject} for a children's coloring book page. Respond with only the fact, in one sentence."
        try:
            active_openai_model_name = config.get('active_openai_model')
            openai_model_id = next((m['id'] for m in model_config.get('openai', []) if m['name'] == active_openai_model_name), None)
            response = llm_client.chat.completions.create(
                model=openai_model_id,
                messages=[{"role": "user", "content": fact_prompt}]
            )
            fun_fact = response.choices[0].message.content
            markdown_content += f'<div style="text-align: center; font-style: italic; margin-top: 50%;">{fun_fact}</div>\n\n'
        except Exception as e:
            print(f"Error generating fun fact for {subject}: {e}")
            # If it fails, the page will just be blank, which is acceptable.
            pass

        # Add the coloring page on the right
        markdown_content += "\\newpage\n\n"
        markdown_content += f"![{subject}]({image_path})\n\n"

    output_filename = f"{title.replace(' ', '_').lower()}_coloring_book.pdf"
    output_path = os.path.join(output_dir, output_filename)

    try:
        pypandoc.convert_text(
            markdown_content,
            'pdf',
            format='md',
            outputfile=output_path,
            extra_args=['-V', 'geometry:paperwidth=8.5in', '-V', 'geometry:paperheight=11in', '-V', 'geometry:margin=1in']
        )
        return output_path
    except Exception as e:
        print(f"Error creating PDF with Pandoc: {e}")
        return None
