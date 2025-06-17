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



def generate_prompt_for_slide_titles(project_name: str,project_context: str) -> str:
    prompt =f"""
You are a seasoned leadership strategist and presentation designer, known for your ability to connect deeply with senior teams, articulate complexity with warmth and clarity, and design narratives that feel more *human* than *corporate*. You’ve been in real leadership rooms. You know how to speak to hearts and minds. You never hide behind jargon.

Your task is to create a clear, structured outline for a corporate-style business presentation — but with emotional intelligence, storytelling sensitivity, and a grounded sense of purpose.

**Context:**  
- Project Title: {project_name}  
- Project Context: {project_context}

**Guidelines:**  
- Begin with a **Title Slide** and **Agenda Slide**.  
- Then organize the deck into **3 to 5 meaningful sections** that typically include:
  - Problem or Opportunity
  - Goals or Strategic Vision
  - Proposed Solution / Intervention Approach
  - Key Features or Differentiators
  - Human and Business Impact
  - Roadmap or Next Steps

- For each section, write **2 to 4 slide titles** that reflect a natural, thoughtful, and empathetic flow — the kind a seasoned coach or leadership partner would use in conversation.

- Use emotionally intelligent, grounded language. Prioritize clarity over buzzwords. Think *trusted advisor*, not *consultant-speak*.
- Infuse a warm, real voice: one that signals “We get you. We’ve been there. Let’s figure this out together.”
- Only include the project name in slide titles if absolutely necessary for clarity.

**Output Format:**  
Return your output as a single, valid JSON dictionary like the one below — with no extra commentary.

```json
{{
  "Section Title 1": ["Slide Title A1", "Slide Title A2", ...],
  "Section Title 2": ["Slide Title B1", "Slide Title B2", ...],
  ...
}}

"""
    return call_llm(prompt)

