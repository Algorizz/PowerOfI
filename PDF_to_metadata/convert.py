# === convert.py ===
import os
import json
from pdf_txt import pdf_to_text_with_ocr
from datasetgenerator import generate_metadata_json
from azure_llm import call_llm


def convert_pdf_to_summary(pdf_path: str):
    # Step 1: Create text output path
    txt_path = pdf_path.replace("Dataset", "Doc txt").replace(".pdf", ".txt")
    os.makedirs(os.path.dirname(txt_path), exist_ok=True)

    # Step 2: OCR - PDF to text
    print("📄 Extracting text from PDF using OCR...")
    pdf_to_text_with_ocr(pdf_path, txt_path)

    # Step 3: Create JSON metadata output path
    metadata_path = txt_path.replace("Output doc", "metadata").replace(".txt", ".json")
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

    # Step 4: Text to JSON metadata
    print("🧠 Generating metadata JSON...")
    generate_metadata_json(txt_path, metadata_path)

    # Step 5: Load JSON and extract slide titles
    with open(metadata_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    titles = [slide.get("Slide Title", "") for slide in json_data if slide.get("Slide Title")]
    joined_titles = "; ".join(titles)

    # Step 6: Generate meta-summary
    print("📝 Generating meta-summary from slide titles...")
    prompt = f"""
    You are an expert business strategist. Your task is to produce an embedding-friendly, semantically rich representation of a business presentation. 

    Analyze the following list of slide titles and generate a clear, content-dense paragraph that captures the overall theme, strategic focus, and key ideas. This output will be stored in a vector database and should be optimized for semantic similarity search.

    Slide Titles:
    {joined_titles}

    Output only the paragraph with no extra notes or commentary.
    """
    summary = call_llm(prompt).strip()

    # Step 7: Save summary
    processed_txt_path = txt_path.replace("Output doc", "Processed txt").replace(".txt", "_summary.txt")
    os.makedirs(os.path.dirname(processed_txt_path), exist_ok=True)
    with open(processed_txt_path, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"✅ Summary saved to: {processed_txt_path}")


if __name__ == "__main__":
    input_pdf = "Dataset\Poi - Algorizz Colaboration-20250523T130226Z-1-001\Poi - Algorizz Colaboration\Tynor\Development of Key Talent_Tynor_March 2023_Diya Kapur Misra.pptx.pdf"
    convert_pdf_to_summary(input_pdf)
