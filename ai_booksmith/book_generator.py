import os
import pypandoc

def create_coloring_book_pdf(title, image_paths, output_dir):
    """
    Creates a PDF for a coloring book from a list of image paths.
    """
    markdown_content = f"---\ntitle: {title}\n---\n\n"
    for image_path in image_paths:
        markdown_content += f"![Coloring Page]({image_path})\n\n"

    output_filename = f"{title.replace(' ', '_').lower()}_coloring_book.pdf"
    output_path = os.path.join(output_dir, output_filename)

    try:
        pypandoc.convert_text(
            markdown_content,
            'pdf',
            format='md',
            outputfile=output_path,
            extra_args=['-V', 'geometry:paperwidth=8.5in', '-V', 'geometry:paperheight=11in', '-V', 'geometry:margin=0.5in']
        )
        return output_path
    except Exception as e:
        print(f"Error creating PDF with Pandoc: {e}")
        return None
