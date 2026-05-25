import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}", "./lib/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        pitch: {
          950: "#050b0b",
          900: "#071312",
          800: "#0d201e",
          700: "#14302d"
        },
        neon: {
          400: "#40f6a3",
          500: "#22d483"
        }
      },
      boxShadow: {
        glow: "0 0 40px rgba(34, 212, 131, 0.16)"
      }
    }
  },
  plugins: []
};

export default config;
