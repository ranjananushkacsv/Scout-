"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, ShieldCheck, Sparkles, Zap } from "lucide-react";

const PILLS = [
  { icon: Sparkles, label: "Grounded RAG answers" },
  { icon: Zap, label: "Live inventory & shipment data" },
  { icon: ShieldCheck, label: "Human-in-the-loop guardrails" },
];

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-hero-glow bg-grid">
      <div className="absolute inset-0 bg-grid-fade" />

      <div className="relative mx-auto flex max-w-5xl flex-col items-center px-6 pb-28 pt-32 text-center md:pt-40">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs font-medium text-ink-secondary"
        >
          <span className="h-1.5 w-1.5 animate-pulse-slow rounded-full bg-brand-cyan" />
          Now watching inventory, shipments &amp; carrier data in real time
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1 }}
          className="text-4xl font-bold leading-[1.1] tracking-tight text-ink-primary sm:text-6xl"
        >
          The AI copilot for your{" "}
          <span className="gradient-text">operations</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="mt-6 max-w-2xl text-lg text-ink-secondary"
        >
          Scout reads your inventory, shipments, and carrier data, answers
          operational questions instantly, and knows exactly when to stop and
          bring in a human — drafting and sending the approval email itself.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="mt-10 flex flex-col items-center gap-4 sm:flex-row"
        >
          <Link
            href="/assistant"
            className="group flex items-center gap-2 rounded-full bg-gradient-to-r from-brand-cyan to-brand-violet px-6 py-3 font-semibold text-bg shadow-glow transition-transform hover:scale-105"
          >
            Talk to Scout
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Link>
          <Link
            href="/dashboard"
            className="rounded-full border border-white/15 px-6 py-3 font-semibold text-ink-primary transition-colors hover:bg-white/5"
          >
            Explore the dashboard
          </Link>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.45 }}
          className="mt-16 flex flex-wrap items-center justify-center gap-3"
        >
          {PILLS.map(({ icon: Icon, label }) => (
            <div
              key={label}
              className="glass-card flex items-center gap-2 px-4 py-2 text-sm text-ink-secondary"
            >
              <Icon className="h-4 w-4 text-brand-cyan" />
              {label}
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
