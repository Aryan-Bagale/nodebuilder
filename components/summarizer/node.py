# ---------- file: nodebuilder/templates/nodes/summarizer/node.py ----------
# Example SummarizerNode for LangGraph
from langgraph.graph import Node


class SummarizerNode(Node):
    """Simple demo summarizer that truncates text to 200 characters."""

    def run(self, text: str) -> str:
        # Replace this with a real LLM summarizer when you want
        return text[:200]