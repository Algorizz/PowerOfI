import os
import json
import tiktoken
from azure_llm import call_llm  # Make sure this function is defined and imports your Azure LLM setup

# -----------------------------
# Tokenizer setup for GPT-4o
# -----------------------------
tokenizer = tiktoken.encoding_for_model("gpt-4o")

def num_tokens(text: str) -> int:
    return len(tokenizer.encode(text))

def split_text_into_chunks(text: str, max_tokens: int = 1500) -> list:
    lines = text.splitlines()
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for line in lines:
        line_tokens = num_tokens(line)
        if current_tokens + line_tokens > max_tokens:
            chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
            current_tokens = line_tokens
        else:
            current_chunk += line + "\n"
            current_tokens += line_tokens

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def generate_prompt(chunk_text: str) -> str:
    return f"""
You are a Head of Strategy preparing a high-stakes business pitch deck for enterprise clients.

Analyze the following text extracted from presentation slides and extract **complete metadata** in valid JSON format. Maintain full fidelity and treat this as if you're preparing for a million-dollar proposal.

### Extract the following metadata per slide:
- Slide Number
- Slide Title
- Slide Type (e.g., Title, Agenda, Insight, Problem, Solution, Chart, ROI, CTA, Thank You)
- Slide Purpose (why it exists in the pitch)
- Tone of Voice (e.g., persuasive, analytical, conversational)
- Textual Content (raw full content)
- Key Phrases / Strategic Terms
- Language Style (bullet style, voice, sentence length)
- Slide Flow Position (Beginning, Middle, End)
- Inferred Layout Type (Title + Bullet, Visual-heavy, etc.)
- Visual Cues Mentioned
- Branding or Signature Lines

Return ONLY a JSON array, one object per slide. Do NOT add any commentary.

Here is the chunk:
{chunk_text}"""

def clean_llm_response(response: str) -> str:
    """
    Removes Markdown code block wrappers from the LLM response.
    """
    response = response.strip()
    if response.startswith("```"):
        lines = response.splitlines()
        # Remove ```json or ``` and ending ```
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return response

def generate_metadata_json(input_txt_path: str, output_json_path: str) -> bool:
    # Step 1: Read full PPT text
    with open(input_txt_path, 'r', encoding='utf-8') as f:
        full_text = f.read()

    # Step 2: Split into chunks
    chunks = split_text_into_chunks(full_text)
    print(f"📦 Total Chunks Generated: {len(chunks)}")

    all_metadata = []

    # Step 3: Process each chunk
    for idx, chunk in enumerate(chunks, start=1):
        print(f"🔍 Processing chunk {idx}/{len(chunks)}...")
        prompt = generate_prompt(chunk)
        response = call_llm(prompt)
        cleaned_response = clean_llm_response(response)

        # Step 4: Attempt JSON parse
        try:
            metadata = json.loads(cleaned_response)
            if isinstance(metadata, list):
                all_metadata.extend(metadata)
            else:
                print(f"⚠️ Chunk {idx} did not return a list. Skipping.")
        except json.JSONDecodeError:
            raw_path = os.path.join(
                os.path.dirname(output_json_path),
                f"chunk_{idx}_raw.txt"
            )
            print(f"❌ JSON parsing failed for chunk {idx}. Saving raw response to: {raw_path}")
            with open(raw_path, 'w', encoding='utf-8') as f:
                f.write(response)
            continue

    # Step 5: Save Final Merged JSON
    if os.path.isdir(output_json_path):
        output_json_path = os.path.join(output_json_path, "metadata.json")

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_metadata, f, indent=4, ensure_ascii=False)

    print(f"✅ Metadata saved to {output_json_path}")
    return True

# CLI-compatible Runner
if __name__ == "__main__":
    # CHANGE THESE PATHS AS NEEDED
    txt_location = "PowerofI/Output doc/Adani Natural Resources - Proposal from Diya - The Poi - Lumina & Digital Deep Dive.txt"
    output_path = "PowerofI/Processed_dataset"  # Can be a directory or a final .json path

    success = generate_metadata_json(input_txt_path=txt_location, output_json_path=output_path)
    if success:
        print("✅ JSON generation completed.")
    else:
        print("❌ Metadata generation failed.")
