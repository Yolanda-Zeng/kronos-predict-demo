import type { PredictResult } from "../types";
import { downloadUrl } from "../api/client";
import SectionHeader from "./SectionHeader";

export default function ResultPanel({ result }: { result: PredictResult }) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <SectionHeader title="预测明细" subtitle="逐日收盘价数据，可导出 CSV / PNG" />
        <div className="flex flex-wrap gap-2">
          <a className="btn-primary" href={downloadUrl(result.csv_path)}>
            下载 CSV
          </a>
          {result.chart_path && (
            <a className="btn-ghost" href={downloadUrl(result.chart_path)}>
              下载 PNG
            </a>
          )}
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-border text-xs uppercase tracking-wide text-muted">
            <tr>
              {Object.keys(result.predictions[0] ?? { timestamps: "", close: "" }).map((key) => (
                <th key={key} className="px-3 py-2.5 font-medium">
                  {key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.predictions.map((row, idx) => (
              <tr key={idx} className="border-t border-border transition hover:bg-elevated/40">
                {Object.values(row).map((value, colIdx) => (
                  <td key={colIdx} className="numeric px-3 py-2">
                    {String(value)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
