import os
import json
import re
from langchain_openai import AzureOpenAIEmbeddings
from llms.azure_llm import call_llm
from qdrant_client import QdrantClient
from openai import AzureOpenAI
from langchain.embeddings.base import Embeddings
from datetime import datetime
from openai import OpenAI
from llms.search_llm import PerplexityResearchAgent

# === ENVIRONMENT SETUP ===
os.environ["AZURE_OPENAI_API_KEY"] = "b46942d9305c42d78df6078a465419ae"
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-12-01-preview"
os.environ["QDRANT_API_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.ota3xr4-xFLlm4d8P42hHHPAvFFb3K-SVPnSUx7ZRrE"
os.environ["PERPLEXITY_API_KEY"] = "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"

# Initializing Perplexity-compatible client
agent = PerplexityResearchAgent(os.getenv("PERPLEXITY_API_KEY"))

# === Azure Embedding for Retrieval ===
class AzureOpenAIEmbeddings(Embeddings):
    def __init__(self, client, deployment):
        self.client = client
        self.deployment = deployment

    def embed_documents(self, texts):
        response = self.client.embeddings.create(
            input=texts,
            model=self.deployment
        )
        return [item.embedding for item in response.data]

    def embed_query(self, text):
        return self.embed_documents([text])[0]

embedding_model = AzureOpenAIEmbeddings(
    client=AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint="https://qrizz-us.openai.azure.com",
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    ),
    deployment="text-embedding-3-small"
)

qdrant = QdrantClient(
    url="https://31ab61e9-62ac-4ad3-980a-a7ddd6d179ae.us-east4-0.gcp.cloud.qdrant.io:6333",
    api_key=os.getenv("QDRANT_API_KEY")
)

# === Persona Retrieval Function ===
def retrieve_persona_summary(query: str):
    query_vector = embedding_model.embed_query(query)
    results = qdrant.search(
        collection_name="new-pipline",
        query_vector=query_vector,
        limit=1
    )
    if not results:
        return ""

    payload = results[0].payload
    tone = payload.get("tone_distribution", "")
    layout = payload.get("layout_distribution", "")
    visuals = payload.get("visual_cues", "")

    return f"Tone: {tone}\nLayout: {layout}\nVisual Cues: {visuals}"


