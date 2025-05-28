import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os

def pdf_to_text_with_ocr(pdf_path, output_txt_path):
    # Check if file already exists
    if os.path.exists(output_txt_path):
        print(f"⚠️ File already exists: {output_txt_path} — skipping extraction.")
        return

    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_txt_path), exist_ok=True)

    # Open the PDF
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Get text using OCR from rendered image of the page
        pix = page.get_pixmap(dpi=300)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))

        # OCR the image
        text = pytesseract.image_to_string(img, lang='eng')

        # Append to full text with markdown annotation
        full_text += (
            f"\n\n--- Page {page_num + 1} ---\n"
            f"> ⚠️ Extracted via OCR (image-based content)\n\n"
            f"{text.strip()}"
        )

    # Save to output file
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"✅ Text extracted and saved to: {output_txt_path}")

# Example usage
pdf_file_path ="Dataset/Poi - Algorizz Colaboration-20250523T130226Z-1-001/Poi - Algorizz Colaboration/Belden/Belden - Final Proposal for HR in Progress Ph 2 - 3Oct24 (1) (1).pdf"
output_text_file = "Doc txt/Belden - Final Proposal for HR in Progress Ph 2 - 3Oct24 (1) (1).txt"

pdf_to_text_with_ocr(pdf_file_path, output_text_file)
