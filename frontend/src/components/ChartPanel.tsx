import { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { IconEmptyChart } from "./icons";
import { useTheme } from "../theme/ThemeContext";
import { getChartPalette } from "../theme/chartTheme";
import type { ChartData } from "../types";

const FUTURE_CHART_LOOKBACK_DAYS = 60;

interface Props {
  chart?: ChartData | null;
  instrument?: string;
  mode?: string;
  predStart?: string;
  predEnd?: string;
}

function parseTs(ts: string): number {
  return new Date(ts).getTime();
}

function maxTs(series?: { timestamps: string[] } | null): number | null {
  if (!series?.timestamps.length) return null;
  return Math.max(...series.timestamps.map(parseTs));
}

function minTs(series?: { timestamps: string[] } | null): number | null {
  if (!series?.timestamps.length) return null;
  return Math.min(...series.timestamps.map(parseTs));
}

function formatPredRange(start?: string, end?: string): string {
  if (!start || !end) return "";
  const fmt = (s: string) => {
    if (s.length === 8) return `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}`;
    return s;
  };
  return `${fmt(start)} ~ ${fmt(end)}`;
}

function ChartLegend() {
  const items = [
    { label: "历史收盘价", color: "bg-chartHistory" },
    { label: "预测收盘价", color: "bg-chartPred" },
    { label: "真实收盘价", color: "bg-chartActual" },
  ];
  return (
    <div className="mb-3 flex flex-wrap gap-4 text-xs text-muted">
      {items.map((item) => (
        <span key={item.label} className="inline-flex items-center gap-1.5">
          <span className={`legend-dot ${item.color}`} />
          {item.label}
        </span>
      ))}
    </div>
  );
}

export default function ChartPanel({ chart, instrument, mode, predStart, predEnd }: Props) {
  const { theme } = useTheme();
  const palette = useMemo(() => getChartPalette(theme), [theme]);

  if (!chart) {
    return (
      <div className="card flex h-[420px] flex-col items-center justify-center gap-3 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-elevated text-muted">
          <IconEmptyChart />
        </div>
        <div>
          <p className="text-sm font-medium">等待预测结果</p>
          <p className="mt-1 text-xs text-muted">提交预测后，这里会显示交互式 K 线对比图</p>
        </div>
      </div>
    );
  }

  const toPairs = (series: ChartData["history"]) =>
    series.timestamps.map((ts, idx) => [ts, series.close[idx]]);

  const isFuture = mode === "future";
  const lastKnownTs = chart.bridge?.timestamp || chart.history.timestamps.at(-1) || "";
  const lastPredictedTs = chart.predicted.timestamps.at(-1) || "";
  const predRangeLabel = formatPredRange(predStart, predEnd);

  let dataZoomStart: number | undefined;
  let dataZoomEnd: number | undefined;

  if (isFuture && lastKnownTs && lastPredictedTs) {
    const lastKnownMs = parseTs(lastKnownTs);
    const lastPredictedMs = parseTs(lastPredictedTs);
    dataZoomStart = lastKnownMs - FUTURE_CHART_LOOKBACK_DAYS * 24 * 60 * 60 * 1000;
    dataZoomEnd = lastPredictedMs + 2 * 24 * 60 * 60 * 1000;
  } else if (chart.actual && lastKnownTs) {
    const focusStart = minTs(chart.history);
    const focusEnd = maxTs(chart.actual) ?? maxTs(chart.predicted);
    if (focusStart != null && focusEnd != null) {
      const span = focusEnd - focusStart;
      dataZoomStart = focusEnd - Math.min(span, 90 * 24 * 60 * 60 * 1000);
      dataZoomEnd = focusEnd + 24 * 60 * 60 * 1000;
    }
  }

  const titleText = isFuture
    ? instrument
      ? `${instrument} 未来预测${predRangeLabel ? ` · ${predRangeLabel}` : ""}`
      : `未来预测${predRangeLabel ? ` · ${predRangeLabel}` : ""}`
    : instrument
      ? `${instrument} 预测 vs 真实`
      : "预测 vs 真实";

  const markLine =
    lastKnownTs && isFuture
      ? {
          symbol: "none",
          label: { formatter: "最后已知K线", color: palette.muted, fontSize: 10 },
          lineStyle: { color: palette.markLine, type: "dashed" },
          data: [{ xAxis: lastKnownTs }],
        }
      : undefined;

  const option = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis",
      backgroundColor: palette.tooltipBg,
      borderColor: palette.tooltipBorder,
      textStyle: { color: palette.tooltipText, fontSize: 12 },
    },
    legend: { show: false },
    grid: { left: 48, right: 24, top: 40, bottom: 48 },
    xAxis: {
      type: "time",
      axisLabel: { color: palette.muted, fontSize: 11 },
      axisLine: { lineStyle: { color: palette.axis } },
    },
    yAxis: {
      type: "value",
      scale: true,
      axisLabel: { color: palette.muted, fontSize: 11 },
      splitLine: { lineStyle: { color: palette.grid } },
    },
    dataZoom: [
      {
        type: "inside",
        ...(dataZoomStart != null && dataZoomEnd != null
          ? { startValue: dataZoomStart, endValue: dataZoomEnd }
          : {}),
      },
      {
        type: "slider",
        height: 20,
        bottom: 8,
        borderColor: palette.dataZoomBorder,
        fillerColor: palette.dataZoomFill,
        handleStyle: { color: palette.dataZoomHandle },
        textStyle: { color: palette.muted },
        ...(dataZoomStart != null && dataZoomEnd != null
          ? { startValue: dataZoomStart, endValue: dataZoomEnd }
          : {}),
      },
    ],
    series: [
      {
        name: "历史收盘价",
        type: "line",
        smooth: true,
        showSymbol: false,
        lineStyle: { color: palette.history, width: 2 },
        data: toPairs(chart.history),
        markLine,
      },
      {
        name: "预测收盘价",
        type: "line",
        smooth: true,
        symbolSize: 6,
        lineStyle: { color: palette.predicted, width: 2, type: "dashed" },
        itemStyle: { color: palette.predicted },
        data: toPairs(chart.predicted),
      },
      ...(chart.actual
        ? [
            {
              name: "真实收盘价",
              type: "line",
              smooth: true,
              symbolSize: 6,
              lineStyle: { color: palette.actual, width: 2 },
              itemStyle: { color: palette.actual },
              data: toPairs(chart.actual),
            },
          ]
        : []),
    ],
    title: {
      text: titleText,
      left: 0,
      textStyle: { color: palette.text, fontSize: 14, fontWeight: 600, fontFamily: "Inter" },
    },
  };

  return (
    <div className="card-highlight">
      <ChartLegend />
      {isFuture && predRangeLabel && (
        <p className="mb-3 rounded-lg bg-accent/10 px-3 py-2 text-xs text-accent">
          预测区间延伸至 {predRangeLabel}（最后一根 K 线之后）
        </p>
      )}
      <ReactECharts option={option} style={{ height: 420, width: "100%" }} notMerge lazyUpdate />
    </div>
  );
}
