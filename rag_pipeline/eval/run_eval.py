"""
eval/run_eval.py — runs the full pipeline (GuardrailedAgent = input
guardrails -> agent [RAG + tools] -> output guardrails) against every
query in test_queries.py, and logs the raw results.

This step does NOT judge quality — it just captures what the system
actually did, so you can review it afterward. Review happens in
eval/review_cli.py.

Usage:
    python -m eval.run_eval

Prerequisites:
    ollama serve (running)
    python -m ingestion.build_index (vector store built)

Output:
    eval/results/run_<timestamp>.jsonl — one JSON object per query:
        {
            "query": str,
            "category": str,
            "answer": str,
            "blocked": bool,
            "block_reason": str|None,
            "tool_calls": [str, ...],     # names of tools called, if any
            "pii_redacted": bool,
            "grounding_ok": bool,
        }
"""

import sys
import os
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import AIMessage

from guardrails.pipeline import GuardrailedAgent
from eval.test_queries import TEST_QUERIES

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def extract_tool_calls(tool_activity):
    names = []
    for m in tool_activity:
        if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
            for tc in m.tool_calls:
                names.append(tc["name"])
    return names


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    run_id = time.strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(RESULTS_DIR, f"run_{run_id}.jsonl")

    print(f"Building guardrailed agent...")
    agent = GuardrailedAgent()

    print(f"Running {len(TEST_QUERIES)} queries. Logging to {output_path}\n")

    with open(output_path, "w", encoding="utf-8") as f:
        for i, item in enumerate(TEST_QUERIES, start=1):
            query = item["query"]
            category = item["category"]
            print(f"[{i}/{len(TEST_QUERIES)}] ({category}) {query}")

            result = agent.ask(query)

            record = {
                "query": query,
                "category": category,
                "answer": result["answer"],
                "blocked": result["blocked"],
                "block_reason": result["block_reason"],
                "tool_calls": extract_tool_calls(result.get("tool_activity", [])),
                "pii_redacted": result["pii_redacted"],
                "grounding_ok": result["grounding_ok"],
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()

            print(f"    -> {record['answer'][:100]}{'...' if len(record['answer']) > 100 else ''}\n")

    print(f"\nDone. {len(TEST_QUERIES)} results logged to:\n  {output_path}")
    print("Next: python -m eval.review_cli --file " + os.path.basename(output_path))


if __name__ == "__main__":
    main()
