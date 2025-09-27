# ---------- file: nodebuilder/templates/nodes/translator/node.py ----------
# Example TranslatorNode for LangGraph
from langgraph.graph import Node


class TranslatorNode(Node):
    """Demo translator that annotates text with a language code."""

    def run(self, text: str, target_lang: str = "en") -> str:
        # Replace this with a call to a translation API if you want
        return f"[{target_lang.upper()}] {text}"

