import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0B1220",
        panel: "#121B2E",
        panel2: "#182236",
        line: "#243450",
        accent: "#4F8CFF",
        accent2: "#7CE3C8",
        warn: "#F2B85C",
        danger: "#F26D6D",
        muted: "#8CA0C4",
      },
      fontFamily: {
        display: ["'Sora'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
      },
      borderRadius: {
        xl2: "1.25rem",
      },
    },
  },
  plugins: [],
};
export default config;
