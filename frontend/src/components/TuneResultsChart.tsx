import { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { useTheme } from "../theme/ThemeContext";
import { getChartPalette } from "../theme/chartTheme";
import type { TuneRow } from "../types";

interface Props {
  results: TuneRow[];
  bestRmse?: number;
}

function comboLabel(row: TuneRow): string {
  return `w${row.window}/T${row.T}/p${row.top_p}/s${row.sample_count}`;
}

export default function TuneResultsChart({ results, bestRmse }: Props) {
  const { theme } = useTheme();
  const palette = useMemo(() => getChartPalette(theme), [theme]);

  const chartData = useMemo(() => {
    return [...results].sort((a, b) => a.mape - b.mape).slice(0, 10);
  }, [results]);

  if (chartData.length === 0) return null;

  const labels = chartData.map(comboLabel);
  const values = chartData.map((r) => r.mape);
  const colors = chartData.map((r) =>
    bestRmse !== undefined && r.rmse === bestRmse ? palette.barBest : palette.bar,
  );

  const option = {
    backgroundColor: "transparent",
    title: {
      text: "Top 10 组合 MAPE 对比",
      left: 0,
      textStyle: { color: palette.text, fontSize: 14, fontWeight: 600, fontFamily: "Inter" },
    },
    tooltip: {
      trigger: "axis",
      backgroundColor: palette.tooltipBg,
      borderColor: palette.tooltipBorder,
      textStyle: { color: palette.tooltipText, fontSize: 12 },
      formatter: (params: { dataIndex: number; value: number }[]) => {
        const idx = params[0]?.dataIndex ?? 0;
        const row = chartData[idx];
        if (!row) return "";
        return [
          comboLabel(row),
          `MAPE: ${row.mape.toFixed(2)}%`,
          `MAE: ${row.mae.toFixed(4)} · RMSE: ${row.rmse.toFixed(4)}`,
        ].join("<br/>");
      },
    },
    grid: { left: 48, right: 16, top: 48, bottom: 72 },
    xAxis: {
      type: "category",
      data: labels,
      axisLabel: {
        color: palette.muted,
        rotate: 35,
        fontSize: 10,
        formatter: (v: string) => (v.length > 18 ? `${v.slice(0, 16)}…` : v),
      },
      axisLine: { lineStyle: { color: palette.axis } },
    },
    yAxis: {
      type: "value",
      name: "MAPE (%)",
      nameTextStyle: { color: palette.muted },
      axisLabel: { color: palette.muted },
      splitLine: { lineStyle: { color: palette.grid } },
    },
    series: [
      {
        type: "bar",
        data: values.map((v, i) => ({
          value: v,
          itemStyle: { color: colors[i], borderRadius: [4, 4, 0, 0] },
        })),
      },
    ],
  };

  return (
    <div className="card">
      <ReactECharts option={option} style={{ height: 320, width: "100%" }} notMerge lazyUpdate />
    </div>
  );
}
