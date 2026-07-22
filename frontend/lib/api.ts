const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json();
}

export interface ImpactAssumptions {
  minutes_per_lookup: number;
  minutes_per_escalation: number;
  hourly_labor_rate_usd: number;
}

export interface ImpactSummary {
  queries_handled: number;
  automated_lookups: number;
  escalations_handled: number;
  guardrail_catches: number;
  minutes_saved: number;
  hours_saved: number;
  cost_saved_usd: number;
  assumptions: ImpactAssumptions;
}

export interface DashboardSummary {
  total_skus: number;
  low_stock_count: number;
  in_transit_count: number;
  delayed_count: number;
  lost_count: number;
  on_time_rate_pct: number;
  open_escalations: number;
}

export interface CategoryBreakdown {
  category: string;
  sku_count: number;
  total_qty: number;
}

export interface ZoneBreakdown {
  zone: string;
  sku_count: number;
  total_qty: number;
}

export interface InventorySummary {
  total_skus: number;
  total_units: number;
  low_stock_count: number;
  healthy_count: number;
  by_category: CategoryBreakdown[];
  by_zone: ZoneBreakdown[];
  low_stock_items: Record<string, unknown>[];
}

export interface StatusBreakdown {
  status: string;
  count: number;
}

export interface ShipmentsSummary {
  total_shipments: number;
  delivered_count: number;
  delayed_count: number;
  lost_count: number;
  in_transit_count: number;
  on_time_rate_pct: number;
  by_status: StatusBreakdown[];
  delay_reason_breakdown: { delay_flag: string; count: number }[];
}

export interface CarrierPerformance {
  carrier: string;
  avg_transit_days: number;
  avg_base_rate_usd: number;
  avg_fuel_surcharge_pct: number;
}

export interface CarriersSummary {
  carriers: CarrierPerformance[];
}

export interface EscalationRecord {
  id: string;
  timestamp: string;
  query: string;
  reason: string;
  to: string;
  subject: string;
  body: string;
  sent: boolean;
  dry_run: boolean;
  error: string | null;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  blocked: boolean;
  block_reason: string | null;
  pii_redacted: boolean;
  grounding_ok: boolean;
  tool_calls: string[];
  sources: string[];
  escalation: EscalationRecord | null;
  error: string | null;
}

export const api = {
  dashboardSummary: () => getJSON<DashboardSummary>("/api/dashboard/summary"),
  inventory: () => getJSON<InventorySummary>("/api/dashboard/inventory"),
  shipments: () => getJSON<ShipmentsSummary>("/api/dashboard/shipments"),
  carriers: () => getJSON<CarriersSummary>("/api/dashboard/carriers"),
  impact: () => getJSON<ImpactSummary>("/api/dashboard/impact"),
  escalations: () => getJSON<EscalationRecord[]>("/api/escalations"),

  chat: async (sessionId: string, message: string): Promise<ChatResponse> => {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message }),
    });
    if (!res.ok) throw new Error(`chat failed: ${res.status}`);
    return res.json();
  },
};
