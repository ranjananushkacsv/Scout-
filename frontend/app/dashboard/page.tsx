import { WifiOff } from "lucide-react";
import { api } from "@/lib/api";
import DashboardTabs from "@/components/dashboard/DashboardTabs";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  try {
    const [summary, inventory, shipments, carriers, impact, escalations] = await Promise.all([
      api.dashboardSummary(),
      api.inventory(),
      api.shipments(),
      api.carriers(),
      api.impact(),
      api.escalations(),
    ]);

    return (
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="mb-8">
          <span className="text-sm font-semibold uppercase tracking-widest text-brand-cyan">
            Live
          </span>
          <h1 className="mt-2 text-3xl font-bold text-ink-primary">
            Operations dashboard
          </h1>
          <p className="mt-2 text-ink-secondary">
            Reflects inventory.csv, shipments.csv, and carrier_rates.csv in
            real time — the same data Scout's assistant reads from.
          </p>
        </div>

        <DashboardTabs
          summary={summary}
          inventory={inventory}
          shipments={shipments}
          carriers={carriers}
          impact={impact}
          escalations={escalations}
        />
      </div>
    );
  } catch {
    return (
      <div className="mx-auto flex max-w-2xl flex-col items-center gap-4 px-6 py-32 text-center">
        <WifiOff className="h-8 w-8 text-status-warning" />
        <h1 className="text-xl font-semibold text-ink-primary">
          Can&apos;t reach the Scout API
        </h1>
        <p className="text-ink-secondary">
          Start the backend from the <code className="rounded bg-white/10 px-1.5 py-0.5">rag_pipeline</code> folder:
        </p>
        <pre className="glass-card w-full overflow-x-auto p-4 text-left text-sm text-brand-cyan">
          uvicorn api.server:app --reload --port 8000
        </pre>
      </div>
    );
  }
}