def slide_outline_agent(state):
    project_name = state["user_input"]
    project_context = state["project_info"]
    structured_outline = generate_prompt_for_slide_titles(project_name,project_context)
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
    import os, re, json, unicodedata

    def sanitize_filename(name):
        # Normalize and remove accents, replace illegal characters
        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
        name = re.sub(r'[\\/*?:"<>|()\n]', "_", name)
        return name.strip().lower().replace(" ", "_")

    outline = state.get("slide_outline", {})
    user_input = state.get("user_input", "")
    project_info = state.get("project_info", "")
    persona_summary = retrieve_persona_summary(user_input)

    # Prepare sanitized path
    safe_user_input = sanitize_filename(user_input)
    output_folder = os.path.join("generated_slides", safe_user_input)
    os.makedirs(output_folder, exist_ok=True)

    # Run search
    search_prompt = f"""
You are a senior business strategist and research analyst with deep expertise in competitive intelligence, enterprise transformation, and sales enablement. You have been tasked with preparing **foundational research** for a proposal aimed at solving a critical business challenge for the recipient company.

This research will be used to create a high-stakes strategic presentation or proposal — therefore, your output must go **beyond listing insights**. It should **diagnose underlying causes**, **justify the need for intervention**, and **highlight industry context or urgency**.

---

### 📘 Project Brief:
- **Project Name**: {user_input}
- **Detailed Description**: {project_info}

---

### 🎯 Research Objectives:
You are expected to conduct a **deep-dive business and market analysis**, synthesizing data and insights into an **executive-ready narrative** that serves as a strategic rationale for the proposed solution.

Your research output must cover the following 4 pillars:

---

#### 1. 📦 Offering Analysis
- Clearly articulate **what is being offered** (product, service, platform, etc.).
- Break it down into key components, features, and enablers (e.g., technology, partnerships, capabilities).
- Highlight its **competitive advantage** or **unique positioning**.
- Include **why this specific offering matters now**.

---

#### 2. 🔥 Business Need & Pain Point Diagnosis
- Identify and explain the **underlying problems**, **inefficiencies**, or **missed opportunities** faced by the recipient.
- Go beyond symptoms — analyze **root causes** (e.g., operational gaps, market disruptions, regulatory pressure, talent shortages).
- Emphasize **why the recipient company needs this solution now**.
- Suggest **consequences of inaction** and potential recovery paths.

---

#### 3. 🌍 Market Contextualization & Benchmarking
- Explore relevant **industry trends**, **shifts in customer behavior**, or **technology disruption** that shape the current landscape.
- Provide **real-world examples**, **competitor moves**, or **peer benchmarks**.
- Include recent events (e.g., post-pandemic shifts, economic indicators, ESG compliance pressures) that validate the need for transformation.

---

#### 4. 🧩 Sales & Strategic Positioning Insight
- Recommend how this offering can be **strategically positioned** to the recipient’s leadership or decision-makers.
- Suggest the right **value narrative** (e.g., ROI, risk mitigation, speed, innovation).
- Highlight **ideal entry points** (e.g., CFO for cost-cutting, CHRO for talent retention, CTO for digitization).
- Include **3-5 executive-ready talking points** that summarize how this offering solves the recipient’s challenges.

---

### 📝 Output Format:
- Use professional, structured sections with clear headers.
- Be direct, specific, and **insight-driven** — not speculative or generic.
- Use bullet points where appropriate, but keep the overall tone analytical and authoritative.
- Bold key phrases. Use statistics, examples, and third-party validation where helpful.

---

📌 This content will be used to build proposal decks, decision memos, and investment justifications. Avoid fluff. Make the business case **clear, urgent, and credible**.
"""  # Your real prompt
    search_results = search_assistant(user_input, search_prompt)
    print("Search Results:\n", search_results)

    slides_structured_json = []
    previous_slide_contents = []

    for section, slides in outline.items():
        for slide_title in slides:
            safe_title = sanitize_filename(slide_title)
            slide_file_path = os.path.join(output_folder, f"{safe_title}.json")
            previous_context = "\n\n".join(previous_slide_contents) if previous_slide_contents else "None yet"

            # Skip if cached
            if os.path.exists(slide_file_path):
                print(f"Cached: {slide_title}")
                with open(slide_file_path, "r", encoding="utf-8") as f:
                    slide_json = json.load(f)
                slides_structured_json.append(slide_json)
                if "slide_content" in slide_json:
                    previous_slide_contents.append(slide_json["slide_content"])
                continue

            print(f"Generating slide: {slide_title}")
            attempt = 0
            max_attempts = 3

            while attempt < max_attempts:
                # Generation prompt
                prompt = f"""
You are an expert in high-end corporate storytelling, business strategy, and visual communication. Your task is to generate a **premium-quality PowerPoint slide** that blends narrative depth, visual appeal, and strategic relevance — tailored for C-suite or board-level presentations.

This is a **stateless API call**. Use only the inputs provided — do not invent facts, add filler, or hallucinate content.

---

### 🎯 Your Task:
Generate a **single slide's content** in rich, structured **JSON format**. The slide must reflect world-class consulting, branding, and business development standards.
### Important guideline :- generate only 20 slides not more than that to make it crisp 
---

### 💡 Output Requirements

Each slide must include:

- `"slide_title"` (string): A clear, specific title that reflects the content’s core idea.
- `"section"` (string): The broader section this slide belongs to (e.g., Insights, Methodology, Solution).
- `"slide_type"` (string): One of the strictly allowed types below.
- `"slide_content"` (string): The main body of the slide. This must be **designed like a real high-end slide**, not just bullet points. Use a **mix of:**
  - **Mini-paragraphs** (2-4 sentences) that describe context, logic, or impact.
  - **Labeled sections or subheadings**, e.g., `“Key Insight”`, `“Business Impact”`, `“Customer Perspective”`.
  - **2-4 concise bullet points** for takeaways, stats, frameworks, or enablers.
  - **[Image Placeholder: ...]** clearly marked where a graphic or diagram is essential.
 - `"image_prompt"` (string): A **concise, design-ready visual brief** that describes the ideal graphic element to accompany the slide — such as a high-resolution infographic, clean data visualization, minimalist flowchart, or conceptual illustration.

---


### 📥 Input Parameters:
- **Slide Title**: "{slide_title}"
- **Section**: "{section}"
- **Project Context**: "{user_input}" — A summary of the initiative or business objective.
- **Recent Market Research**: "{search_results}" — Data, benchmarks, or insights that must inform the content.
- **Persona Insight**: "{persona_summary}" — Communication tone and priorities for this executive audience.
- **Previous Slide Context**: "{previous_context}" — A list of recent slide content to avoid duplication and maintain flow.

---

### 🧭 Slide Types Allowed (use only these exact labels):
- `"title"` — Deck opener with project title, date, and agenda (**only once**).
- `"insights"` — Market context, customer need, or business challenge (**max 3 in a row**).
- `"methodology"` — Your step-by-step approach or execution logic.
- `"flowchart"` — Linear or cyclical process explained in steps (**must include paragraph + flow breakdown**).
- `"methodology with infographics"` — A structured model, framework, or pyramid with visual logic.
- `"flowchart with infographics"` — Process map with layers of detail (e.g., phases, actors, outcomes).
- `"solution"` — Proposal of actions, services, or decisions to be made.
- `"conclusion"` — Wrap-up and next steps (**must be last**).

---

### ✅ Design & Content Expectations

1. **Narrative-Driven Layout**
   - Use **short, vivid paragraphs** to explain logic and value clearly.
   - Avoid robotic tone or generic filler — speak like a smart, empathetic strategist.
   - Add **labels or subheads** to guide the reader’s attention (e.g., “Strategic Insight”, “Cultural Shift”).

2. **Information Density + Beauty**
   - Balance text and visuals. Use **infographics, process flows, and data visuals**.
   - Keep slides tight — not overloaded — but don’t leave them empty.
   - Each slide must **stand alone** and convey a meaningful, strategic insight.

3. **Data, Differentiators, and Depth**
   - Pull **2+ data-backed points** directly from `Recent Market Research` where possible.
   - Use relevant benchmarks, strategic levers, or behaviors seen in high-performing companies.
   - Highlight **Abbott-specific** tensions or opportunities based on provided context.

4. **Flowchart-Specific Rules**
   - When `slide_type` is `"flowchart"` or `"flowchart with infographics"`:
     - Begin with a concise intro paragraph that explains the journey or model.
     - Clearly list **each step** with a label and 1-line purpose.

### ✅ Design Guidelines:

1. **Keep Visuals Light on Text**:
   - Do **not generate image prompts that rely heavily on embedded text**.
   - If text is required (e.g., for labels or headings), **limit to 3-5 short words** and ensure it is **large, legible, and clearly positioned**.
   - Always prefer **symbolic visuals**, **icons**, **shapes**, or **flows** over text-heavy diagrams.

2. **Purpose-Driven Visuals Only**:
   - Insert `[Image Placeholder: ...]` only when a visual meaningfully enhances understanding, persuasion, or executive clarity.
   - Avoid purely decorative elements or visuals that repeat textual slide content.

3. **Allowed Slide Types**:
   - Only generate image prompts for the following slide types:
     - `"title"`
     - `"insights"`
     - `"methodology"`
   - For all other slide types, set `"image_prompt": ""`.

4. **Prompt Precision & Style**:
   - Describe structure, orientation, layout, and intent.
   - Specify visual metaphors, layout (e.g., circular, grid, linear), icon use, flow direction, and style (e.g., "modern", "tech-savvy", "executive-level").
   - Mention color palettes only if relevant to brand or contrast (e.g., “corporate blue and gray”).

5. **Example Prompts**:
   - ✅ Good: `"A minimalist horizontal flowchart with 4 labeled steps (Discover, Design, Test, Launch), using arrows and icons, clean white background, subtle gradients, C-level aesthetic."`
   - ✅ Good: `"A radar chart comparing 5 enterprise capabilities, using soft blue hues and no internal text — axis labels only."`
   - ❌ Bad: `"A diagram with 7 paragraphs explaining the full framework"` → Too text-heavy
   - ❌ Bad: `"A chart showing lots of labels and KPIs in small text"` → Cluttered and unreadable

---

**⛔️ Avoid:**
- Dense visuals with paragraphs or blocks of text
- Generic prompts like “a nice diagram”
- Any visual where more than 20% of the area is occupied by small text

---
6. **Avoid Repetition**
   - Reference `Previous Slide Context` to **avoid repeating concepts or structures**.
   - Ensure **every slide adds something new** to the strategic arc or storyline.

---

### 🔍 Advanced Logic Enhancements

For the best possible output and to maintain your writing style:

- **Preserve executive tone**: Write like a McKinsey, BCG, or Deloitte partner. Intelligent, structured, purposeful.
- **Frame strategic tensions**: When possible, show the contrast between current reality and desired future state (especially in transformation slides).
- **Map behavior to business**: When addressing culture, always connect behaviors (e.g., silos, risk-aversion) to business outcomes (e.g., missed growth, slow execution).
- **Highlight leadership dynamics**: For Neil George and team, emphasize dynamics of trust, change resistance, and credibility-building.
- **Use framing questions**: Occasionally guide reflection subtly (e.g., “How might the leadership team…?”) when insight needs nudging.
- **Respect flow sequence**: Build on prior logic and escalate toward decision, not repetition.
- **Include pre-/post-work if relevant**: For workshop planning slides, clarify touchpoints before/after main event to create continuity.

⚠️ Critical Compliance Rule: If the following guideline is not followed, the slide will be rejected from the proposal pipeline.-[ Only generate image prompts for the following slide types:
     - `"title"`
     - `"insights"`
     - `"methodology"`
   - For all other slide types, set `"image_prompt": ""`.]
---
### 🧾 Output Format (must return valid JSON only):

```json
{{
  "slide_title": "Title of the Slide",
  "section": "Methodology",
  "slide_type": "flowchart with infographics",
  "slide_content": "To ensure scalable implementation, we propose a 4-stage transformation journey.\\n\\n**Stage 1: Discover** – Assess the current landscape and identify pain points.\\n**Stage 2: Co-Design** – Collaboratively develop tailored interventions.\\n**Stage 3: Pilot** – Test in controlled environments.\\n**Stage 4: Scale & Sustain** – Expand across the organization with feedback loops.\\n\\n[Image Placeholder: Flowchart with 4 phases arranged horizontally: Discover, Co-Design, Pilot, Scale]",
  "image_prompt": "Horizontal flowchart with 4 labeled phases and icons: Discover, Co-Design, Pilot, Scale & Sustain"
}}

"""  # Insert full prompt as needed
                response = call_llm(prompt)
                cleaned_response = clean_llm_response(response)

                try:
                    slide_json = json.loads(cleaned_response)
                except json.JSONDecodeError:
                    print(f"❌ JSON Decode Error on attempt {attempt+1} for: {slide_title}")
                    attempt += 1
                    continue

                # Review prompt
                review_prompt = f"""
You are a content quality reviewer. Review this slide for business presentation standards. Respond ONLY with 'PASS' or 'FAIL'.

Slide Title: {slide_json.get("slide_title", "")}
Section: {slide_json.get("section", "")}
Type: {slide_json.get("slide_type", "")}
Content:
{slide_json.get("slide_content", "")}
                """.strip()

                review_decision = call_llm(review_prompt).strip().upper()

                if "PASS" in review_decision:
                    print(f"✅ Slide approved: {slide_title}")
                    break
                else:
                    print(f"❌ Slide rejected on attempt {attempt+1}: {slide_title}")
                    attempt += 1

            if attempt == max_attempts:
                print(f"⚠️ Failed to generate valid slide after {max_attempts} attempts: {slide_title}")
                continue

            # Save approved slide
            with open(slide_file_path, "w", encoding="utf-8") as f:
                json.dump(slide_json, f, indent=4)

            slides_structured_json.append(slide_json)
            previous_slide_contents.append(slide_json.get("slide_content", ""))

    # Save all slides as a backup
    with open("generated_slides/complete_slides.json", "w", encoding="utf-8") as f:
        json.dump(slides_structured_json, f, indent=4)

    return {
        "generated_slides_json": slides_structured_json,
        "search_reference": search_results,
        "persona_reference": persona_summary
    }

