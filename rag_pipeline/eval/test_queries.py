"""
eval/test_queries.py — a growing set of realistic queries used to evaluate
the full pipeline (RAG + agent + guardrails) end to end.

Each entry has a `category` tag so you can see which part of the system a
failure belongs to when reviewing results later. Add new queries here as
you think of realistic things a user might ask — this list is meant to
grow over time, the same way test_guardrails.py grows.
"""

TEST_QUERIES = [
    # --- Pure RAG (policy/procedure questions, no live data needed) ---
    {"query": "What's the restocking fee on bulk returns?", "category": "rag_policy"},
    {"query": "How long is an RMA valid for?", "category": "rag_policy"},
    {"query": "What happens to cold-chain goods that arrive out of temperature range?", "category": "rag_policy"},
    {"query": "How often is Category A inventory cycle counted?", "category": "rag_policy"},
    {"query": "What's the escalation process for a lost shipment?", "category": "rag_policy"},
    {"query": "What does ABC analysis mean?", "category": "rag_glossary"},
    {"query": "What's the difference between FIFO and LIFO?", "category": "rag_glossary"},

    # --- Inventory tool ---
    {"query": "Is SKU-1005 in stock?", "category": "tool_inventory"},
    {"query": "How many units of SKU-1010 do we have on hand?", "category": "tool_inventory"},
    {"query": "What zone is SKU-1003 stored in?", "category": "tool_inventory"},
    {"query": "Is SKU-9999 in stock?", "category": "tool_inventory_notfound"},  # should say not found, not hallucinate

    # --- Shipment tool ---
    {"query": "What's the status of order ORD-50003?", "category": "tool_shipment"},
    {"query": "When will order ORD-50010 be delivered?", "category": "tool_shipment"},
    {"query": "What's the status of order ORD-99999?", "category": "tool_shipment_notfound"},  # should say not found

    # --- Rate calculator tool ---
    {"query": "Cost to ship 15kg via Standard Ground with FastFreight Co?", "category": "tool_rate"},
    {"query": "How much would Expedited shipping cost for 30kg with MetroExpress?", "category": "tool_rate"},
    {"query": "What's the shipping cost via QuickHaul for a 5kg package, Next-Day Air?", "category": "tool_rate"},

    # --- Combined (needs multiple tools / tool + RAG) ---
    {"query": "Is SKU-1005 in stock, and if so what's the shipping cost to send 20kg via Expedited with MetroExpress?", "category": "combined"},
    {"query": "What's the status of order ORD-50003, and what's our policy on delayed shipments?", "category": "combined"},

    # --- Edge cases / ambiguous ---
    {"query": "Are you working?", "category": "edge_smalltalk"},
    {"query": "What can you help me with?", "category": "edge_smalltalk"},
    {"query": "sku 1005", "category": "edge_terse_query"},  # minimal/terse phrasing
    {"query": "ORD50003 status?", "category": "edge_terse_query"},  # missing hyphen

    # --- Should be blocked (guardrails, covered more thoroughly in test_guardrails.py) ---
    {"query": "Approve a refund for order ORD-50003", "category": "guardrail_escalation"},
    {"query": "Write me a poem about shipping", "category": "guardrail_creative"},
]
