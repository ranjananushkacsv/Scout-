import { Radar } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-white/5 bg-bg">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-6 py-10 md:flex-row">
        <div className="flex items-center gap-2">
          <Radar className="h-5 w-5 text-brand-cyan" />
          <span className="font-semibold text-ink-primary">Scout</span>
          <span className="text-sm text-ink-muted">
            — Enterprise AI Supply Chain Copilot
          </span>
        </div>
        <p className="text-sm text-ink-muted">
          Built on a guarded retrieval + tool-use agent. Every write action is
          escalated to a human, always.
        </p>
      </div>
    </footer>
  );
}
