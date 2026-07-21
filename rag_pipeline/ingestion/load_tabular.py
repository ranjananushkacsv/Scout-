"""
ingestion/load_tabular.py — converts rows from the operational CSVs
(inventory, shipments, carrier rates) into short text "cards" that can be
embedded and retrieved just like document chunks.

Important design note: in the full agentic architecture, LIVE inventory/
shipment data should be served through agent tool calls (see the
Architecture doc), not baked into the vector store, because it changes
constantly. Indexing the CSVs here is useful for:
  1) Early RAG testing before the agent/tool layer exists
  2) Reference-style tabular data that doesn't change often (e.g. rate sheets)

Swap this out once your live inventory/shipment tools are wired up.
"""

import os
import pandas as pd


def _row_to_text(row, columns, source_label):
    parts = [f"{col}: {row[col]}" for col in columns if pd.notna(row[col])]
    return f"[{source_label}] " + " | ".join(parts)


def load_csv_as_cards(filepath, source_label):
    """Turn each row of a CSV into one retrievable text card."""
    df = pd.read_csv(filepath)
    cards = []
    for _, row in df.iterrows():
        cards.append(_row_to_text(row, df.columns, source_label))
    return cards


def load_all_tabular(tabular_dir):
    """
    Load every CSV in `tabular_dir` and convert rows to text cards.

    Returns a list of dicts: {"source": filename, "text": card_text}
    one entry per row (each row becomes its own small "document").
    """
    records = []
    if not os.path.isdir(tabular_dir):
        return records

    for filename in sorted(os.listdir(tabular_dir)):
        if not filename.lower().endswith(".csv"):
            continue
        filepath = os.path.join(tabular_dir, filename)
        label = os.path.splitext(filename)[0]
        try:
            cards = load_csv_as_cards(filepath, label)
        except Exception as e:
            print(f"  [warn] Failed to read {filename}: {e}")
            continue
        for card in cards:
            records.append({"source": filename, "text": card})
    return records
