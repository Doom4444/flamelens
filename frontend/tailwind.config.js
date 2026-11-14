/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        aerospace: {
          bg: "#080F1C",
          sidebar: "#0C1626",
          card: "#111E30",
          cardHover: "#16253C",
          border: "#243449",
          borderLight: "#334760",
          cyan: "#35C6E8",
          orange: "#FF914D",
          textPrimary: "#F4F7FB",
          textSecondary: "#94A3B8",
          textMuted: "#64748B",
        },
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          'sans-serif',
        ],
        mono: [
          '"JetBrains Mono"',
          'ui-monospace',
          'SFMono-Regular',
          'Menlo',
          'Monaco',
          'Consolas',
          'monospace',
        ],
      },
    },
  },
  plugins: [],
}
