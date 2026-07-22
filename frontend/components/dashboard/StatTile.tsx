import { LucideIcon } from "lucide-react";
import clsx from "clsx";

const TONE_STYLES: Record<string, string> = {
  neutral: "text-brand-cyan bg-brand-cyan/10",
  good: "text-status-good bg-status-good/10",
  warning: "text-status-warning bg-status-warning/10",
  critical: "text-status-critical bg-status-critical/10",
};

export default function StatTile({
  icon: Icon,
  label,
  value,
  sublabel,
  tone = "neutral",
}: {
  icon: LucideIcon;
  label: string;
  value: string | number;
  sublabel?: string;
  tone?: "neutral" | "good" | "warning" | "critical";
}) {
  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-ink-secondary">{label}</span>
        <span className={clsx("flex h-8 w-8 items-center justify-center rounded-lg", TONE_STYLES[tone])}>
          <Icon className="h-4 w-4" />
        </span>
      </div>
      <div className="mt-3 text-3xl font-bold tabular-nums text-ink-primary">
        {value}
      </div>
      {sublabel && <div className="mt-1 text-xs text-ink-muted">{sublabel}</div>}
    </div>
  );
}
