import type { EscalationRecord } from "@/lib/api";
import { Mail, MailCheck, MailWarning } from "lucide-react";

function timeAgo(iso: string) {
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function EscalationsPanel({ data }: { data: EscalationRecord[] }) {
  if (data.length === 0) {
    return (
      <div className="glass-card flex flex-col items-center justify-center gap-2 p-10 text-center">
        <Mail className="h-6 w-6 text-ink-muted" />
        <p className="text-sm text-ink-secondary">
          No escalations yet — Scout drafts an email here the moment a request
          needs human approval.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-card divide-y divide-white/5 p-2">
      {data.map((e) => (
        <div key={e.id} className="flex flex-col gap-2 p-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-2">
              {e.sent ? (
                <MailCheck className="h-4 w-4 shrink-0 text-status-good" />
              ) : (
                <MailWarning className="h-4 w-4 shrink-0 text-status-warning" />
              )}
              <span className="text-sm font-semibold text-ink-primary">{e.subject}</span>
            </div>
            <span className="whitespace-nowrap text-xs text-ink-muted">{timeAgo(e.timestamp)}</span>
          </div>
          <p className="text-sm text-ink-secondary">
            &ldquo;{e.query}&rdquo;
          </p>
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="rounded-full border border-white/10 px-2 py-0.5 text-ink-muted">
              reason: {e.reason.replace(/_/g, " ")}
            </span>
            <span className="rounded-full border border-white/10 px-2 py-0.5 text-ink-muted">
              to: {e.to}
            </span>
            {e.sent ? (
              <span className="rounded-full bg-status-good/10 px-2 py-0.5 font-medium text-status-good">
                sent
              </span>
            ) : (
              <span className="rounded-full bg-status-warning/10 px-2 py-0.5 font-medium text-status-warning">
                {e.dry_run ? "drafted (dry-run — SMTP not configured)" : "send failed"}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
