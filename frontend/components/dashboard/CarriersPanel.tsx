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
import type { CarriersSummary } from "@/lib/api";
import ChartCard, { ChartTooltip } from "./ChartCard";

const AXIS_STYLE = { fill: "#6d7690", fontSize: 12 };

export default function CarriersPanel({ data }: { data: CarriersSummary }) {
  const transitData = data.carriers.map((c) => ({
    name: c.carrier,
    days: c.avg_transit_days,
  }));

  return (
    <div className="grid gap-5 lg:grid-cols-2">
      <ChartCard title="Avg transit time by carrier" subtitle="Days, across all service levels">
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={transitData} margin={{ left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1c2338" vertical={false} />
            <XAxis dataKey="name" tick={AXIS_STYLE} axisLine={{ stroke: "#1c2338" }} tickLine={false} interval={0} angle={-15} textAnchor="end" height={50} />
            <YAxis tick={AXIS_STYLE} axisLine={{ stroke: "#1c2338" }} tickLine={false} unit="d" />
            <Tooltip content={<ChartTooltip unit=" days" />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
            <Bar dataKey="days" name="Avg transit" fill="#9085e9" radius={[4, 4, 0, 0]} maxBarSize={48} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <div className="glass-card overflow-x-auto p-6">
        <h3 className="text-sm font-semibold text-ink-primary">Carrier rate summary</h3>
        <p className="mt-0.5 text-xs text-ink-muted">Averaged across weight bands</p>
        <table className="mt-4 w-full min-w-[420px] text-left text-sm">
          <thead>
            <tr className="text-xs uppercase tracking-wide text-ink-muted">
              <th className="pb-2 pr-4 font-medium">Carrier</th>
              <th className="pb-2 pr-4 font-medium">Base rate</th>
              <th className="pb-2 font-medium">Fuel surcharge</th>
            </tr>
          </thead>
          <tbody>
            {data.carriers.map((c) => (
              <tr key={c.carrier} className="border-t border-white/5">
                <td className="py-2 pr-4 font-medium text-ink-primary">{c.carrier}</td>
                <td className="py-2 pr-4 tabular-nums text-ink-secondary">${c.avg_base_rate_usd.toFixed(2)}</td>
                <td className="py-2 tabular-nums text-ink-secondary">{c.avg_fuel_surcharge_pct.toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
