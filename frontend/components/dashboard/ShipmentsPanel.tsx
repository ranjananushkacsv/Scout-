"use client";

import {
  Bar,
  BarChart,
  Cell,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ShipmentsSummary } from "@/lib/api";
import ChartCard, { ChartTooltip } from "./ChartCard";

const AXIS_STYLE = { fill: "#6d7690", fontSize: 12 };

const STATUS_COLOR: Record<string, string> = {
  Delivered: "#0ca30c",
  "Out for Delivery": "#3987e5",
  Processing: "#9085e9",
  Delayed: "#fab219",
  "Lost in Transit": "#d03b3b",
};

const STATUS_ORDER = [
  { status: "Delivered", tone: "good" },
  { status: "Delayed", tone: "warning" },
  { status: "Lost in Transit", tone: "critical" },
];

export default function ShipmentsPanel({ data }: { data: ShipmentsSummary }) {
  const statusData = data.by_status.map((s) => ({ name: s.status, count: s.count }));
  const delayData = data.delay_reason_breakdown.map((d) => ({
    name: d.delay_flag,
    count: d.count,
  }));

  return (
    <div className="grid gap-5 lg:grid-cols-2">
      <ChartCard title="Shipments by status" subtitle={`${data.total_shipments} total shipments`}>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={statusData} layout="vertical" margin={{ left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1c2338" horizontal={false} />
            <XAxis type="number" tick={AXIS_STYLE} axisLine={{ stroke: "#1c2338" }} tickLine={false} />
            <YAxis
              type="category"
              dataKey="name"
              tick={AXIS_STYLE}
              axisLine={{ stroke: "#1c2338" }}
              tickLine={false}
              width={110}
            />
            <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
            <Bar dataKey="count" name="Shipments" radius={[0, 4, 4, 0]} maxBarSize={26}>
              {statusData.map((entry) => (
                <Cell key={entry.name} fill={STATUS_COLOR[entry.name] ?? "#3987e5"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        <div className="mt-4 flex flex-wrap gap-3">
          {STATUS_ORDER.map(({ status, tone }) => (
            <span key={status} className="flex items-center gap-1.5 text-xs text-ink-secondary">
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: STATUS_COLOR[status] }}
              />
              {status}
            </span>
          ))}
        </div>
      </ChartCard>

      <ChartCard title="Delay reason breakdown" subtitle={`${data.delayed_count} delayed · ${data.lost_count} lost`}>
        {delayData.length > 0 ? (
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={delayData} margin={{ left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1c2338" vertical={false} />
              <XAxis dataKey="name" tick={AXIS_STYLE} axisLine={{ stroke: "#1c2338" }} tickLine={false} />
              <YAxis tick={AXIS_STYLE} axisLine={{ stroke: "#1c2338" }} tickLine={false} />
              <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
              <Bar dataKey="count" name="Shipments" fill="#fab219" radius={[4, 4, 0, 0]} maxBarSize={56} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-[240px] items-center justify-center text-sm text-ink-muted">
            No delay records right now.
          </div>
        )}
      </ChartCard>
    </div>
  );
}
