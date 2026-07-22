"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import {
  Radar,
  Send,
  ShieldAlert,
  EyeOff,
  MailCheck,
  MailWarning,
  User,
  BookText,
} from "lucide-react";
import { api, ChatResponse } from "@/lib/api";

type Role = "user" | "assistant";

interface Message {
  id: string;
  role: Role;
  text: string;
  meta?: ChatResponse;
}

const SUGGESTIONS = [
  "Is SKU-1005 in stock?",
  "Where is order ORD-50003?",
  "What's the restocking fee on bulk returns?",
  "Approve a refund for order ORD-50004",
];

function newId() {
  return Math.random().toString(36).slice(2, 10);
}

export default function ChatWindow() {
  const [sessionId] = useState(() => newId());
  const [messages, setMessages] = useState<Message[]>([
    {
      id: newId(),
      role: "assistant",
      text: "Hi, I'm Scout. Ask me about inventory, shipment status, shipping costs, or warehouse policy — I'll pull live data or hand things off to your team when a decision needs a human.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setMessages((m) => [...m, { id: newId(), role: "user", text: trimmed }]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.chat(sessionId, trimmed);
      setMessages((m) => [...m, { id: newId(), role: "assistant", text: res.answer, meta: res }]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          id: newId(),
          role: "assistant",
          text: "I couldn't reach the Scout backend just now. Make sure the API server is running and try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="glass-card flex h-[70vh] flex-col overflow-hidden">
      <div ref={scrollRef} className="flex-1 space-y-5 overflow-y-auto p-6">
        {messages.map((m) => (
          <ChatBubble key={m.id} message={m} />
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-sm text-ink-muted">
            <Avatar role="assistant" />
            <span className="flex gap-1">
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-brand-cyan [animation-delay:-0.2s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-brand-cyan [animation-delay:-0.1s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-brand-cyan" />
            </span>
          </div>
        )}
      </div>

      {messages.length <= 1 && (
        <div className="flex flex-wrap gap-2 border-t border-white/5 px-6 py-3">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              className="rounded-full border border-white/10 px-3 py-1.5 text-xs text-ink-secondary transition-colors hover:border-brand-cyan/40 hover:text-ink-primary"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="flex items-center gap-3 border-t border-white/5 p-4"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about inventory, shipments, or policy..."
          className="flex-1 rounded-full border border-white/10 bg-white/[0.03] px-4 py-2.5 text-sm text-ink-primary placeholder:text-ink-muted focus:border-brand-cyan/50 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-cyan to-brand-violet text-bg transition-transform hover:scale-105 disabled:opacity-40 disabled:hover:scale-100"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}

function Avatar({ role }: { role: Role }) {
  if (role === "user") {
    return (
      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white/10 text-ink-secondary">
        <User className="h-4 w-4" />
      </span>
    );
  }
  return (
    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-cyan to-brand-violet text-bg">
      <Radar className="h-4 w-4" />
    </span>
  );
}

function ChatBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const meta = message.meta;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : ""}`}
    >
      <Avatar role={message.role} />
      <div className={`flex max-w-[75%] flex-col gap-2 ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={
            isUser
              ? "rounded-2xl rounded-tr-sm bg-gradient-to-br from-brand-cyan to-brand-violet px-4 py-2.5 text-sm font-medium text-bg"
              : "rounded-2xl rounded-tl-sm border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-ink-primary"
          }
        >
          {isUser ? message.text : <FormattedAnswer text={message.text} />}
        </div>

        {meta && (meta.blocked || meta.pii_redacted) && (
          <div className="flex flex-wrap gap-1.5">
            {meta.blocked && (
              <Badge icon={ShieldAlert} tone="warning" label={`guardrail: ${meta.block_reason?.replace(/_/g, " ")}`} />
            )}
            {meta.pii_redacted && <Badge icon={EyeOff} tone="warning" label="PII redacted" />}
          </div>
        )}

        {meta?.sources && meta.sources.length > 0 && <SourcesList sources={meta.sources} />}

        {meta?.escalation && <EscalationCard escalation={meta.escalation} />}
      </div>
    </motion.div>
  );
}

/** Renders inline `**bold**` markers as <strong>. */
function InlineText({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <>
      {parts.map((part, i) =>
        part.startsWith("**") && part.endsWith("**") ? (
          <strong key={i} className="font-semibold text-ink-primary">
            {part.slice(2, -2)}
          </strong>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}

const BULLET_RE = /^\s*[-*]\s+/;
const NUMBERED_RE = /^\s*\d+[.)]\s+/;

/**
 * Turns the assistant's raw reply into readable blocks: paragraphs stay
 * paragraphs, consecutive bullet/numbered lines become a real list — instead
 * of dumping everything as one dense wall of text.
 */
function FormattedAnswer({ text }: { text: string }) {
  const blocks = text.trim().split(/\n\s*\n/);

  return (
    <div className="space-y-3">
      {blocks.map((block, i) => {
        const lines = block.split("\n").map((l) => l.trim()).filter(Boolean);
        if (lines.length === 0) return null;

        const isBulletList = lines.every((l) => BULLET_RE.test(l));
        const isNumberedList = lines.every((l) => NUMBERED_RE.test(l));

        if (isBulletList) {
          return (
            <ul key={i} className="list-disc space-y-1 pl-5 marker:text-brand-cyan">
              {lines.map((l, j) => (
                <li key={j} className="leading-relaxed">
                  <InlineText text={l.replace(BULLET_RE, "")} />
                </li>
              ))}
            </ul>
          );
        }

        if (isNumberedList) {
          return (
            <ol key={i} className="list-decimal space-y-1 pl-5 marker:text-brand-cyan">
              {lines.map((l, j) => (
                <li key={j} className="leading-relaxed">
                  <InlineText text={l.replace(NUMBERED_RE, "")} />
                </li>
              ))}
            </ol>
          );
        }

        return (
          <p key={i} className="leading-relaxed">
            <InlineText text={lines.join(" ")} />
          </p>
        );
      })}
    </div>
  );
}

function SourcesList({ sources }: { sources: string[] }) {
  return (
    <div className="flex flex-wrap items-center gap-x-1.5 gap-y-1 text-[11px] text-ink-muted">
      <BookText className="h-3 w-3 shrink-0" />
      <span className="font-medium">Sources:</span>
      <span className="text-ink-secondary">{sources.join(" · ")}</span>
    </div>
  );
}

function Badge({
  icon: Icon,
  label,
  tone,
}: {
  icon: typeof ShieldAlert;
  label: string;
  tone: "neutral" | "warning";
}) {
  return (
    <span
      className={`flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] ${
        tone === "warning"
          ? "border-status-warning/30 text-status-warning"
          : "border-white/10 text-ink-muted"
      }`}
    >
      <Icon className="h-3 w-3" />
      {label}
    </span>
  );
}

function EscalationCard({ escalation }: { escalation: NonNullable<ChatResponse["escalation"]> }) {
  return (
    <div className="w-full rounded-xl border border-brand-violet/30 bg-brand-violet/5 p-4">
      <div className="flex items-center gap-2">
        {escalation.sent ? (
          <MailCheck className="h-4 w-4 text-status-good" />
        ) : (
          <MailWarning className="h-4 w-4 text-status-warning" />
        )}
        <span className="text-sm font-semibold text-ink-primary">
          {escalation.sent ? "Escalation email sent to your team" : "Escalation email drafted"}
        </span>
      </div>
      <p className="mt-2 text-xs font-medium text-ink-secondary">{escalation.subject}</p>
      <p className="mt-1 whitespace-pre-line text-xs text-ink-muted">{escalation.body}</p>
      <p className="mt-2 text-[11px] text-ink-muted">
        To: {escalation.to}
        {!escalation.sent && escalation.dry_run && " · dry-run: SMTP not configured yet"}
      </p>
    </div>
  );
}
