import os
import glob
import json
import uuid
from collections import Counter, defaultdict


def create_deck_level_payloads(
    metadata_dir="Metadata_dump",
    output_file="qdrant_deck_payloads.jsonl"
):
    metadata_files = glob.glob(os.path.join(metadata_dir, "*.json"))

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as out_file:
        for path in metadata_files:
            deck_name = os.path.basename(path).replace(".json", "")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # If it's a list of slides
                if isinstance(data, list):
                    slides = data
                # If it's a dict with slide-like keys
                elif isinstance(data, dict):
                    slides = [data]
                else:
                    print(f"❌ Skipping {deck_name}: Unrecognized structure.")
                    continue

                slide_data_list = []
                tone_counter = Counter()
                layout_counter = Counter()
                branding_counter = Counter()
                visual_cue_counter = Counter()

                for slide in slides:
                    slide_data_list.append({
                        "slide_number": slide.get("Slide Number"),
                        "slide_title": slide.get("Slide Title"),
                        "slide_type": slide.get("Slide Type"),
                        "slide_purpose": slide.get("Slide Purpose"),
                        "tone_of_voice": slide.get("Tone of Voice"),
                        "layout_type": slide.get("Inferred Layout Type"),
                        "language_style": slide.get("Language Style"),
                        "slide_flow_position": slide.get("Slide Flow Position"),
                        "branding_lines": slide.get("Branding or Signature Lines", []),
                        "visual_cues": slide.get("Visual Cues Mentioned", []),
                        "strategic_terms": slide.get("Key Phrases / Strategic Terms", [])
                    })

                    tone_counter[slide.get("Tone of Voice")] += 1
                    layout_counter[slide.get("Inferred Layout Type")] += 1
                    branding_counter.update(slide.get("Branding or Signature Lines", []))
                    visual_cue_counter.update(slide.get("Visual Cues Mentioned", []))

                summary = f"""
Deck Name: {deck_name}
Most Common Tones: {dict(tone_counter)}
Most Common Layouts: {dict(layout_counter)}
Visual Cues: {list(visual_cue_counter.keys())}
""".strip()

                payload = {
                    "id": str(uuid.uuid4()),
                    "deck_title": deck_name,
                    "persona_summary": summary,
                    "tone_distribution": dict(tone_counter),
                    "layout_distribution": dict(layout_counter),
                    "branding_lines": list(branding_counter.keys()),
                    "visual_cues": list(visual_cue_counter.keys()),
                    "slides": slide_data_list
                }

                out_file.write(json.dumps(payload) + "\n")
                print(f"✅ Deck-level payload added for: {deck_name}")

            except Exception as e:
                print(f"❌ Skipping {deck_name}: {e}")

    print(f"\n🎉 All deck persona payloads saved to: {output_file}")


if __name__ == "__main__":
    create_deck_level_payloads()
