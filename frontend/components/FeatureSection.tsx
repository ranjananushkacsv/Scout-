"use client";

import { motion } from "framer-motion";
import {
  BarChart3,
  BrainCircuit,
  DatabaseZap,
  MailCheck,
  MessageSquareText,
  ShieldAlert,
} from "lucide-react";

const FEATURES = [
  {
    icon: DatabaseZap,
    title: "Always up to date",
    description:
      "Stock levels, shipments, and carrier rates — pulled live, never a stale snapshot.",
  },
  {
    icon: BrainCircuit,
    title: "Answers you can trust",
    description:
      "Scout only answers from your own documents. If it's not in there, it says so instead of guessing.",
  },
  {
    icon: MessageSquareText,
    title: "Checks real data first",
    description:
      "Before answering, Scout looks up the actual SKU, order, or rate — no made-up numbers.",
  },
  {
    icon: ShieldAlert,
    title: "Built-in safety checks",
    description:
      "Sketchy prompts, off-topic asks, and private data are caught before they cause problems.",
  },
  {
    icon: MailCheck,
    title: "Knows when to ask a human",
    description:
      "Refunds, cancellations, overrides — Scout hands these to your team by email instead of guessing.",
  },
  {
    icon: BarChart3,
    title: "One dashboard, full picture",
    description:
      "Stock, shipments, carriers, and every escalation — all in one place.",
  },
];

export default function FeatureSection() {
  return (
    <section id="features" className="relative bg-bg py-28">
      <div className="mx-auto max-w-6xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="mx-auto max-w-2xl text-center"
        >
          <span className="text-sm font-semibold uppercase tracking-widest text-brand-cyan">
            Platform
          </span>
          <h2 className="mt-3 text-3xl font-bold text-ink-primary sm:text-4xl">
            Everything an operations team needs from an AI copilot
          </h2>
          <p className="mt-4 text-ink-secondary">
            One guarded agent, grounded in your data, that knows the
            difference between "look this up" and "someone needs to sign off
            on this."
          </p>
        </motion.div>

        <div className="mt-16 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: (i % 3) * 0.08 }}
              className="glass-card group p-6 transition-colors hover:border-brand-cyan/30"
            >
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-brand-cyan/20 to-brand-violet/20 text-brand-cyan">
                <feature.icon className="h-5 w-5" />
              </div>
              <h3 className="mt-4 text-lg font-semibold text-ink-primary">
                {feature.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-ink-secondary">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
