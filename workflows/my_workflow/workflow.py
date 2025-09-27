# Generated workflow: my_workflow
from langgraph.graph import Workflow
from nodes.summarizer.node import SummarizerNode
from nodes.translator.node import TranslatorNode


class my_workflow(Workflow):
    """Generated workflow: summarizer → translator"""

    def __init__(self):
        self.summarizer = SummarizerNode()
        self.translator = TranslatorNode()

    def run(self, text, target_lang='en') -> str:
        summary = self.summarizer.run(text)
        translated_text = self.translator.run(summary, target_lang)
        return translated_text
