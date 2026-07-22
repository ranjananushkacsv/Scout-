import { Clock, DollarSign, Zap, MailCheck, ShieldCheck, LucideIcon } from "lucide-react";
import type { ImpactSummary } from "@/lib/api";

export default function ImpactBanner({ data }: { data: ImpactSummary }) {
  const { assumptions } = data;

  return (
    <div className="glass-card relative overflow-hidden p-6 sm:p-8">
      <div className="pointer-events-none absolute inset-0 bg-hero-glow opacity-60" />

      <div className="relative">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <div>
            <span className="text-xs font-semibold uppercase tracking-widest text-brand-cyan">
              Impact
            </span>
            <h2 className="mt-1 text-xl font-bold text-ink-primary">
              What Scout has saved your team
            </h2>
          </div>
          <span className="text-xs text-ink-muted">
            Based on {data.queries_handled} assistant {data.queries_handled === 1 ? "query" : "queries"} so far
          </span>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-5 sm:grid-cols-3 lg:grid-cols-5">
          <ImpactStat icon={Clock} value={`${data.hours_saved}h`} label="Time saved" highlight />
          <ImpactStat
            icon={DollarSign}
            value={`$${data.cost_saved_usd.toLocaleString()}`}
            label="Cost saved"
            highlight
          />
          <ImpactStat icon={Zap} value={data.automated_lookups} label="Lookups automated" />
          <ImpactStat icon={MailCheck} value={data.escalations_handled} label="Escalations handled" />
          <ImpactStat icon={ShieldCheck} value={data.guardrail_catches} label="Risky requests caught" />
        </div>

        <p className="mt-6 text-xs text-ink-muted">
          Estimate: {assumptions.minutes_per_lookup} min saved per automated lookup and{" "}
          {assumptions.minutes_per_escalation} min per auto-handled escalation, at $
          {assumptions.hourly_labor_rate_usd}/hr — tune these in <code className="rounded bg-white/10 px-1 py-0.5">config.py</code> to match your team.
        </p>
      </div>
    </div>
  );
}

function ImpactStat({
  icon: Icon,
  value,
  label,
  highlight,
}: {
  icon: LucideIcon;
  value: string | number;
  label: string;
  highlight?: boolean;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <span
        className={
          highlight
            ? "flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-brand-cyan/20 to-brand-violet/20 text-brand-cyan"
            : "flex h-9 w-9 items-center justify-center rounded-lg bg-white/5 text-ink-secondary"
        }
      >
        <Icon className="h-4 w-4" />
      </span>
      <span className={`text-2xl font-bold tabular-nums ${highlight ? "gradient-text" : "text-ink-primary"}`}>
        {value}
      </span>
      <span className="text-xs text-ink-secondary">{label}</span>
    </div>
  );
}
