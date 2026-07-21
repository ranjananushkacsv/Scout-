"""
cli.py — interactive terminal chat for testing the RAG pipeline end-to-end.

Usage:
    python cli.py

Prerequisites:
    1. pip install -r requirements.txt
    2. ollama pull gemma4:e4b   (or whichever tag you set in config.py)
    3. python -m ingestion.build_index   (build the vector store at least once)
"""

from rag.pipeline import RAGPipeline


BANNER = """
============================================================
 Logistics RAG Assistant — local test CLI
 Type your question, or 'exit' to quit.
 Type 'sources' after any answer to see what was retrieved.
============================================================
"""


def main():
    print(BANNER)
    print("Loading pipeline (embedding model + vector store + Ollama client)...\n")
    pipeline = RAGPipeline()
    last_result = None

    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not query:
            continue
        if query.lower() in {"exit", "quit"}:
            print("Exiting.")
            break
        if query.lower() == "sources":
            if last_result is None:
                print("(No previous answer to show sources for.)\n")
                continue
            print("\nRetrieved sources for the last answer:")
            for s in last_result["sources"]:
                print(f"  - {s['source']}  (distance: {s['distance']})")
            print()
            continue

        result = pipeline.answer(query)
        last_result = result

        print(f"\nAssistant: {result['answer']}\n")


if __name__ == "__main__":
    main()
