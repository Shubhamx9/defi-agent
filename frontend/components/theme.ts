import { type Theme } from "@coinbase/cdp-react/theme";

export const theme: Partial<Theme> = {
  // Background colors
  "colors-bg-default": "rgba(255, 255, 255, 0.05)", // translucent dark
  "colors-bg-overlay": "rgba(15, 23, 42, 0.9)", // slate-900 overlay
  "colors-bg-skeleton": "rgba(255, 255, 255, 0.08)",

  // Primary surfaces
  "colors-bg-primary": "linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)", // blue → purple gradient
  "colors-bg-secondary": "rgba(255, 255, 255, 0.08)",

  // Foreground (text/icons)
  "colors-fg-default": "#F8FAFC", // slate-50
  "colors-fg-muted": "#94A3B8",   // slate-400
  "colors-fg-primary": "#60A5FA", // blue-400
  "colors-fg-onPrimary": "#FFFFFF",
  "colors-fg-onSecondary": "#E2E8F0", // slate-200

  // Borders
  "colors-line-default": "rgba(255, 255, 255, 0.1)",
  "colors-line-heavy": "rgba(255, 255, 255, 0.2)",
  "colors-line-primary": "#3B82F6",

  // Typography
  "font-family-sans": "Inter, sans-serif",
  "font-size-base": "14px",
};
