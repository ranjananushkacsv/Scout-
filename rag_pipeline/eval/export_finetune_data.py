"""
eval/export_finetune_data.py — converts a reviewed results file into a
fine-tuning dataset in Gemma chat format, ready to hand to Unsloth/PEFT.

What gets included:
    - "pass" verdicts -> used as-is (query, answer) — reinforces good
      behavior that's already happening.
    - "fail" verdicts WITH a corrected_answer -> used as (query,
      corrected_answer) — teaches the model what it SHOULD have said.
    - "fail" verdicts WITHOUT a correction -> excluded (nothing to teach
      from an example with no known right answer).
    - "skipped" -> excluded.

Usage:
    python -m eval.export_finetune_data --file reviewed_run_20260722_143000.jsonl

Output:
    eval/results/finetune_dataset.jsonl — one JSON object per line:
        {"messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]}
    This is the standard chat-format expected by most QLoRA fine-tuning
    scripts (Unsloth, TRL SFTTrainer, etc.) — you can point your Colab
    notebook's dataset loader directly at this file.
"""

import sys
import os
import json
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

# Keep this in sync with agent/graph.py's AGENT_SYSTEM_PROMPT — the
# fine-tuned model should be trained under the same system prompt it will
# actually run with in production.
try:
    from agent.graph import AGENT_SYSTEM_PROMPT
except Exception:
    AGENT_SYSTEM_PROMPT = (
        "You are a logistics and warehousing operations assistant with access to tools."
    )


def load_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def build_training_examples(records):
    examples = []
    skipped_no_correction = 0

    for r in records:
        verdict = r.get("verdict")

        if verdict == "pass":
            answer = r["answer"]
        elif verdict == "fail" and r.get("corrected_answer"):
            answer = r["corrected_answer"]
        elif verdict == "fail":
            skipped_no_correction += 1
            continue
        else:
            continue  # skipped or unreviewed

        examples.append({
            "messages": [
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": r["query"]},
                {"role": "assistant", "content": answer},
            ]
        })

    return examples, skipped_no_correction


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Reviewed filename inside eval/results/")
    parser.add_argument("--out", default="finetune_dataset.jsonl", help="Output filename inside eval/results/")
    args = parser.parse_args()

    input_path = os.path.join(RESULTS_DIR, args.file)
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        sys.exit(1)

    records = load_jsonl(input_path)
    examples, skipped = build_training_examples(records)

    output_path = os.path.join(RESULTS_DIR, args.out)
    with open(output_path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"Exported {len(examples)} training examples to:\n  {output_path}")
    if skipped:
        print(f"Skipped {skipped} 'fail' records with no correction typed in — "
              f"go back and add corrections in review_cli.py if you want them included.")

    if len(examples) < 50:
        print(f"\nNote: {len(examples)} examples is on the low side for fine-tuning — "
              f"aim for 100+ before running a training pass. Keep running eval "
              f"cycles against more realistic queries to build this up.")


if __name__ == "__main__":
    main()
