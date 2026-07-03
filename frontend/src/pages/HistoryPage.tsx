import { useEffect, useState } from "react";
import { listPredictions } from "../api/client";
import ChartPanel from "../components/ChartPanel";
import { IconEmptyChart } from "../components/icons";
import MetricCards from "../components/MetricCards";
import ResultPanel from "../components/ResultPanel";
import SectionHeader from "../components/SectionHeader";
import { HistoryListSkeleton } from "../components/Skeleton";
import type { ChartData, HistoryItem, PredictResult } from "../types";

interface Props {
  onOpenResult: (result: PredictResult) => void;
}

const emptyChart: ChartData = {
  history: { timestamps: [], close: [] },
  predicted: { timestamps: [], close: [] },
  actual: null,
  bridge: { timestamp: "", close: 0 },
};

function chartFromItem(item: HistoryItem): ChartData {
  if (item.chart_complete && item.chart) {
    return {
      history: item.chart.history ?? emptyChart.history,
      predicted: item.chart.predicted ?? emptyChart.predicted,
      actual: item.chart.actual ?? null,
      bridge: item.chart.bridge ?? emptyChart.bridge,
    };
  }
  return {
    ...emptyChart,
    predicted: item.chart?.predicted ?? emptyChart.predicted,
  };
}

export default function HistoryPage({ onOpenResult }: Props) {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [selected, setSelected] = useState<{ item: HistoryItem; result: PredictResult } | null>(null);

  useEffect(() => {
    listPredictions()
      .then((res) => setItems(res.items))
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false));
  }, []);

  const openItem = (item: HistoryItem) => {
    const result: PredictResult = {
      instrument: item.instrument,
      mode: item.mode ?? "unknown",
      csv_path: item.csv_path,
      chart_path: item.png_path ?? "",
      metrics: item.metrics ?? null,
      predictions: [],
      chart: chartFromItem(item),
      pred_start: item.pred_start,
      pred_end: item.pred_end,
    };
    setSelected({ item, result });
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[360px,1fr]">
      <div className="card space-y-4">
        <SectionHeader title="历史预测" subtitle={`共 ${items.length} 条记录`} />
        {loading && <HistoryListSkeleton />}
        {error && (
          <p className="rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p>
        )}
        {!loading && items.length === 0 && (
          <div className="py-8 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-elevated text-muted">
              <IconEmptyChart className="h-6 w-6" />
            </div>
            <p className="mt-3 text-sm text-muted">暂无历史记录</p>
          </div>
        )}
        <div className="space-y-2">
          {items.map((item) => {
            const active = selected?.item.id === item.id;
            return (
              <button
                key={item.id}
                type="button"
                className={active ? "history-item-active" : "history-item"}
                onClick={() => openItem(item)}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium">{item.instrument}</span>
                  <span className="numeric text-xs text-muted">{item.run_timestamp}</span>
                </div>
                <p className="mt-1 text-xs text-muted">
                  pred {item.pred_start}-{item.pred_end} · w{item.window} h{item.horizon}
                  {item.metrics ? ` · MAPE ${item.metrics.mape.toFixed(2)}%` : ""}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      <div className="space-y-4">
        {selected ? (
          <>
            <div className="flex flex-wrap gap-3">
              <button type="button" className="btn-primary" onClick={() => onOpenResult(selected.result)}>
                在预测页打开
              </button>
            </div>
            {!selected.item.chart_complete && (
              <div className="rounded-lg border border-warning/30 bg-warning/10 px-3 py-2 text-xs text-warning">
                该记录为旧格式，仅含预测曲线。重新运行一次回测/预测可保存完整图表（含历史与真实对比线）。
              </div>
            )}
            <ChartPanel
              chart={selected.result.chart}
              instrument={selected.result.instrument}
              mode={selected.result.mode}
              predStart={selected.result.pred_start}
              predEnd={selected.result.pred_end}
            />
            <MetricCards metrics={selected.result.metrics} showBacktestNote={!!selected.result.metrics} />
            {selected.result.csv_path && (
              <ResultPanel
                result={{
                  ...selected.result,
                  predictions: selected.result.chart.predicted.timestamps.map((ts, idx) => ({
                    timestamps: ts,
                    close: selected.result.chart.predicted.close[idx],
                  })),
                }}
              />
            )}
          </>
        ) : (
          <div className="card flex h-[320px] flex-col items-center justify-center gap-3 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-elevated text-muted">
              <IconEmptyChart className="h-6 w-6" />
            </div>
            <p className="text-sm text-muted">选择一条历史记录查看详情</p>
          </div>
        )}
      </div>
    </div>
  );
}
