"""
agent_cli.py — interactive terminal chat for testing the full agentic
pipeline (RAG + live-data tools) end to end.

Usage:
    python agent_cli.py

Prerequisites:
    pip install -r requirements.txt
    ollama pull gemma4:e4b
    python -m ingestion.build_index   (if you haven't built the vector store yet)
"""

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

from agent.graph import build_agent, AGENT_SYSTEM_PROMPT

BANNER = """
============================================================
 Logistics Agent — RAG + Live Tools test CLI
 Type your question, or 'exit' to quit.

 Try:
   "Is SKU-1005 in stock?"
   "What's the status of order ORD-50012?"
   "Cost to ship 30kg via Expedited with FastFreight Co?"
   "What's the restocking fee on bulk returns?"   (pure RAG, no tool)
============================================================
"""


def print_tool_activity(new_messages):
    """Print which tools were called and what they returned, for transparency."""
    for m in new_messages:
        if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
            for tc in m.tool_calls:
                print(f"  [tool call] {tc['name']}({tc['args']})")
        if isinstance(m, ToolMessage):
            preview = m.content if len(m.content) < 200 else m.content[:200] + "..."
            print(f"  [tool result] {preview}")


def main():
    print(BANNER)
    print("Building agent graph (LLM + tools)...\n")
    agent = build_agent()

    history = [SystemMessage(content=AGENT_SYSTEM_PROMPT)]

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

        history.append(HumanMessage(content=query))
        result = agent.invoke({"messages": history})
        new_messages = result["messages"]

        print_tool_activity(new_messages[len(history):])

        final_message = new_messages[-1]
        print(f"\nAssistant: {final_message.content}\n")

        history = new_messages  # carry full history forward for multi-turn context


if __name__ == "__main__":
    main()
