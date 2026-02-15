import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#FF6B8A",
          dark: "#E8527A",
          light: "#FFB3C6",
        },
        secondary: "#6C5CE7",
        accent: "#00D2D3",
        success: "#00B894",
        danger: "#FF6B6B",
        warning: "#FDCB6E",
        "app-bg": "#FAFAFA",
        "app-card": "#FFFFFF",
        "app-text": "#1A1A2E",
        "app-text-light": "#6B7280",
        "app-border": "#F3E8FF",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
      },
      borderRadius: {
        "xl": "16px",
        "2xl": "20px",
        "3xl": "24px",
      },
    },
  },
  plugins: [],
};

export default config;
