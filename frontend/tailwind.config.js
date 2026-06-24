/** CastCore Tailwind config — wired to the corporate-design brand tokens. */
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // CastCore brand palette (see branding/brand/brand-tokens.json)
        "core-green": "#22C55E",
        "signal-cyan": "#06B6D4",
        "control-blue": "#3B82F6",
        "deep-navy": "#07111F",
        "panel-navy": "#111C2E",
        slate: "#64748B",
        mist: "#E2E8F0",
        warning: "#F59E0B",
        danger: "#EF4444"
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "sans-serif"]
      }
    }
  },
  plugins: []
};
