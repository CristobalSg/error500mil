/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        // tailwindcss-animate
      },
      colors: {
        primary: {
          light: "#6366f1", // indigo-500
          dark: "#7e22ce",  // purple-700
        },
        secondary: {
          light: "#4b5563", // gray-600
          dark: "#111827",  // gray-900
        },
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
      screens: {
        sm: "640px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
