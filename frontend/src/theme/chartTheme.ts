import type { Theme } from "./ThemeContext";

export interface ChartPalette {
  text: string;
  muted: string;
  grid: string;
  axis: string;
  tooltipBg: string;
  tooltipBorder: string;
  tooltipText: string;
  dataZoomBorder: string;
  dataZoomFill: string;
  dataZoomHandle: string;
  markLine: string;
  history: string;
  predicted: string;
  actual: string;
  bar: string;
  barMuted: string;
  barBest: string;
}

export function getChartPalette(theme: Theme): ChartPalette {
  if (theme === "dark") {
    return {
      text: "#ededf5",
      muted: "#94a3b8",
      grid: "rgba(255,255,255,0.06)",
      axis: "rgba(255,255,255,0.1)",
      tooltipBg: "rgba(22,26,46,0.96)",
      tooltipBorder: "rgba(129,140,248,0.25)",
      tooltipText: "#ededf5",
      dataZoomBorder: "rgba(129,140,248,0.2)",
      dataZoomFill: "rgba(129,140,248,0.18)",
      dataZoomHandle: "#818cf8",
      markLine: "rgba(148,163,184,0.5)",
      history: "#94a3b8",
      predicted: "#fb7185",
      actual: "#22d3ee",
      bar: "rgba(129,140,248,0.45)",
      barMuted: "rgba(100,116,139,0.35)",
      barBest: "#818cf8",
    };
  }

  return {
    text: "#312e81",
    muted: "#64748b",
    grid: "rgba(49,46,129,0.06)",
    axis: "rgba(49,46,129,0.12)",
    tooltipBg: "rgba(255,255,255,0.98)",
    tooltipBorder: "rgba(199,210,254,1)",
    tooltipText: "#312e81",
    dataZoomBorder: "rgba(199,210,254,1)",
    dataZoomFill: "rgba(99,102,241,0.12)",
    dataZoomHandle: "#6366f1",
    markLine: "rgba(100,116,139,0.45)",
    history: "#475569",
    predicted: "#f43f5e",
    actual: "#06b6d4",
    bar: "rgba(99,102,241,0.35)",
    barMuted: "rgba(148,163,184,0.35)",
    barBest: "#6366f1",
  };
}
