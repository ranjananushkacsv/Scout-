"use client";

import { motion } from "framer-motion";
import { MessageCircle, ShieldAlert, MailCheck, UserCheck } from "lucide-react";

const STEPS = [
  {
    icon: MessageCircle,
    title: "A request comes in",
    description: '"Approve a refund for order ORD-50003"',
  },
  {
    icon: ShieldAlert,
    title: "Scout recognizes it needs a human",
    description:
      "Guardrails flag it as a write/approval action outside the assistant's authority — before the model ever acts on it.",
  },
  {
    icon: MailCheck,
    title: "Scout drafts the email",
    description:
      "Subject, context, and reason for escalation are generated automatically and logged to the dashboard.",
  },
  {
    icon: UserCheck,
    title: "Your team approves",
    description:
      "The email lands in your inbox — nothing is approved, cancelled, or overridden without a person saying yes.",
  },
];

export default function EscalationShowcase() {
  return (
    <section className="relative bg-bg py-28">
      <div className="mx-auto max-w-6xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="mx-auto max-w-2xl text-center"
        >
          <span className="text-sm font-semibold uppercase tracking-widest text-brand-violet">
            Human in the loop
          </span>
          <h2 className="mt-3 text-3xl font-bold text-ink-primary sm:text-4xl">
            Scout never makes the call it isn&apos;t allowed to make
          </h2>
          <p className="mt-4 text-ink-secondary">
            Every action that changes a record — a refund, a cancellation, an
            override — is routed to your team automatically, with the full
            context already written up.
          </p>
        </motion.div>

        <div className="relative mt-16 grid gap-6 md:grid-cols-4">
          <div className="absolute left-0 right-0 top-9 hidden h-px bg-gradient-to-r from-transparent via-white/15 to-transparent md:block" />
          {STEPS.map((step, i) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.12 }}
              className="relative flex flex-col items-center text-center"
            >
              <div className="relative z-10 flex h-[72px] w-[72px] items-center justify-center rounded-2xl border border-white/10 bg-surface shadow-card">
                <step.icon className="h-7 w-7 text-brand-cyan" />
                <span className="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-brand-cyan to-brand-violet text-xs font-bold text-bg">
                  {i + 1}
                </span>
              </div>
              <h3 className="mt-5 text-base font-semibold text-ink-primary">
                {step.title}
              </h3>
              <p className="mt-2 text-sm text-ink-secondary">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
