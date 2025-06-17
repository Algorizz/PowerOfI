import json
import pdfkit
import re
import os
import uuid
from core.titlePage import titlePage
from core.pointOfViewPage import pointOfViewPage
from core.MethodologyFlowchartPage import MethodologyFlowchartPage
from core.getTemplates import getProfileHtml, getCredentialHtml, getThankYouHtml
from core.decideSlideType import decideSlideType
from core.infographicspage import InfoGraphicsPage
from core.circularinfographics import CircularInfoGraphicsPage
from core.imageGen import ImageGenerator

# API configuration
API_KEY = "b46942d9305c42d78df6078a465419ae"
ENDPOINT = "https://qrizz-us.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview"

# Load slide data
with open("slides_raw_data/final_output (8).json", "r", encoding="utf-8") as f:
    slide_data = json.load(f)

top_slides = slide_data

# Initialize generators
title_page_gen = titlePage(api_key=API_KEY, endpoint_url=ENDPOINT)
pov_gen = pointOfViewPage(api_key=API_KEY, endpoint_url=ENDPOINT)
method_gen = MethodologyFlowchartPage(api_key=API_KEY, endpoint_url=ENDPOINT)
decideSlide = decideSlideType(api_key=API_KEY, endpoint_url=ENDPOINT)
infoGraphicSlide = InfoGraphicsPage(api_key=API_KEY, endpoint_url=ENDPOINT)
circularGraphics = CircularInfoGraphicsPage(api_key=API_KEY, endpoint_url=ENDPOINT)
image_generator = ImageGenerator()
html_blocks = []

import re

import os
import re
import uuid
import tempfile
import pdfkit
from PyPDF2 import PdfMerger


# Your slide

def html_to_temp_pdf(html: str) -> str:
    cleaned_html = re.sub(r"```(?:html|css|json|python)?\n?", "", html).replace("```", "")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_path = tmp_pdf.name

    pdfkit.from_string(cleaned_html, tmp_path, options={
        'page-width': '280mm',
        'page-height': '180mm',
        'encoding': 'UTF-8',
        'margin-top': '5mm',
        'margin-bottom': '5mm',
        'margin-left': '32mm',
        'margin-right': '10mm',
        'no-outline': None,
        'print-media-type': '',
    })

    return tmp_path

def extract_slide_title(slide: dict) -> str:
    if isinstance(slide, dict):
        return slide.get("slide_title", "").strip().lower()
    return ""

def generate_proposal_pdf(slides):
    pdf_paths = []

    for i, slide in enumerate(slides):
        
        if not isinstance(slide, dict):
            raise ValueError(f"Slide at index {i} is not a valid dictionary: {slide}")
        image_html = ""
        slide_title = extract_slide_title(slide)
        slide_type = slide.get("slide_type", "").lower()
        content = slide.get("slide_content", "")
        print(f"[Slide {i+1}] Title: {slide_title} | Type: {slide_type}")

        if "title" in slide_type:
            html = title_page_gen.generate_html(context=content)
            image_html = ""
            if "image_prompt" in slide and slide["image_prompt"].strip():
                print("image present, generating image..")
                base64_img = image_generator.generate_image_base64(slide["image_prompt"], content)
                if base64_img:
                    image_html = f'''
                    <div style="text-align: center; margin-top: 5px;">
                        <img src="{base64_img}" alt="Generated Visual" style="max-width:30%;" />
                    </div>
                    '''
                    html += image_html
                    html += '<div style="page-break-after: always;"></div>'
                    print("image added to slide")
        

        elif "infographics" in slide_type:
            html = infoGraphicSlide.generate_html(context=content)
        elif "solution" in slide_type:
            html = method_gen.generate_html(context=content)
        elif "summary & action plan" in slide_type:
            html = method_gen.generate_html(context=content)
        elif slide_type in ["introduction", "problem statement","summary", "features", "features overview", "feature overview", "insight", "insights", "conclusion", "summary & action plan", "overview"]:
            html = pov_gen.generate_html(context=content)
            image_html = ""
            if "image_prompt" in slide and slide["image_prompt"].strip():
                print("image present, generating image..")
                base64_img = image_generator.generate_image_base64(slide["image_prompt"], content)
                if base64_img:
                    image_html = f'''
                    <div style="text-align: center; margin-top: 5px;">
                        <img src="{base64_img}" alt="Generated Visual" style="max-width:30%;" />
                    </div>
                    '''
                    html += image_html
                    html += '<div style="page-break-after: always;"></div>'
                    print("image added to slide")
        else:
            html = f"<div><h2>{slide.get('slide_title', 'Untitled')}</h2><pre style='white-space: pre-wrap;'>{content}</pre></div>"


        html += '<div style="page-break-after: always;"></div>'
        pdf_path = html_to_temp_pdf(html)
        pdf_paths.append(pdf_path)

    # Append static pages
    for static_html in [getProfileHtml(), getCredentialHtml(), getThankYouHtml()]:
        pdf_paths.append(html_to_temp_pdf(static_html))

    # Create final merged PDF
    os.makedirs("GeneratedPDF", exist_ok=True)
    document_id = str(uuid.uuid4())[:8]
    output_path = os.path.join("GeneratedPDF", f"proposal_output_{document_id}.pdf")

    merger = PdfMerger()
    for path in pdf_paths:
        merger.append(path)
    merger.write(output_path)
    merger.close()

    # Cleanup temp files
    for path in pdf_paths:
        os.remove(path)

    print(f"✅ PDF generated: {output_path}")

# Run generation
# generate_proposal_pdf(top_slides)