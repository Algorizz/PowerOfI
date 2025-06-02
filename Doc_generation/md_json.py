import json
import re

def markdown_to_slides(md_path: str, json_path: str = None) -> list:
    """
    Converts a markdown file where each section starts with a '# Title' and is followed by content,
    into a structured JSON list of slide objects.

    Args:
        md_path (str): Path to the input markdown file.
        json_path (str): Optional path to save the output JSON.

    Returns:
        list: A list of dicts with 'title' and 'content' for each slide.
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split using regex to capture sections
    matches = re.findall(r"# (.+?)\n(.*?)(?=\n# |\Z)", text, re.DOTALL)

    slides = []
    for title, content in matches:
        slides.append({
            "title": title.strip(),
            "content": content.strip()
        })

    if json_path:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(slides, f, indent=4)

    return slides
