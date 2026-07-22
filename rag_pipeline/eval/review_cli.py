"""
eval/review_cli.py — interactive human review of a run_eval.py results
file. For each query/answer pair, you mark it PASS or FAIL. On FAIL, you
pick a failure category and optionally type a corrected answer — that
correction is what becomes fine-tuning data later.

Usage:
    python -m eval.review_cli --file run_20260722_143000.jsonl

Output:
    eval/results/reviewed_<original_filename> — same records, with added:
        {
            ...,
            "verdict": "pass" | "fail",
            "failure_category": str | None,   # broken_format, wrong_tool_call, off_tone, hallucination, other
            "corrected_answer": str | None,    # only if you typed one
        }

Controls at each prompt:
    p  = pass (answer is good as-is)
    f  = fail (you'll be asked for a category, and optionally a correction)
    s  = skip (decide later, not included in fine-tuning export)
    q  = quit and save progress so far
"""

import sys
import os
import json
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

FAILURE_CATEGORIES = {
    "1": "broken_format",
    "2": "wrong_tool_call",
    "3": "off_tone",
    "4": "hallucination",
    "5": "other",
}


def load_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def save_jsonl(path, records):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def prompt_failure_category():
    print("  Failure category:")
    for key, name in FAILURE_CATEGORIES.items():
        print(f"    {key}) {name}")
    choice = input("  Choose (1-5): ").strip()
    return FAILURE_CATEGORIES.get(choice, "other")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Filename inside eval/results/ to review")
    args = parser.parse_args()

    input_path = os.path.join(RESULTS_DIR, args.file)
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        sys.exit(1)

    records = load_jsonl(input_path)
    output_path = os.path.join(RESULTS_DIR, f"reviewed_{args.file}")

    # Resume support: if a reviewed file already exists, load prior verdicts
    already_reviewed = {}
    if os.path.exists(output_path):
        prior = load_jsonl(output_path)
        already_reviewed = {r["query"]: r for r in prior if r.get("verdict")}
        print(f"Resuming — {len(already_reviewed)} queries already reviewed.\n")

    print(f"Reviewing {len(records)} queries. Controls: [p]ass  [f]ail  [s]kip  [q]uit\n")

    for i, record in enumerate(records, start=1):
        if record["query"] in already_reviewed:
            records[i - 1] = already_reviewed[record["query"]]
            continue

        print("=" * 70)
        print(f"[{i}/{len(records)}] Category: {record['category']}")
        print(f"Query:  {record['query']}")
        if record["blocked"]:
            print(f"BLOCKED (reason: {record['block_reason']})")
        else:
            print(f"Tools called: {record['tool_calls'] or 'none'}")
        print(f"Answer: {record['answer']}")

        choice = input("\n  Verdict [p/f/s/q]: ").strip().lower()

        if choice == "q":
            print("\nSaving progress and exiting.")
            save_jsonl(output_path, records[:i - 1])
            return

        if choice == "p":
            record["verdict"] = "pass"
            record["failure_category"] = None
            record["corrected_answer"] = None
        elif choice == "f":
            record["verdict"] = "fail"
            record["failure_category"] = prompt_failure_category()
            correction = input("  Corrected answer (leave blank to skip): ").strip()
            record["corrected_answer"] = correction or None
        else:  # skip or anything else
            record["verdict"] = "skipped"
            record["failure_category"] = None
            record["corrected_answer"] = None

        save_jsonl(output_path, records[:i])  # save incrementally after every item
        print()

    print(f"\nReview complete. Saved to:\n  {output_path}")
    print("Next: python -m eval.export_finetune_data --file " + os.path.basename(output_path))


if __name__ == "__main__":
    main()
