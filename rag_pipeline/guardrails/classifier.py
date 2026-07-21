"""
guardrails/classifier.py — a small, separate LLM call whose only job is to
judge whether a query is in-scope (logistics/warehousing/supply chain) or
not. Kept independent from the main agent call so topic gating doesn't
rely on the agent choosing to follow its own system prompt — it's an
external check the query has to pass before the agent ever sees it.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.generator import OllamaGenerator

CLASSIFIER_SYSTEM_PROMPT = """You are a strict topic and task-type classifier for a logistics support assistant.

The assistant's job is operational assistance: looking up inventory, shipment
status, rates, and explaining logistics/warehousing policies and procedures.

Classify the message as RELEVANT only if it is a genuine operational
question or request within that scope.

Classify as OFF_TOPIC if it is:
- Unrelated to logistics/warehousing/supply chain entirely, OR
- A creative-writing request (poem, song, story, joke, script, etc.) —
  even if the subject matter is inventory, logistics, or warehouses. A
  poem ABOUT logistics is still creative writing, not an operational
  request, and is OFF_TOPIC.
- A request for code, translation, general knowledge, or any task outside
  operational logistics support.

Small talk/greetings directed at the support bot ("hi", "are you working")
are RELEVANT.

Respond with EXACTLY one word: RELEVANT or OFF_TOPIC.
Do not explain your answer. Do not add punctuation."""


class TopicClassifier:
    def __init__(self, generator=None):
        self.generator = generator or OllamaGenerator()

    def is_relevant(self, query):
        """
        Returns True if the query is in-scope, False otherwise.
        Fails open (treats as relevant) if the classifier call errors out,
        so a transient Ollama issue doesn't block legitimate queries —
        adjust this default if you'd rather fail closed for your use case.
        """
        try:
            response = self.generator.generate(
                system_prompt=CLASSIFIER_SYSTEM_PROMPT,
                user_message=query,
                temperature=0.0,
            )
        except Exception as e:
            print(f"  [guardrail warning] Topic classifier call failed, defaulting to allow: {e}")
            return True

        verdict = response.strip().upper()
        return "OFF_TOPIC" not in verdict
