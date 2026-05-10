/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#1a1816",
        surface: "rgba(42, 38, 34, 0.7)",
        "surface-solid": "#2a2622",
        border: "rgba(82, 74, 62, 0.4)",
        accent: "#7c9a72",
        "accent-hover": "#6b8a62",
        muted: "#a89882",
        warm: "#c4a882",
        terracotta: "#b87356",
      },
      backdropBlur: {
        glass: "16px",
      },
      borderRadius: {
        japandi: "12px",
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
