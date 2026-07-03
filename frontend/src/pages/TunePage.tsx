import { useEffect, useMemo, useRef, useState } from "react";
import { createTuneJob, downloadUrl, getJob } from "../api/client";
import JobStatusPanel from "../components/JobStatusPanel";
import ParamHelpField from "../components/ParamHelpField";
import TuneContextBanner from "../components/TuneContextBanner";
import TuneEmptyState from "../components/TuneEmptyState";
import TuneGuidePanel from "../components/TuneGuidePanel";
import TunePresetPicker from "../components/TunePresetPicker";
import TuneResultsChart from "../components/TuneResultsChart";
import {
  estimateTuneWorkload,
  metricHelp,
  tuneParamHelp,
  type TunePreset,
} from "../content/paramHelp";
import type { PredictFormValues, TuneRow } from "../types";

interface Props {
  form: PredictFormValues;
  setForm: (value: PredictFormValues) => void;
  onApplyBest: (value: PredictFormValues) => void;
}

type SortKey = "window" | "T" | "top_p" | "sample_count" | "mae" | "rmse" | "mape";
type SortDir = "asc" | "desc";

const sortColumns: { key: SortKey; label: string; metric?: boolean }[] = [
  { key: "window", label: "窗口" },
  { key: "T", label: "温度" },
  { key: "top_p", label: "top_p" },
  { key: "sample_count", label: "采样" },
  { key: "mae", label: "MAE", metric: true },
  { key: "rmse", label: "RMSE", metric: true },
  { key: "mape", label: "MAPE", metric: true },
];

