"""
api/models.py — Pydantic request/response schemas for the Scout API.
"""

from typing import Any, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str


class EscalationRecord(BaseModel):
    id: str
    timestamp: str
    query: str
    reason: str
    to: str
    subject: str
    body: str
    sent: bool
    dry_run: bool
    error: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    blocked: bool
    block_reason: Optional[str] = None
    pii_redacted: bool = False
    grounding_ok: bool = True
    tool_calls: list[str] = []
    sources: list[str] = []
    escalation: Optional[EscalationRecord] = None
    error: Optional[str] = None


class CategoryBreakdown(BaseModel):
    category: str
    sku_count: int
    total_qty: int


class ZoneBreakdown(BaseModel):
    zone: str
    sku_count: int
    total_qty: int


class InventorySummary(BaseModel):
    total_skus: int
    total_units: int
    low_stock_count: int
    healthy_count: int
    by_category: list[CategoryBreakdown]
    by_zone: list[ZoneBreakdown]
    low_stock_items: list[dict[str, Any]]


class StatusBreakdown(BaseModel):
    status: str
    count: int


class ShipmentsSummary(BaseModel):
    total_shipments: int
    delivered_count: int
    delayed_count: int
    lost_count: int
    in_transit_count: int
    on_time_rate_pct: float
    by_status: list[StatusBreakdown]
    delay_reason_breakdown: list[dict[str, Any]]


class CarrierPerformance(BaseModel):
    carrier: str
    avg_transit_days: float
    avg_base_rate_usd: float
    avg_fuel_surcharge_pct: float


class CarriersSummary(BaseModel):
    carriers: list[CarrierPerformance]


class DashboardSummary(BaseModel):
    total_skus: int
    low_stock_count: int
    in_transit_count: int
    delayed_count: int
    lost_count: int
    on_time_rate_pct: float
    open_escalations: int


class ImpactAssumptions(BaseModel):
    minutes_per_lookup: float
    minutes_per_escalation: float
    hourly_labor_rate_usd: float


class ImpactSummary(BaseModel):
    queries_handled: int
    automated_lookups: int
    escalations_handled: int
    guardrail_catches: int
    minutes_saved: float
    hours_saved: float
    cost_saved_usd: float
    assumptions: ImpactAssumptions
