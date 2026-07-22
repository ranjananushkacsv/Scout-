"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

export default function CtaSection() {
  return (
    <section className="relative overflow-hidden py-24">
      <div className="mx-auto max-w-4xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="glass-card relative overflow-hidden px-8 py-14 text-center sm:px-16"
        >
          <div className="pointer-events-none absolute inset-0 bg-hero-glow" />
          <div className="relative">
            <h2 className="text-3xl font-bold text-ink-primary sm:text-4xl">
              See your supply chain through Scout
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-ink-secondary">
              Open the dashboard for a live read on inventory and shipments,
              or start a conversation with the assistant.
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Link
                href="/dashboard"
                className="rounded-full bg-gradient-to-r from-brand-cyan to-brand-violet px-6 py-3 font-semibold text-bg shadow-glow transition-transform hover:scale-105"
              >
                Open dashboard
              </Link>
              <Link
                href="/assistant"
                className="group flex items-center gap-2 rounded-full border border-white/15 px-6 py-3 font-semibold text-ink-primary transition-colors hover:bg-white/5"
              >
                Chat with Scout
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
