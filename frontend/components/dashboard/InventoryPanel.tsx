"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { InventorySummary } from "@/lib/api";
import ChartCard, { ChartTooltip } from "./ChartCard";
import { AlertTriangle } from "lucide-react";

const AXIS_STYLE = { fill: "#6d7690", fontSize: 12 };

export default function InventoryPanel({ data }: { data: InventorySummary }) {
  const categoryData = data.by_category.map((c) => ({
    name: `Category ${c.category}`,
    qty: c.total_qty,
  }));
  const zoneData = data.by_zone.map((z) => ({ name: z.zone, qty: z.total_qty }));

  return (
    <div className="grid gap-5 lg:grid-cols-2">
      <ChartCard title="Stock by category" subtitle="Total units on hand">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={categoryData} margin={{ left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1c2338" vertical={false} />
            <XAxis dataKey="name" tick={AXIS_STYLE} axisLine={{ stroke: "#1c2338" }} tickLine={false} />
            <YAxis tick={AXIS_STYLE} axisLine={{ stroke: "#1c2338" }} tickLine={false} />
            <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
            <Bar dataKey="qty" name="Units" fill="#3987e5" radius={[4, 4, 0, 0]} maxBarSize={56} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Stock by warehouse zone" subtitle="Total units on hand">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={zoneData} margin={{ left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1c2338" vertical={false} />
            <XAxis dataKey="name" tick={AXIS_STYLE} axisLine={{ stroke: "#1c2338" }} tickLine={false} />
            <YAxis tick={AXIS_STYLE} axisLine={{ stroke: "#1c2338" }} tickLine={false} />
            <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
            <Bar dataKey="qty" name="Units" fill="#199e70" radius={[4, 4, 0, 0]} maxBarSize={40} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      {data.low_stock_items.length > 0 && (
        <div className="glass-card p-6 lg:col-span-2">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-status-warning" />
            <h3 className="text-sm font-semibold text-ink-primary">
              Below reorder point ({data.low_stock_items.length})
            </h3>
          </div>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[500px] text-left text-sm">
              <thead>
                <tr className="text-xs uppercase tracking-wide text-ink-muted">
                  <th className="pb-2 pr-4 font-medium">SKU</th>
                  <th className="pb-2 pr-4 font-medium">Product</th>
                  <th className="pb-2 pr-4 font-medium">Zone</th>
                  <th className="pb-2 pr-4 font-medium">On hand</th>
                  <th className="pb-2 font-medium">Reorder point</th>
                </tr>
              </thead>
              <tbody>
                {data.low_stock_items.map((item: any) => (
                  <tr key={item.sku_id} className="border-t border-white/5">
                    <td className="py-2 pr-4 font-medium text-ink-primary">{item.sku_id}</td>
                    <td className="py-2 pr-4 text-ink-secondary">{item.product_name}</td>
                    <td className="py-2 pr-4 text-ink-secondary">{item.zone}</td>
                    <td className="py-2 pr-4 tabular-nums text-status-warning">{item.quantity_on_hand}</td>
                    <td className="py-2 tabular-nums text-ink-secondary">{item.reorder_point}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