# === JSON Cleaner ===
def clean_llm_response(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            content = parts[1].strip()
            if content.lower().startswith("json"):
                content = content[4:].strip()
            return content
    elif text.startswith("'''") and text.endswith("'''"):
        return text.strip("'''").strip()
    return text


# === AGENTS ===
def user_input_agent(state):
    return {"user_input": state.get("user_input", "")}

# def search_assistant(user_input: str, prompt: str) -> str:
#     """
#     Uses PerplexityResearchAgent to search the web, saves the query and result in a Markdown file,
#     and returns the response content.
#     """
#     # === Step 1: Prepare storage path ===
#     os.makedirs("search_info", exist_ok=True)
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     safe_filename = user_input.replace(" ", "_").lower()
#     file_path = os.path.join("search_info", f"{safe_filename}_{timestamp}.md")

#     # === Step 2: Save the query ===
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(f"# Project: {user_input}\n\n")
#         f.write(f"## Search Query:\n{prompt}\n\n")

#     # === Step 3: Make API Call ===
#     try:
#         content = agent.run(prompt)
#     except Exception as e:
#         content = f"❌ Error while searching: {e}"

#     # === Step 4: Save result ===
#     with open(file_path, "a", encoding="utf-8") as f:
#         f.write(f"## Perplexity Response:\n{content}\n")

#     return content

def search_assistant(user_input: str, prompt: str) -> str:
    """
    Uses PerplexityResearchAgent to search the web, saves the query and result in a Markdown file,
    and returns the response content.
    """
    # === Step 1: Prepare storage path ===
    os.makedirs("search_info", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Improved filename sanitization
    safe_filename = "".join(c for c in user_input if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_filename = safe_filename.replace(" ", "_").lower()[:50]  # Limit length
    
    # Ensure .md extension is properly added
    file_path = os.path.join("search_info", f"{safe_filename}_{timestamp}.md")
    
    print(f"Creating file: {file_path}")  # Debug line

    # === Step 2: Save the query ===
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# Project: {user_input}\n\n")
            f.write(f"## Search Query:\n{prompt}\n\n")
            f.flush()  # Ensure data is written to disk
        print(f"Query saved successfully")  # Debug line
    except Exception as e:
        print(f"Error saving query: {e}")
        return f"❌ Error saving query: {e}"

    # === Step 3: Make API Call ===
    try:
        content = agent.run(prompt)
        print(f"API call successful, content length: {len(str(content))}")  # Debug line
    except Exception as e:
        content = f"❌ Error while searching: {e}"
        print(f"API call failed: {e}")  # Debug line

    # === Step 4: Save result ===
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"## Perplexity Response:\n{content}\n")
            f.flush()  # Ensure data is written to disk
        print(f"Response saved successfully")  # Debug line
    except Exception as e:
        print(f"Error saving response: {e}")
        return f"❌ Error saving response: {e}"

    return content



def generate_prompt_for_slide_titles(project_name: str) -> str:
    prompt = f"""
You are a presentation strategist.
Generate a structured slide outline for a corporate-style presentation on the following project:

Project: {project_name}

Instructions:
- Start with a title slide and an agenda.
- Divide the presentation into 3-5 major sections (e.g., Problem Statement, Solution Architecture, Features, Impact, Conclusion).
- Under each section, list 2-4 slide titles.
- Use formal language suitable for enterprise-level decks.
- Output format must be valid JSON:
{{"section_title": ["slide1", "slide2", ...], ...}}

Only output valid JSON. Do not include explanations.
"""
    return call_llm(prompt)

def slide_outline_agent(state):
    project_name = state["user_input"]
    structured_outline = generate_prompt_for_slide_titles(project_name)
    print("🔍 Raw LLM Output for Slide Outline:\n", structured_outline)

    if not structured_outline.strip():
        raise ValueError("LLM returned an empty response for slide outline generation.")

    cleaned = clean_llm_response(structured_outline)

    try:
        outline_json = json.loads(cleaned)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON from LLM:\n{cleaned}")

    return {"slide_outline": outline_json}

def generator_agent(state):
    import os, re, json

    outline = state.get("slide_outline", {})
    user_input = state.get("user_input", "")
    project_info = state.get("project_info", "")
    persona_summary = retrieve_persona_summary(user_input)

    search_prompt = f"""You are a senior business strategist and analyst.

Given:
- Project Name: "{user_input}"
- Project Information: "{project_info}"

Perform a deep-dive analysis with the following objectives:

1. Understand the Offering
2. Business Need Analysis
3. Market Contextualization
4. Sales Positioning Insight

Be concise but insightful. Cite any relevant examples. Return findings suitable for slide content.
"""
    search_results = search_assistant(user_input, search_prompt)
    print("The initial search results about the topic:- " + search_results)
    generated_slides = []
    slides_structured_json = []

    os.makedirs("generated_slides", exist_ok=True)

    for section, slides in outline.items():
        for slide_title in slides:
            prompt = f"""
You are a corporate communication expert and technical content strategist.
Your task is to generate well-structured JSON output for a PowerPoint slide.

---

### Slide Example Format (JSON):
{{
  "slide_title": "AI-Powered Support Overview",
  "section": "Solution Overview",
  "slide_type": "Solution Overview",
  "slide_content": "- 65% reduction in human support dependency\\n- 40% faster ticket resolution\\n- Multilingual query handling\\n[Image Placeholder: Support System Diagram]"
}}

---

### Inputs:

- **Slide Title**: "{slide_title}"
- **Section**: "{section}"
- **Project Context**: "{user_input}"
- **Recent Market Research**: "{search_results}"
- **Persona Insight**: "{persona_summary}"

---

### Instructions:
- Limit content to one slide.
- Use bullet points, stats, and visuals where appropriate.
- Mention `[Image Placeholder: ...]` for diagrams.
- Use professional, formal language.
- Slide type must be one of: "Title", "Problem Statement", "Solution Overview", "Insights", or a custom type if needed.

Respond ONLY with the final JSON structure.
"""

            response = call_llm(prompt)
            cleaned_response = clean_llm_response(response)

            try:
                slide_json = json.loads(cleaned_response)
            except json.JSONDecodeError:
                print(f"⚠️ Error parsing slide: {slide_title}")
                continue

            # Save individual JSON slide
            safe_title = re.sub(r'[\\/*?:"<>|]', "_", slide_title)
            slide_file_path = f"generated_slides/{safe_title.replace(' ', '_').lower()}.json"
            with open(slide_file_path, "w", encoding="utf-8") as f:
                json.dump(slide_json, f, indent=4)

            slides_structured_json.append(slide_json)

    # Save all slides to a complete file
    with open("generated_slides/complete_slides.json", "w", encoding="utf-8") as f:
        json.dump(slides_structured_json, f, indent=4)

    return {"generated_slides_json": slides_structured_json}


def reviewer_agent(state):
    slides_json = state.get("generated_slides_json", [])

    reviewed_slides = []
    for slide in slides_json:
        title = slide["slide_title"]
        content = slide["slide_content"]
        section = slide.get("section", "")
        slide_type = slide.get("slide_type", "")

        prompt = f"""
You are an enterprise-level presentation reviewer and editor.

Slide Title: {title}
Section: {section}
Slide Type: {slide_type}
Original Slide Content:
{content}

Instructions:
- Improve clarity, tone, and formatting.
- Make it concise and compelling for a business presentation.
- Maintain structure: keep bullet points, stats, and visual placeholders intact.
- Return only the revised slide content (no explanations).
"""

        improved_content = call_llm(prompt).strip()

        reviewed_slides.append({
            "slide_title": title,
            "section": section,
            "slide_type": slide_type,
            "slide_content": improved_content
        })

    # Save reviewed version
    os.makedirs("reviewed_slides", exist_ok=True)
    with open("reviewed_slides/final_output.json", "w", encoding="utf-8") as f:
        json.dump(reviewed_slides, f, indent=4)

    # Also format into markdown for compatibility if needed later
    markdown_output = "\n\n".join(
        f"# {slide['slide_title']}\n{slide['slide_content']}" for slide in reviewed_slides
    )

    return {
        "final_output": markdown_output,
        "reviewed_slides_json": reviewed_slides
    }


def chain_agent(state):
    reviewed_slides = state.get("reviewed_slides_json", [])
    total_slides = len(reviewed_slides)
    project_title = state.get("user_input", "")

    compiled_text = "\n\n".join(
        f"Slide Title: {slide['slide_title']}\nSection: {slide['section']}\nSlide Type: {slide['slide_type']}\nContent:\n{slide['slide_content']}"
        for slide in reviewed_slides
    )

    prompt = f"""
You are a senior content auditor reviewing a final business proposal presentation.

Project Title: {project_title}
Total Slides: {total_slides}

Slides:
{compiled_text}

Instructions:
- Evaluate overall tone, structure, consistency, and professional quality.
- Identify strengths and suggest areas for improvement.
- Return final comments as a structured executive summary.
"""

    feedback = call_llm(prompt).strip()
    return {"process_assessment": feedback}


def ppt_generation_pipeline(user_input, project_info):
    state = {
        "user_input": user_input,
        "project_info": project_info
    }

    # Run the agent pipeline
    state.update(slide_outline_agent(state))
    state.update(generator_agent(state))
    state.update(reviewer_agent(state))
    state.update(chain_agent(state))

    reviewed_slides_json = state.get("reviewed_slides_json", [])

    slides_structured = []
    for idx, slide in enumerate(reviewed_slides_json, start=1):
        slides_structured.append({
            "slide_number": idx,
            "slide_title": slide.get("slide_title", ""),
            "section": slide.get("section", ""),
            "slide_type": slide.get("slide_type", ""),
            "slide_content": slide.get("slide_content", "")
        })

    # Generate Markdown fallback for compatibility/use in manual review
    markdown_output = "\n\n".join(
        f"# {slide['slide_title']}\n{slide['slide_content']}" for slide in reviewed_slides_json
    )

    # Save the final structured JSON to disk (optional for record-keeping)
    os.makedirs("final_output", exist_ok=True)
    with open("final_output/structured_slides.json", "w", encoding="utf-8") as f:
        json.dump(slides_structured, f, indent=4)

    return {
        "slides": slides_structured,
        "total_slides": len(slides_structured),
        "markdown": markdown_output.strip(),
        "status": "complete",
        "assessment": state["process_assessment"]
    }

