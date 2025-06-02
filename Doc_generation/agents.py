import os
import json
import re
from langchain_openai import AzureOpenAIEmbeddings
from azure_llm import call_llm, client
from qdrant_client import QdrantClient
from openai import AzureOpenAI
from langchain.embeddings.base import Embeddings
from datetime import datetime
from openai import OpenAI

# === ENVIRONMENT SETUP ===
os.environ["AZURE_OPENAI_API_KEY"] = "b46942d9305c42d78df6078a465419ae"
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-12-01-preview"
os.environ["QDRANT_API_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.ota3xr4-xFLlm4d8P42hHHPAvFFb3K-SVPnSUx7ZRrE"
os.environ["PERPLEXITY_API_KEY"] = "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"

# Initializing Perplexity-compatible client
client = OpenAI(
    api_key=os.getenv("PERPLEXITY_API_KEY"),  # Store in .env or config.py
    base_url="https://api.perplexity.ai"
)

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
    return text

# === AGENTS ===
def user_input_agent(state):
    return {"user_input": state.get("user_input", "")}

def search_assistant(user_input:str,prompt:str) -> str:
    # === Step 1: Save input to Markdown ===
    os.makedirs("search_info", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join("search_info", f"{user_input}_{timestamp}.md")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# Project: {user_input}\n\n")
        f.write(f"## Search Query:\n{prompt}\n\n")

    # === Step 2: Call Perplexity API ===
    messages = [
        {
            "role": "system",
            "content": (
                "You are a research assistant. Search the web, analyze trends, "
                "and deliver helpful insights relevant to the user's query."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        response = client.chat.completions.create(
            model="sonar",
            messages=messages
        )
        content = response.choices[0].message.content
    except Exception as e:
        content = f"❌ Error while searching: {e}"

    # === Step 3: Append result to the same .md file ===
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"## Perplexity Response:\n{content}")

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
    outline = state.get("slide_outline", {})
    user_input = state.get("user_input", "")
    project_info = state.get("project_info","")
    persona_summary = retrieve_persona_summary(user_input)
    search_prompt = f"""You are a senior business strategist and analyst.

Given:
- Project Name: "{user_input}"
- Project Information: "{project_info}"

Perform a deep-dive analysis with the following objectives:

---

1. **Understand the Offering**
   - Briefly summarize what this project is about in business terms.
   - Identify the core technology/service/product being offered.

2. **Business Need Analysis**
   - Identify the key reasons why a mid-to-large enterprise might require this solution.
   - List possible pain points, inefficiencies, or strategic objectives this solution addresses.
   - Highlight any specific departments, industries, or operational areas where this could bring significant impact.

3. **Market Contextualization**
   - Search and cite any recent news, industry trends, regulatory changes, or market shifts that support the need for this solution.
   - Mention examples of companies, deals, or industry movements that reinforce the business value of this offering.

4. **Sales Positioning Insight**
   - Construct a compelling value proposition using the identified needs and market signals.
   - Include persuasive language and argumentation that can be used in a high-stakes enterprise pitch.
   - Frame this in a format suitable to feed into a slide deck or a pitch presentation.

Be concise but insightful. Use industry language where appropriate.

"""
    search_results = search_assistant(user_input,search_prompt)
    generated_slides = []

    os.makedirs("generated_slides", exist_ok=True)

    for section, slides in outline.items():
        for slide_title in slides:
            prompt = f"""
You are a corporate communication expert and technical content writer.
Generate the content for a PowerPoint slide titled "{slide_title}" in the section "{section}".

Project Context: {user_input}
Recent market research about the topic and the company : {search_results}
Additional Persona Insight: {persona_summary}

Instructions:
- Limit content to what would appear on a single slide.
- Include bullet points, stats, or visuals where appropriate.
- Mention placeholder text for diagrams or images if needed (e.g., [Image Placeholder: System Diagram]).
- Use professional, formal language.

Output:
Slide Title: {slide_title}
Slide Content:
Slide Type[from these Title,Problem Statement,Solution Overview, Insights if any other include that too]:  
"""
            content = call_llm(prompt)

            # === Sanitize filename ===
            safe_title = re.sub(r'[\\/*?:"<>|]', "_", slide_title)
            slide_file = f"generated_slides/{safe_title.replace(' ', '_').lower()}.txt"

            with open(slide_file, "w", encoding="utf-8") as f:
                f.write(content.strip())

            generated_slides.append(f"# {slide_title}\n{content.strip()}\n")

    return {"generated_slides": "\n".join(generated_slides)}

def reviewer_agent(state):
    slides_text = state["generated_slides"]
    lines = slides_text.splitlines()
    slide_chunks = []
    current_chunk = []

    for line in lines:
        if line.startswith("# "):
            if current_chunk:
                slide_chunks.append("\n".join(current_chunk))
            current_chunk = [line]
        else:
            current_chunk.append(line)
    if current_chunk:
        slide_chunks.append("\n".join(current_chunk))

    reviewed_slides = []
    for chunk in slide_chunks:
        if not chunk.strip():
            continue
        try:
            title_line, content = chunk.strip().split("\n", 1)
        except ValueError:
            continue
        title = title_line.lstrip("# ").strip()
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

def ppt_generation_pipeline(user_input, project_info):
    state = {"user_input": user_input, "project_info": project_info}
    state.update(slide_outline_agent(state))
    state.update(generator_agent(state))
    state.update(reviewer_agent(state))
    state.update(chain_agent(state))

    final_md = state["final_output"]
    lines = final_md.splitlines()
    slide_chunks = []
    current_chunk = []

    for line in lines:
        if line.startswith("# "):  # New slide
            if current_chunk:
                slide_chunks.append("\n".join(current_chunk))
            current_chunk = [line]
        else:
            current_chunk.append(line)
    if current_chunk:
        slide_chunks.append("\n".join(current_chunk))

    slides_structured = []
    for idx, chunk in enumerate(slide_chunks, start=1):
        if not chunk.strip():
            continue
        try:
            title_line, content = chunk.strip().split("\n", 1)
            title = title_line.lstrip("# ").strip()
            slides_structured.append({
                "slide_number": idx,
                "slide_title": title,
                "slide_content": content.strip()
            })
        except ValueError:
            # If content is missing or malformed
            slides_structured.append({
                "slide_number": idx,
                "slide_title": title_line.lstrip("# ").strip(),
                "slide_content": ""
            })

    return {
        "slides": slides_structured,
        "total_slides": len(slides_structured),
        "markdown": final_md.strip(),
        "status": "complete",
        "assessment": state["process_assessment"]
    }