export default function TunePage({ form, setForm, onApplyBest }: Props) {
  const [presetId, setPresetId] = useState<TunePreset["id"]>("standard");
  const [gridWindow, setGridWindow] = useState("64,128,256");
  const [gridTemp, setGridTemp] = useState("1.0,0.9");
  const [gridTopP, setGridTopP] = useState("0.95,0.9");
  const [gridSampleCount, setGridSampleCount] = useState("1,5");
  const [tuneStride, setTuneStride] = useState(5);
  const [tuneMaxWindows, setTuneMaxWindows] = useState(120);
  const [status, setStatus] = useState<string>();
  const [message, setMessage] = useState<string>();
  const [progress, setProgress] = useState<number>();
  const [error, setError] = useState<string>();
  const [results, setResults] = useState<TuneRow[]>([]);
  const [best, setBest] = useState<TuneRow | null>(null);
  const [csvPath, setCsvPath] = useState<string>();
  const [submitting, setSubmitting] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>("mape");
  const [sortDir, setSortDir] = useState<SortDir>("asc");
  const pollRef = useRef<number | null>(null);

  const workload = useMemo(
    () =>
      estimateTuneWorkload({
        grid_window: gridWindow,
        grid_temp: gridTemp,
        grid_top_p: gridTopP,
        grid_sample_count: gridSampleCount,
        tune_max_windows: tuneMaxWindows,
      }),
    [gridWindow, gridTemp, gridTopP, gridSampleCount, tuneMaxWindows],
  );

  const sortedResults = useMemo(() => {
    const copy = [...results];
    copy.sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      const cmp = av < bv ? -1 : av > bv ? 1 : 0;
      return sortDir === "asc" ? cmp : -cmp;
    });
    return copy;
  }, [results, sortKey, sortDir]);

  useEffect(
    () => () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    },
    [],
  );

  const applyPreset = (preset: TunePreset) => {
    setPresetId(preset.id);
    setGridWindow(preset.grid_window);
    setGridTemp(preset.grid_temp);
    setGridTopP(preset.grid_top_p);
    setGridSampleCount(preset.grid_sample_count);
    setTuneStride(preset.tune_stride);
    setTuneMaxWindows(preset.tune_max_windows);
  };

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir(key === "mape" || key === "mae" || key === "rmse" ? "asc" : "desc");
    }
  };

  const pollJob = (id: string) => {
    if (pollRef.current) window.clearInterval(pollRef.current);
    pollRef.current = window.setInterval(async () => {
      try {
        const job = await getJob(id);
        setStatus(job.status);
        setMessage(job.message);
        setProgress(job.progress);
        setError(job.error);
        if (job.status === "done" && job.result) {
          const payload = job.result as { results: TuneRow[]; best: TuneRow; csv_path?: string };
          setResults(payload.results);
          setBest(payload.best);
          setCsvPath(payload.csv_path);
          setSortKey("mape");
          setSortDir("asc");
          setSubmitting(false);
          if (pollRef.current) window.clearInterval(pollRef.current);
        }
        if (job.status === "failed") {
          setSubmitting(false);
          if (pollRef.current) window.clearInterval(pollRef.current);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
        setSubmitting(false);
        if (pollRef.current) window.clearInterval(pollRef.current);
      }
    }, 1500);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(undefined);
    setResults([]);
    setBest(null);
    setCsvPath(undefined);
    try {
      const { job_id } = await createTuneJob({
        ...form,
        grid_window: gridWindow,
        grid_temp: gridTemp,
        grid_top_p: gridTopP,
        grid_sample_count: gridSampleCount,
        tune_stride: tuneStride,
        tune_max_windows: tuneMaxWindows,
      });
      setStatus("queued");
      pollJob(job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setSubmitting(false);
    }
  };

  const applyBest = () => {
    if (!best) return;
    onApplyBest({
      ...form,
      window: best.window,
      temperature: best.T,
      top_p: best.top_p,
      sample_count: best.sample_count,
    });
    setForm({
      ...form,
      window: best.window,
      temperature: best.T,
      top_p: best.top_p,
      sample_count: best.sample_count,
    });
  };

  const bestRmse = best?.rmse;
  const showEmptyState = results.length === 0 && !submitting;

  return (
    <div className="space-y-4">
      <TuneContextBanner form={form} />

      <div className="grid gap-6 lg:grid-cols-[360px,1fr,280px]">
        <div className="card space-y-4">
          <div>
            <h2 className="text-lg font-semibold">网格调参</h2>
            <p className="text-sm text-muted">基于当前股票与日期区间做滚动回测，耗时较长。</p>
          </div>

          <TunePresetPicker selected={presetId} onSelect={applyPreset} />

          <ParamHelpField help={tuneParamHelp.grid_window} value={gridWindow} onChange={setGridWindow} />
          <ParamHelpField help={tuneParamHelp.grid_temp} value={gridTemp} onChange={setGridTemp} />
          <ParamHelpField help={tuneParamHelp.grid_top_p} value={gridTopP} onChange={setGridTopP} />
          <ParamHelpField
            help={tuneParamHelp.grid_sample_count}
            value={gridSampleCount}
            onChange={setGridSampleCount}
          />
          <ParamHelpField
            help={tuneParamHelp.tune_stride}
            value={String(tuneStride)}
            onChange={(v) => setTuneStride(Number(v))}
            type="number"
          />
          <ParamHelpField
            help={tuneParamHelp.tune_max_windows}
            value={String(tuneMaxWindows)}
            onChange={(v) => setTuneMaxWindows(Number(v))}
            type="number"
          />

          <div className="rounded-lg bg-elevated px-3 py-2 text-xs text-muted">{workload.label}</div>

          <button className="btn-primary w-full" disabled={submitting} onClick={handleSubmit}>
            {submitting ? "调参进行中..." : "开始调参"}
          </button>
        </div>

        <div className="space-y-4">
          <JobStatusPanel status={status} message={message} progress={progress} error={error} />

          {showEmptyState && <TuneEmptyState />}

          {best && (
            <div className="card-highlight flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-sm font-medium">最优参数（按 RMSE 最小）</p>
                <p className="numeric text-sm text-muted">
                  窗口={best.window}, 温度={best.T}, top_p={best.top_p}, 采样={best.sample_count} · MAPE=
                  {best.mape.toFixed(2)}%
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                {csvPath && (
                  <a className="btn-ghost" href={downloadUrl(csvPath)}>
                    下载 CSV
                  </a>
                )}
                <button className="btn-primary" onClick={applyBest}>
                  应用到预测表单
                </button>
              </div>
            </div>
          )}

          {results.length > 0 && (
            <>
              <TuneResultsChart results={results} bestRmse={bestRmse} />
              <div className="card overflow-x-auto">
                <p className="mb-3 text-xs text-muted">
                  点击列头排序 · 默认 MAPE 升序 · 最优行（RMSE 最小）高亮
                </p>
                <table className="min-w-full text-left text-sm">
                  <thead className="text-xs uppercase text-muted">
                    <tr>
                      <th className="px-3 py-2">标记</th>
                      {sortColumns.map((col) =>
                        col.metric ? (
                          <MetricSortHeader
                            key={col.key}
                            keyName={col.key as "mae" | "rmse" | "mape"}
                            active={sortKey === col.key}
                            dir={sortDir}
                            onSort={() => toggleSort(col.key)}
                          />
                        ) : (
                          <SortHeader
                            key={col.key}
                            label={col.label}
                            active={sortKey === col.key}
                            dir={sortDir}
                            onSort={() => toggleSort(col.key)}
                          />
                        ),
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {sortedResults.map((row, idx) => {
                      const isBest = bestRmse !== undefined && row.rmse === bestRmse;
                      return (
                        <tr
                          key={idx}
                          className={`border-t border-border ${isBest ? "bg-accent/10" : ""}`}
                        >
                          <td className="px-3 py-2">
                            {isBest && (
                              <span className="rounded bg-accent/20 px-2 py-0.5 text-xs text-accent">最优</span>
                            )}
                          </td>
                          <td className="numeric px-3 py-2">{row.window}</td>
                          <td className="numeric px-3 py-2">{row.T}</td>
                          <td className="numeric px-3 py-2">{row.top_p}</td>
                          <td className="numeric px-3 py-2">{row.sample_count}</td>
                          <td className="numeric px-3 py-2">{row.mae.toFixed(4)}</td>
                          <td className="numeric px-3 py-2">{row.rmse.toFixed(4)}</td>
                          <td className="numeric px-3 py-2">{row.mape.toFixed(2)}%</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>

        <div className="lg:col-span-1">
          <TuneGuidePanel />
        </div>
      </div>
    </div>
  );
}

function SortHeader({
  label,
  active,
  dir,
  onSort,
}: {
  label: string;
  active: boolean;
  dir: SortDir;
  onSort: () => void;
}) {
  return (
    <th className="px-3 py-2">
      <button type="button" className="inline-flex items-center gap-1 hover:text-primary" onClick={onSort}>
        {label}
        {active && <span className="text-accent">{dir === "asc" ? "↑" : "↓"}</span>}
      </button>
    </th>
  );
}

function MetricSortHeader({
  keyName,
  active,
  dir,
  onSort,
}: {
  keyName: "mae" | "rmse" | "mape";
  active: boolean;
  dir: SortDir;
  onSort: () => void;
}) {
  const [open, setOpen] = useState(false);
  const entry = metricHelp[keyName];

  return (
    <th className="relative px-3 py-2">
      <span className="inline-flex items-center gap-1 normal-case">
        <button type="button" className="inline-flex items-center gap-1 hover:text-primary" onClick={onSort}>
          {entry.abbrev}
          {entry.recommended && <span className="text-[10px] text-accent">★</span>}
          {active && <span className="text-accent">{dir === "asc" ? "↑" : "↓"}</span>}
        </button>
        <button
          type="button"
          className="help-btn h-4 w-4 text-[10px]"
          aria-label={`${entry.fullName} 说明`}
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          ?
        </button>
      </span>
      {open && (
        <div className="absolute left-0 top-full z-10 mt-1 w-52 rounded-lg border border-border bg-surface p-2 text-left text-xs font-normal normal-case text-muted shadow-soft">
          <p className="font-medium text-primary">{entry.fullName}</p>
          <p className="mt-1">{entry.summary}</p>
          <p className="mt-1">{entry.tip}</p>
        </div>
      )}
    </th>
  );
}
