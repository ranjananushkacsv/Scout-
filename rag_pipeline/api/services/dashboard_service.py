"""
api/services/dashboard_service.py — turns the CSVs in data/tabular (our
stand-in "database") into the aggregates the dashboard renders.

Nothing here is persisted — every call re-reads the CSVs, so editing a row
in inventory.csv / shipments.csv / carrier_rates.csv is reflected on the
next request with no restart needed.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd

import config


def _read(filename: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(config.TABULAR_DIR, filename))


def get_inventory_summary() -> dict:
    df = _read("inventory.csv")
    df["below_reorder"] = df["quantity_on_hand"] <= df["reorder_point"]

    by_category = (
        df.groupby("category")
        .agg(sku_count=("sku_id", "count"), total_qty=("quantity_on_hand", "sum"))
        .reset_index()
        .sort_values("category")
    )
    by_zone = (
        df.groupby("zone")
        .agg(sku_count=("sku_id", "count"), total_qty=("quantity_on_hand", "sum"))
        .reset_index()
        .sort_values("zone")
    )

    low_stock = df[df["below_reorder"]].copy()
    low_stock_items = low_stock[
        ["sku_id", "product_name", "category", "zone", "quantity_on_hand", "reorder_point"]
    ].to_dict(orient="records")

    return {
        "total_skus": int(len(df)),
        "total_units": int(df["quantity_on_hand"].sum()),
        "low_stock_count": int(df["below_reorder"].sum()),
        "healthy_count": int((~df["below_reorder"]).sum()),
        "by_category": by_category.to_dict(orient="records"),
        "by_zone": by_zone.to_dict(orient="records"),
        "low_stock_items": low_stock_items,
    }


def get_shipments_summary() -> dict:
    df = _read("shipments.csv")
    total = len(df)

    by_status = (
        df.groupby("status").size().reset_index(name="count").sort_values("count", ascending=False)
    )

    delayed = int((df["status"] == "Delayed").sum())
    lost = int((df["status"] == "Lost in Transit").sum())
    delivered = int(df["status"].isin(["Delivered"]).sum())
    in_transit = int(df["status"].isin(["Out for Delivery", "Processing", "In Transit"]).sum())

    on_time_rate = round((delivered / total) * 100, 1) if total else 0.0

    delay_df = df[df["delay_flag"].notna() & (df["delay_flag"].astype(str).str.strip() != "")]
    delay_reason_breakdown = (
        delay_df.groupby("delay_flag").size().reset_index(name="count").to_dict(orient="records")
    )

    return {
        "total_shipments": int(total),
        "delivered_count": delivered,
        "delayed_count": delayed,
        "lost_count": lost,
        "in_transit_count": in_transit,
        "on_time_rate_pct": on_time_rate,
        "by_status": by_status.to_dict(orient="records"),
        "delay_reason_breakdown": delay_reason_breakdown,
    }


def get_carriers_summary() -> dict:
    df = _read("carrier_rates.csv")
    grouped = (
        df.groupby("carrier")
        .agg(
            avg_transit_days=("avg_transit_days", "mean"),
            avg_base_rate_usd=("base_rate_usd", "mean"),
            avg_fuel_surcharge_pct=("fuel_surcharge_pct", "mean"),
        )
        .reset_index()
        .round(2)
        .sort_values("avg_transit_days")
    )
    return {"carriers": grouped.to_dict(orient="records")}


def get_dashboard_summary(open_escalations: int = 0) -> dict:
    inv = get_inventory_summary()
    ship = get_shipments_summary()
    return {
        "total_skus": inv["total_skus"],
        "low_stock_count": inv["low_stock_count"],
        "in_transit_count": ship["in_transit_count"],
        "delayed_count": ship["delayed_count"],
        "lost_count": ship["lost_count"],
        "on_time_rate_pct": ship["on_time_rate_pct"],
        "open_escalations": open_escalations,
    }
