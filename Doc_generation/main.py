from langgraph.graph import StateGraph, END
import json
from typing import TypedDict, List, Dict
from md_json import markdown_to_slides
from agents import (
    user_input_agent,
    slide_outline_agent,
    generator_agent,
    reviewer_agent,
    chain_agent
)

# === Define the state structure passed between agents ===
class GraphState(TypedDict, total=False):
    user_input: str
    slide_outline: Dict[str, List[str]]
    generated_slides: str
    final_output: str
    process_assessment: str
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
    workflow = build_graph()

    user_query = input("📝 Enter your project name or idea for the presentation report: ")
    project_info = input("Enter project specific information:- ")
    result = workflow.invoke({"user_input": user_query,"project_info":project_info})

    output_filename = f"{user_query.replace(' ', '_').lower()}_presentation.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(result.get("final_output", "No final output generated."))
    
    
    # Save as structured JSON
    output_filename = f"{user_query.replace(' ', '_').lower()}_presentation.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        

    print(f"\n✅ Presentation content saved to: {output_filename}")
    print(f"📊 Slides Generated: {result.get('total_slides', 0)}")
    print("\n📋 Final Assessment:")
    print(result.get("assessment", "No assessment available."))

