export default function ChartCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="glass-card p-6">
      <h3 className="text-sm font-semibold text-ink-primary">{title}</h3>
      {subtitle && <p className="mt-0.5 text-xs text-ink-muted">{subtitle}</p>}
      <div className="mt-4">{children}</div>
    </div>
  );
}

export function ChartTooltip({
  active,
  payload,
  label,
  unit,
}: {
  active?: boolean;
  payload?: { value: number; name: string; color?: string }[];
  label?: string;
  unit?: string;
}) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="rounded-lg border border-white/10 bg-[#0e1424] px-3 py-2 text-xs shadow-card">
      <div className="font-medium text-ink-primary">{label}</div>
      {payload.map((p, i) => (
        <div key={i} className="mt-1 flex items-center gap-1.5 text-ink-secondary">
          {p.color && (
            <span
              className="h-2 w-2 rounded-full"
              style={{ backgroundColor: p.color }}
            />
          )}
          {p.name}: <span className="font-semibold text-ink-primary">{p.value}{unit}</span>
        </div>
      ))}
    </div>
  );
}
