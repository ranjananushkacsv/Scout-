"use client";

import { useState } from "react";
import clsx from "clsx";
import {
  Boxes,
  Truck,
  AlertTriangle,
  Ban,
  MailQuestion,
  CheckCircle2,
} from "lucide-react";
import StatTile from "./StatTile";
import ImpactBanner from "./ImpactBanner";
import InventoryPanel from "./InventoryPanel";
import ShipmentsPanel from "./ShipmentsPanel";
import CarriersPanel from "./CarriersPanel";
import EscalationsPanel from "./EscalationsPanel";
import type {
  CarriersSummary,
  DashboardSummary,
  EscalationRecord,
  ImpactSummary,
  InventorySummary,
  ShipmentsSummary,
} from "@/lib/api";

const TABS = ["Inventory", "Shipments", "Carriers", "Escalations"] as const;
type Tab = (typeof TABS)[number];

export default function DashboardTabs({
  summary,
  inventory,
  shipments,
  carriers,
  impact,
  escalations,
}: {
  summary: DashboardSummary;
  inventory: InventorySummary;
  shipments: ShipmentsSummary;
  carriers: CarriersSummary;
  impact: ImpactSummary;
  escalations: EscalationRecord[];
}) {
  const [tab, setTab] = useState<Tab>("Inventory");

  return (
    <div>
      <ImpactBanner data={impact} />

      <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <StatTile icon={Boxes} label="Total SKUs" value={summary.total_skus} tone="neutral" />
        <StatTile
          icon={AlertTriangle}
          label="Low stock"
          value={summary.low_stock_count}
          tone={summary.low_stock_count > 0 ? "warning" : "good"}
        />
        <StatTile icon={Truck} label="In transit" value={summary.in_transit_count} tone="neutral" />
        <StatTile
          icon={AlertTriangle}
          label="Delayed"
          value={summary.delayed_count}
          tone={summary.delayed_count > 0 ? "warning" : "good"}
        />
        <StatTile
          icon={Ban}
          label="Lost"
          value={summary.lost_count}
          tone={summary.lost_count > 0 ? "critical" : "good"}
        />
        <StatTile
          icon={summary.open_escalations > 0 ? MailQuestion : CheckCircle2}
          label="Open escalations"
          value={summary.open_escalations}
          tone={summary.open_escalations > 0 ? "warning" : "good"}
        />
      </div>

      <div className="mt-10 flex gap-2 overflow-x-auto border-b border-white/5 pb-px">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={clsx(
              "whitespace-nowrap rounded-t-lg px-4 py-2.5 text-sm font-medium transition-colors",
              tab === t
                ? "border-b-2 border-brand-cyan text-ink-primary"
                : "border-b-2 border-transparent text-ink-muted hover:text-ink-secondary"
            )}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {tab === "Inventory" && <InventoryPanel data={inventory} />}
        {tab === "Shipments" && <ShipmentsPanel data={shipments} />}
        {tab === "Carriers" && <CarriersPanel data={carriers} />}
        {tab === "Escalations" && <EscalationsPanel data={escalations} />}
      </div>
    </div>
  );
}
