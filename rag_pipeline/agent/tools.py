"""
agent/tools.py — defines the tools (functions) that the agent can call.

Each tool is decorated with @tool so LangChain/LangGraph can expose it to
Gemma 4 as a callable function. The docstring on each tool becomes the
description the model reads to decide when to call it — keep them precise.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from langchain_core.tools import tool

import config
from rag.pipeline import format_context
from rag.retriever import Retriever
from rag.embedder import Embedder
from rag.vector_store import VectorStore

_embedder = None
_store = None
_retriever = None


def _get_retriever():
    global _embedder, _store, _retriever
    if _retriever is None:
        _embedder = Embedder()
        _store = VectorStore()
        _retriever = Retriever(embedder=_embedder, store=_store)
    return _retriever


def _load_csv(filename):
    path = os.path.join(config.TABULAR_DIR, filename)
    return pd.read_csv(path)


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search SOPs, policies, glossary, and FAQ documents for information about
    warehouse procedures, shipping/returns policy, escalation rules, or
    logistics terminology. Use this for "how / what / why" policy or
    procedure questions — NOT for live inventory or shipment status.
    """
    retriever = _get_retriever()
    hits = retriever.retrieve(query, top_k=3)
    if not hits:
        return "No relevant information found in the knowledge base."
    return format_context(hits)


@tool
def check_inventory(sku_id: str) -> str:
    """
    Look up current stock levels for a specific SKU ID (e.g. "SKU-1005").
    Returns quantity on hand, reorder point, safety stock, zone, and
    category. Use this when the user asks about live/current stock of a
    specific item.
    """
    df = _load_csv("inventory.csv")
    row = df[df["sku_id"].str.upper() == sku_id.upper().strip()]
    if row.empty:
        return f"No inventory record found for SKU '{sku_id}'. Double-check the SKU ID."
    r = row.iloc[0]
    status = (
        "Below reorder point — restock recommended."
        if r["quantity_on_hand"] <= r["reorder_point"]
        else "Stock level healthy."
    )
    return (
        f"SKU {r['sku_id']} ({r['product_name']}): "
        f"{r['quantity_on_hand']} {r['unit_of_measure']} on hand in {r['zone']} "
        f"(Category {r['category']}). Reorder point: {r['reorder_point']}, "
        f"safety stock: {r['safety_stock']}. {status}"
    )


@tool
def get_shipment_status(order_id: str) -> str:
    """
    Look up the current status of a shipment by order ID (e.g. "ORD-50012").
    Returns status, carrier, service level, ship date, and estimated
    delivery. Use this when the user asks where their order/shipment is.
    """
    df = _load_csv("shipments.csv")
    row = df[df["order_id"].str.upper() == order_id.upper().strip()]
    if row.empty:
        return f"No shipment record found for order '{order_id}'. Double-check the order ID."
    r = row.iloc[0]
    delay_note = ""
    if pd.notna(r["delay_flag"]) and str(r["delay_flag"]).strip():
        delay_note = f" Delay reason code: {r['delay_flag']}."
    return (
        f"Order {r['order_id']} (shipment {r['shipment_id']}): status is "
        f"'{r['status']}' via {r['carrier']} ({r['service_level']}). "
        f"Shipped {r['ship_date']}, estimated delivery {r['estimated_delivery']}."
        f"{delay_note}"
    )


@tool
def calculate_shipping_cost(carrier: str, service_level: str, weight_kg: float) -> str:
    """
    Estimate shipping cost for a given carrier, service level, and package
    weight in kg. Valid service levels: "Standard Ground", "Expedited",
    "Next-Day Air", "Freight (LTL)". Use this when the user asks how much
    shipping would cost.
    """
    df = _load_csv("carrier_rates.csv")
    matches = df[
        (df["carrier"].str.lower() == carrier.lower().strip())
        & (df["service_level"].str.lower() == service_level.lower().strip())
    ]
    if matches.empty:
        available = ", ".join(sorted(df["carrier"].unique()))
        return (
            f"No rate found for carrier '{carrier}' with service level "
            f"'{service_level}'. Available carriers: {available}."
        )

    def band_matches(band_str, weight):
        band_str = band_str.replace(" (LTL)", "")
        low, high = band_str.split("-")
        return float(low) <= weight <= float(high)

    band_row = None
    for _, r in matches.iterrows():
        if band_matches(r["weight_band_kg"], weight_kg):
            band_row = r
            break
    if band_row is None:
        band_row = matches.iloc[-1]

    base_cost = band_row["base_rate_usd"] + (band_row["per_kg_surcharge_usd"] * weight_kg)
    total_cost = base_cost * (1 + band_row["fuel_surcharge_pct"] / 100)

    return (
        f"Estimated cost for {weight_kg}kg via {carrier} ({service_level}): "
        f"${total_cost:.2f} (includes {band_row['fuel_surcharge_pct']}% fuel "
        f"surcharge). Average transit time: {band_row['avg_transit_days']} days."
    )


ALL_TOOLS = [search_knowledge_base, check_inventory, get_shipment_status, calculate_shipping_cost]