#def an agent for 

def reviewer_agent(state):
    slides_json = state.get("generated_slides_json", [])

    reviewed_slides = []
    for slide in slides_json:
        title = slide["slide_title"]
        content = slide["slide_content"]
        section = slide.get("section", "")
        slide_type = slide.get("slide_type", "")
        image_prompt = slide.get("image_prompt","")
        
        prompt =  f"""
You are a senior presentation strategist and executive editor specializing in high-impact enterprise communication. Your task is to **refine and elevate a PowerPoint slide’s written content** to meet **C-suite boardroom standards**.

---

### Slide Metadata
- **Slide Title**: {title}
- **Section**: {section}
- **Slide Type**: {slide_type}

---

### Original Slide Content:
{content}

---

### 🔧 Editing Instructions:
- **Sharpen clarity, structure, and business tone**. Rephrase wherever needed for flow and authority.
- Make the content feel like it belongs in a **McKinsey, BCG, or Fortune 100 board deck**.
- Maintain all intended structure:
  - Bullet points,
  - Markdown subheadings (e.g., `**Executive Insight**`),
  - Data points,
  - `[Image Placeholder: ...]` blocks.
- Preserve or enhance logical flow from introduction to conclusion.
- If text feels shallow or generic, **tighten it** or make it **more specific and action-oriented**.
- Avoid excessive wordiness — be dense with meaning, not with words.

---

### 📤 Output:
Return only the **fully revised `slide_content`** string. Do not include explanations, justifications, or formatting comments.
"""
        improved_content = call_llm(prompt).strip()

        reviewed_slides.append({
            "slide_title": title,
            "section": section,
            "slide_type": slide_type,
            "slide_content": improved_content,
            "image_prompt" : image_prompt 
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
You are a senior enterprise-grade presentation strategist and executive editor.

Project Title: {project_title}  
Total Slides: {total_slides}  

---

Slides:  
{compiled_text}

---

🎯 Your Role:
- Carefully review and **rewrite each slide’s content** to meet the standards of a **C-suite or boardroom presentation**.
- Ensure every slide delivers **maximum insight**, **strategic clarity**, and is **self-sufficient** in value.

---

🔧 Guidelines:
- Keep all structural elements **intact**:
  - Slide titles
  - Section headers (e.g., **Customer Pain Point**, **Strategic Levers**)
  - Bullet points
  - Image placeholders like `[Image Placeholder: ...]`

- Refine language for:
  - Executive tone
  - Logical flow
  - Precision and clarity
  - Impactful phrasing and business polish

- If any content is weak, vague, or redundant, **strengthen it** or **reframe it with actionable insights or stronger articulation**.

---

🧾 Output:
Return the **fully revised `compiled_text`** with each slide updated.  
Do not include any explanations, extra commentary, or formatting notes.
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
            "slide_content": slide.get("slide_content", ""),
            "image_prompt" : slide.get("image_prompt", "")
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

