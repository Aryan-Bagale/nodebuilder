# ---------- file: nodebuilder/templates/workflows/summarize_and_translate/workflow.py ----------
from langgraph.graph import Workflow
from nodes.summarizer.node import SummarizerNode
from nodes.translator.node import TranslatorNode


class SummarizeAndTranslateWorkflow(Workflow):
    """Example workflow: summarize, then translate."""

    def __init__(self):
        self.summarizer = SummarizerNode()
        self.translator = TranslatorNode()

    def run(self, text: str, target_lang: str = "en") -> str:
        summary = self.summarizer.run(text)
        return self.translator.run(summary, target_lang=target_lang)