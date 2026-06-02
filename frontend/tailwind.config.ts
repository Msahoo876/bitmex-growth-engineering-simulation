import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#050505",
        panel: "#0d0f0e",
        border: "#202621",
        muted: "#9aa39c",
        primary: "#00d084",
        accent: "#00b7c7",
        warning: "#f6b44b",
        danger: "#ff5c5c"
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(0,208,132,.2), 0 16px 40px rgba(0,0,0,.35)"
      }
    }
  },
  plugins: []
} satisfies Config;
