import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#05070d",
        surface: "#0b0f1c",
        surface2: "#111730",
        border: "rgba(255,255,255,0.08)",
        ink: {
          primary: "#f4f7fb",
          secondary: "#a6b0c8",
          muted: "#6d7690",
        },
        brand: {
          cyan: "#22d3ee",
          violet: "#8b5cf6",
          indigo: "#5865f2",
        },
        chart: {
          blue: "#3987e5",
          orange: "#d95926",
          aqua: "#199e70",
          yellow: "#c98500",
          magenta: "#d55181",
          green: "#008300",
          violet: "#9085e9",
          red: "#e66767",
        },
        status: {
          good: "#0ca30c",
          warning: "#fab219",
          serious: "#ec835a",
          critical: "#d03b3b",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "grid-fade":
          "linear-gradient(to bottom, rgba(5,7,13,0) 0%, rgba(5,7,13,1) 85%), radial-gradient(circle at 50% 0%, rgba(139,92,246,0.18), transparent 60%)",
        "hero-glow":
          "radial-gradient(600px circle at 20% 10%, rgba(34,211,238,0.15), transparent 60%), radial-gradient(500px circle at 85% 25%, rgba(139,92,246,0.18), transparent 60%)",
      },
      boxShadow: {
        glow: "0 0 40px -10px rgba(34,211,238,0.35)",
        card: "0 4px 24px -8px rgba(0,0,0,0.5)",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        "pulse-slow": {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        "pulse-slow": "pulse-slow 4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
