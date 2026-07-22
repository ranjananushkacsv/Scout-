"""
agent/graph.py — builds the LangGraph agent that lets Gemma 4 decide, per
query, whether to answer directly, search the knowledge base (RAG), or
call a live-data tool (inventory / shipment status / rate calculator).

Flow:
    user message -> agent (LLM) -> decides to call a tool? 
        yes -> tools node executes it -> back to agent with the result
        no  -> END, return the answer
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode, tools_condition

import config
from agent.tools import ALL_TOOLS

AGENT_SYSTEM_PROMPT = """You are a logistics and warehousing operations assistant with access to tools.

Rules you must always follow:
1. Use search_knowledge_base for policy/procedure/SOP/glossary questions.
2. Use check_inventory, get_shipment_status, or calculate_shipping_cost for
   live operational data — always call the tool rather than guessing values.
3. If a question needs both policy context and live data, call both tools
   before answering.
4. Never fabricate a SKU ID, order ID, or number — if a tool returns "not
   found", tell the user rather than inventing a plausible-sounding answer.
5. Stay within the logistics/warehousing domain; politely decline unrelated
   requests.
6. For actions that write/modify data (approving refunds, cancelling orders,
   editing inventory), explain that this requires human escalation — you do
   not have a tool for that and must not pretend to perform it.
7. Formatting: write in short paragraphs (2-3 sentences max) or a short
   bullet list when giving multiple facts/numbers — never one dense wall of
   text. Do NOT include bracketed citations like "[Source 1: ...]" or
   "(Source: ...)" in your answer — sources are shown separately to the
   user, so just answer naturally.
"""


def build_agent():
    """Compile and return the runnable LangGraph agent."""
    llm = ChatOllama(
        model=config.OLLAMA_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        temperature=config.OLLAMA_TEMPERATURE,
        num_ctx=config.OLLAMA_NUM_CTX,
    )
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def agent_node(state: MessagesState):
        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT)] + messages
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(ALL_TOOLS))

    graph.set_entry_point("agent")
    # tools_condition inspects the agent's last message: if it contains
    # tool calls, route to "tools"; otherwise route to END.
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")  # after running a tool, let the agent respond

    return graph.compile()
