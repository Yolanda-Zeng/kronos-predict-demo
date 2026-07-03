import { useState } from "react";
import type { PredictFormValues } from "../types";
import { dataSourceHints } from "../types";
import ParamHelpField from "./ParamHelpField";
import SectionHeader from "./SectionHeader";
import { predictParamHelp } from "../content/paramHelp";

interface Props {
  form: PredictFormValues;
  setForm: (value: PredictFormValues) => void;
  onSubmit: () => void;
  submitting: boolean;
}

export default function ParamForm({ form, setForm, onSubmit, submitting }: Props) {
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const update = <K extends keyof PredictFormValues>(key: K, value: PredictFormValues[K]) => {
    setForm({ ...form, [key]: value });
  };

  return (
    <div className="card space-y-5">
      <SectionHeader title="参数配置" subtitle="填写股票与日期区间，提交后后台异步推理。" />

      <div className="grid gap-3">
        <div>
          <label className="label" htmlFor="instrument">
            股票代码
          </label>
          <input
            id="instrument"
            className="input font-mono"
            value={form.instrument}
            onChange={(e) => update("instrument", e.target.value)}
          />
        </div>

        <div>
          <label className="label" htmlFor="data-source">
            数据源
          </label>
          <select
            id="data-source"
            className="input"
            value={form.data_source}
            onChange={(e) => update("data_source", e.target.value as PredictFormValues["data_source"])}
          >
            <option value="akshare">akshare (A股)</option>
            <option value="hkshare">hkshare (港股)</option>
            <option value="usstock">usstock (美股)</option>
            <option value="qlib">qlib (本地)</option>
          </select>
          <p className="mt-2 rounded-lg border border-border bg-elevated/60 px-3 py-2 text-xs leading-relaxed text-muted">
            {dataSourceHints[form.data_source]}
          </p>
        </div>

        {form.data_source === "qlib" && (
          <div>
            <label className="label" htmlFor="provider-uri">
              qlib 数据路径
            </label>
            <input
              id="provider-uri"
              className="input"
              value={form.provider_uri ?? ""}
              onChange={(e) => update("provider_uri", e.target.value)}
            />
          </div>
        )}

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <label className="label" htmlFor="start-date">
              起始日期
            </label>
            <input
              id="start-date"
              className="input"
              type="date"
              value={form.start}
              onChange={(e) => update("start", e.target.value)}
            />
          </div>
          <div>
            <label className="label" htmlFor="end-date">
              {form.future ? "预测至日期" : "结束日期"}
            </label>
            <input
              id="end-date"
              className="input"
              type="date"
              value={form.end}
              onChange={(e) => update("end", e.target.value)}
            />
          </div>
        </div>

        <div className="rounded-lg border border-border bg-elevated/40 p-3">
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted">预测模式</p>
          <div className="segmented" role="radiogroup" aria-label="预测模式">
            <button
              type="button"
              role="radio"
              aria-checked={!form.future}
              className={!form.future ? "segment-active" : "segment-inactive"}
              onClick={() => update("future", false)}
            >
              <span className="block font-medium text-primary">历史回测</span>
              <span className="mt-0.5 block text-[11px] leading-snug opacity-80">扣留最后 horizon 天对比</span>
            </button>
            <button
              type="button"
              role="radio"
              aria-checked={form.future}
              className={form.future ? "segment-active" : "segment-inactive"}
              onClick={() => update("future", true)}
            >
              <span className="block font-medium text-primary">预测未来</span>
              <span className="mt-0.5 block text-[11px] leading-snug opacity-80">--future 延伸至目标日</span>
            </button>
          </div>
          <p className="mt-2 text-xs leading-relaxed text-muted">
            {form.future
              ? `历史 K 线最多到最新交易日。若「预测至日期」晚于最新 K 线，预测红线延伸至该日；否则按 horizon=${form.horizon} 个交易日预测。`
              : `图表最远日期为结束日期；horizon=${form.horizon} 表示末尾 ${form.horizon} 天用于与真实值对比。`}
          </p>
        </div>
      </div>

      <div className="space-y-3 border-t border-border pt-4">
        <p className="text-xs font-medium uppercase tracking-wide text-muted">模型路径</p>
        <div>
          <label className="label" htmlFor="model-path">
            model_path
          </label>
          <input
            id="model-path"
            className="input font-mono text-xs"
            value={form.model_path}
            onChange={(e) => update("model_path", e.target.value)}
          />
        </div>
        <div>
          <label className="label" htmlFor="tokenizer-path">
            tokenizer_path
          </label>
          <input
            id="tokenizer-path"
            className="input font-mono text-xs"
            value={form.tokenizer_path}
            onChange={(e) => update("tokenizer_path", e.target.value)}
          />
        </div>
      </div>

      <button type="button" className="btn-ghost w-full" onClick={() => setAdvancedOpen((v) => !v)}>
        {advancedOpen ? "收起高级参数" : "展开高级参数"}
      </button>

      {advancedOpen && (
        <div className="grid grid-cols-2 gap-3 rounded-lg border border-border bg-elevated/30 p-3">
          <ParamHelpField
            help={predictParamHelp.window}
            value={String(form.window)}
            onChange={(v) => update("window", Number(v))}
            type="number"
          />
          <ParamHelpField
            help={{
              ...predictParamHelp.horizon,
              summary: form.future
                ? "未来模式：若「预测至日期」晚于最新 K 线则延伸至该日；否则按 horizon 个交易日"
                : predictParamHelp.horizon.summary,
              debugTip: form.future
                ? "预测至日期优先；结束日≤最新 K 线时才使用 horizon"
                : predictParamHelp.horizon.debugTip,
            }}
            value={String(form.horizon)}
            onChange={(v) => update("horizon", Number(v))}
            type="number"
          />
          <ParamHelpField
            help={predictParamHelp.seed}
            value={String(form.seed)}
            onChange={(v) => update("seed", Number(v))}
            type="number"
          />
          <ParamHelpField
            help={predictParamHelp.temperature}
            value={String(form.temperature)}
            onChange={(v) => update("temperature", Number(v))}
            type="number"
            step={0.1}
          />
          <ParamHelpField
            help={predictParamHelp.top_p}
            value={String(form.top_p)}
            onChange={(v) => update("top_p", Number(v))}
            type="number"
            step={0.05}
          />
          <ParamHelpField
            help={predictParamHelp.sample_count}
            value={String(form.sample_count)}
            onChange={(v) => update("sample_count", Number(v))}
            type="number"
          />
          <div className="col-span-2">
            <DeviceField value={form.device} onChange={(v) => update("device", v)} />
          </div>
          {form.data_source === "akshare" && (
            <div className="col-span-2">
              <label className="label" htmlFor="adjust">
                复权方式
              </label>
              <select
                id="adjust"
                className="input"
                value={form.adjust}
                onChange={(e) => update("adjust", e.target.value as PredictFormValues["adjust"])}
              >
                <option value="qfq">前复权 qfq</option>
                <option value="hfq">后复权 hfq</option>
                <option value="">不复权</option>
              </select>
            </div>
          )}
        </div>
      )}

      <button type="button" className="btn-primary w-full" disabled={submitting} onClick={onSubmit}>
        {submitting ? "预测进行中..." : "开始预测"}
      </button>
    </div>
  );
}

function DeviceField({ value, onChange }: { value: string; onChange: (value: string) => void }) {
  const [open, setOpen] = useState(false);
  const help = predictParamHelp.device;

  return (
    <div>
      <div className="mb-1 flex items-center gap-1.5">
        <label className="label mb-0">{help.label}</label>
        <button
          type="button"
          className="help-btn h-4 w-4 text-[10px]"
          aria-label={`${help.label} 说明`}
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          ?
        </button>
      </div>
      <select className="input" value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="cpu">cpu</option>
        <option value="cuda">cuda</option>
        <option value="mps">mps</option>
      </select>
      {open && (
        <div className="mt-2 space-y-1 rounded-lg border border-border bg-elevated/80 px-3 py-2 text-xs text-muted">
          <p>{help.summary}</p>
          {help.range && <p>建议范围：{help.range}</p>}
          {help.debugTip && <p className="text-primary/80">调试：{help.debugTip}</p>}
        </div>
      )}
    </div>
  );
}
