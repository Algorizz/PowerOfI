from langgraph.graph import StateGraph, END
import json
from typing import TypedDict, List, Dict
from agents import (
    user_input_agent,
    slide_outline_agent,
    generator_agent,
    reviewer_agent,
    chain_agent
)

from typing import TypedDict, List, Dict
import json
import os

# === Define the state structure passed between agents ===
class GraphState(TypedDict, total=False):
    user_input: str
    project_info: str
    slide_outline: Dict[str, List[str]]
    generated_slides_json: List[Dict]
    reviewed_slides_json: List[Dict]
    final_output: str  # Markdown output
    process_assessment: str
    slides: List[Dict]
    status: str

# === Build the LangGraph ===
def build_graph():
    graph = StateGraph(GraphState)

    # Add agent nodes
    graph.add_node("UserInput", user_input_agent)
    graph.add_node("SlideOutline", slide_outline_agent)
    graph.add_node("Generator", generator_agent)
    graph.add_node("Reviewer", reviewer_agent)
    graph.add_node("ChainQA", chain_agent)

    # Define flow
    graph.set_entry_point("UserInput")
    graph.add_edge("UserInput", "SlideOutline")
    graph.add_edge("SlideOutline", "Generator")
    graph.add_edge("Generator", "Reviewer")
    graph.add_edge("Reviewer", "ChainQA")
    graph.add_edge("ChainQA", END)

    return graph.compile()

# === Execution Entrypoint ===
if __name__ == "__main__":
    import os
    import json
    
    workflow = build_graph()

    user_query = input("📝 Enter your project name or idea for the presentation report: ")
    project_info = input("Enter project specific information: ")

    result = workflow.invoke({
        "user_input": user_query,
        "project_info": project_info
    })

    # === Ensure output directory exists ===
    output_dir = "output_final"
    os.makedirs(output_dir, exist_ok=True)

    # === Improved filename sanitization ===
    # Remove special characters and limit length
    safe_filename = "".join(c for c in user_query if c.isalnum() or c in (' ', '-', '_')).rstrip()
    base_filename = safe_filename.replace(' ', '_').lower()[:50]  # Limit to 50 chars
    
    # Fallback if filename becomes empty
    if not base_filename:
        base_filename = "presentation"
    
    print(f"📁 Base filename: {base_filename}")  # Debug info

    # === Save Markdown output ===
    md_filename = os.path.join(output_dir, f"{base_filename}_presentation.md")
    try:
        with open(md_filename, "w", encoding="utf-8") as f:
            content = result.get("final_output", "No final output generated.")
            f.write(content)
            f.flush()  # Ensure data is written immediately
        print(f"✅ Markdown saved to: {md_filename}")
        print(f"📄 File size: {os.path.getsize(md_filename)} bytes")
    except Exception as e:
        print(f"❌ Error saving Markdown file: {e}")

    # === Save JSON slide structure ===
    json_filename = os.path.join(output_dir, f"{base_filename}_presentation.json")
    try:
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
            f.flush()  # Ensure data is written immediately
        print(f"📊 JSON slides saved to: {json_filename}")
        print(f"📄 File size: {os.path.getsize(json_filename)} bytes")
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")

    # === Debug information ===
    print(f"\n🔍 Debug Info:")
    print(f"Result keys: {list(result.keys()) if result else 'None'}")
    print(f"Final output length: {len(str(result.get('final_output', '')))}")

    # === Feedback to user ===
    print(f"\n📈 Total Slides: {result.get('total_slides', 0)}")
    print("\n🧠 Final Assessment:")
    print(result.get("assessment", "No assessment available."))
