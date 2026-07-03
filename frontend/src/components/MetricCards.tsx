import { useState } from "react";
import type { Metrics } from "../types";
import { metricHelpList } from "../content/paramHelp";
import { IconInfo } from "./icons";

const accentColors = ["border-accent/60", "border-accent-secondary/60", "border-success/60"];

export default function MetricCards({
  metrics,
  showBacktestNote = false,
}: {
  metrics?: Metrics | null;
  showBacktestNote?: boolean;
}) {
  if (!metrics) return null;

  return (
    <div className="space-y-3">
      <div>
        <h3 className="text-sm font-semibold">回测误差指标</h3>
        <p className="text-xs text-muted">MAPE 越小越好，横向对比股票或参数时优先看 MAPE。</p>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {metricHelpList.map((entry, idx) => (
          <MetricCard key={entry.key} entry={entry} value={metrics[entry.key]} accent={accentColors[idx % accentColors.length]} />
        ))}
      </div>
      {showBacktestNote && (
        <p className="rounded-lg bg-elevated/60 px-3 py-2 text-xs text-muted">
          本结果为历史回测，扣留最后 horizon 天与真实值对比。
        </p>
      )}
    </div>
  );
}

function MetricCard({
  entry,
  value,
  accent,
}: {
  entry: (typeof metricHelpList)[number];
  value: number;
  accent: string;
}) {
  const [open, setOpen] = useState(false);
  const formatted = entry.key === "mape" ? `${value.toFixed(2)}%` : value.toFixed(4);

  return (
    <div className={`card metric-accent ${accent}`}>
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5">
          <p className="text-xs font-medium uppercase tracking-wide text-muted">{entry.abbrev}</p>
          {entry.recommended && (
            <span className="rounded bg-accent/15 px-1.5 py-0.5 text-[10px] font-medium text-accent">推荐</span>
          )}
        </div>
        <button
          type="button"
          className="help-btn"
          aria-label={`${entry.fullName} 详细说明`}
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          <IconInfo className="h-3.5 w-3.5" />
        </button>
      </div>
      <p className="numeric mt-2 text-3xl font-semibold tracking-tight">{formatted}</p>
      <p className="mt-1 text-xs leading-relaxed text-muted">{entry.summary}</p>
      {open && (
        <div className="mt-3 space-y-1 rounded-lg border border-border bg-elevated/80 px-3 py-2 text-xs text-muted">
          <p className="font-medium text-primary">{entry.fullName}</p>
          <p>{entry.interpretation}</p>
          <p>{entry.tip}</p>
        </div>
      )}
    </div>
  );
}
