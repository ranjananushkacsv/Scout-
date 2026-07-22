import ChatWindow from "@/components/assistant/ChatWindow";

export default function AssistantPage() {
  return (
    <div className="relative">
      <div className="pointer-events-none absolute inset-0 bg-hero-glow" />
      <div className="relative mx-auto max-w-4xl px-6 py-12">
        <div className="mb-8 text-center">
          <span className="text-sm font-semibold uppercase tracking-widest text-brand-violet">
            AI Assistant
          </span>
          <h1 className="mt-2 text-3xl font-bold text-ink-primary">Talk to Scout</h1>
          <p className="mx-auto mt-2 max-w-xl text-ink-secondary">
            Grounded in your policies and live operational data.
          </p>
        </div>
        <ChatWindow />
      </div>
    </div>
  );
}
