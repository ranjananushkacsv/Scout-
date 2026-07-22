"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Radar } from "lucide-react";
import clsx from "clsx";

const LINKS = [
  { href: "/#features", label: "Features" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/assistant", label: "AI Assistant" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="fixed top-0 z-50 w-full border-b border-white/5 bg-bg/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-cyan to-brand-violet shadow-glow">
            <Radar className="h-5 w-5 text-bg" strokeWidth={2.5} />
          </span>
          <span className="text-lg font-semibold tracking-tight text-ink-primary">
            Scout
          </span>
        </Link>

        <nav className="hidden items-center gap-8 md:flex">
          {LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={clsx(
                "text-sm font-medium transition-colors hover:text-ink-primary",
                pathname === link.href ? "text-ink-primary" : "text-ink-secondary"
              )}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <Link
          href="/assistant"
          className="rounded-full bg-gradient-to-r from-brand-cyan to-brand-violet px-4 py-2 text-sm font-semibold text-bg transition-transform hover:scale-105"
        >
          Talk to Scout
        </Link>
      </div>
    </header>
  );
}
