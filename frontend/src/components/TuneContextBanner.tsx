import type { PredictFormValues } from "../types";

const dataSourceLabels: Record<PredictFormValues["data_source"], string> = {
  akshare: "A股 akshare",
  hkshare: "港股 hkshare",
  usstock: "美股 usstock",
  qlib: "qlib 本地",
};

export default function TuneContextBanner({ form }: { form: PredictFormValues }) {
  return (
    <div className="card-highlight flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm">
        <span className="rounded-md bg-accent/15 px-2 py-0.5 font-medium text-accent">{form.instrument}</span>
        <span className="text-muted">{dataSourceLabels[form.data_source]}</span>
        <span className="text-muted">·</span>
        <span className="numeric text-muted">
          {form.start} ~ {form.end}
        </span>
      </div>
      <p className="text-xs text-muted">调参使用预测 Tab 中的股票与日期，请先在预测 Tab 确认后再跑。</p>
    </div>
  );
}
