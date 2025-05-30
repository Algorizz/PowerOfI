import os
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain.chains import RetrievalQA
from azure_llm import call_llm, client
import json

# === ENVIRONMENT SETUP ===
os.environ["AZURE_OPENAI_API_KEY"] = "b46942d9305c42d78df6078a465419ae"  # ✅ Replace with your actual Azure OpenAI API key
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-12-01-preview"

# === AZURE EMBEDDING SETUP ===
embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-small",  # Azure deployment name
    azure_endpoint="https://qrizz-us.openai.azure.com",  # ✅ Updated to use azure_endpoint
    openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"]
)

# === VECTOR STORE ===
vectordb = Chroma(
    persist_directory="New fgenerator\SDD generator\chrome_db_txt",
    embedding_function=embeddings
)
retriever = vectordb.as_retriever(search_kwargs={"k": 5})

# === AGENTS ===
# === USER INPUT AGENT ===
def user_input_agent(state):
    return {"user_input": state.get("user_input", "")}


# === GENERATE PROMPT FOR SLIDE TITLES ===
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


# === SLIDE OUTLINE AGENT ===
def slide_outline_agent(state):
    project_name = state["user_input"]
    structured_outline = generate_prompt_for_slide_titles(project_name)

    print("🔍 Raw LLM Output for Slide Outline:\n", structured_outline)

    if not structured_outline.strip():
        raise ValueError("LLM returned an empty response for slide outline generation.")

    try:
        outline_json = json.loads(structured_outline)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON from LLM:\n{structured_outline}")

    return {"slide_outline": outline_json}


# === SLIDE GENERATOR AGENT ===
def generator_agent(state):
    outline = state.get("slide_outline", {})
    user_input = state.get("user_input", "")
    generated_slides = []
    os.makedirs("generated_slides", exist_ok=True)

    for section, slides in outline.items():
        for slide_title in slides:
            prompt = f"""
You are a corporate communication expert and technical content writer.
Generate the content for a PowerPoint slide titled "{slide_title}" in the section "{section}".

Project Context: {user_input}

Instructions:
- Limit content to what would appear on a single slide.
- Include bullet points, stats, or visuals where appropriate.
- Mention placeholder text for diagrams or images if needed (e.g., [Image Placeholder: System Diagram]).
- Use professional, formal language.

Output:
Slide Title: {slide_title}
Slide Content:
"""
            content = call_llm(prompt)
            slide_file = f"generated_slides/{slide_title.replace(' ', '_').lower()}.txt"
            with open(slide_file, "w", encoding="utf-8") as f:
                f.write(content.strip())
            generated_slides.append(f"# {slide_title}\n{content.strip()}\n")

    return {"generated_slides": "\n".join(generated_slides)}


# === SLIDE REVIEWER AGENT ===
def reviewer_agent(state):
    slides = state["generated_slides"].split("# ")
    reviewed_slides = []

    for s in slides:
        if not s.strip():
            continue
        title, content = s.split("\n", 1)
        prompt = f"""
You are an enterprise-level presentation reviewer. Refine the following slide content for accuracy, structure, and impact.

Slide Title: {title}
Slide Content:
{content}

Instructions:
- Improve clarity, formatting, and tone.
- Make it suitable for a business audience.
- Return only improved slide content.
"""
        improved = call_llm(prompt)
        reviewed_slides.append(f"# {title}\n{improved.strip()}\n")

    return {"final_output": "\n".join(reviewed_slides)}


# === CHAIN QUALITY ASSESSMENT AGENT ===
def chain_agent(state):
    prompt = f"""
Evaluate the final presentation:
- Project: {state['user_input']}
- Total Slides: {len(state.get('final_output', '').split('# ')) - 1}
- Assess quality, consistency, slide tone, and structure.

Provide final feedback and highlight any improvement suggestions.
"""
    result = call_llm(prompt)
    return {"process_assessment": result}


# === PIPELINE FUNCTION ===
def ppt_generation_pipeline(user_input):
    state = {"user_input": user_input}
    state.update(slide_outline_agent(state))
    state.update(generator_agent(state))
    state.update(reviewer_agent(state))
    state.update(chain_agent(state))

    return {
        "output": state["final_output"],
        "status": "complete",
        "assessment": state["process_assessment"]
    }
