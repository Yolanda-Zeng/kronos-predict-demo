import { useState } from "react";
import type { ParamHelpEntry } from "../content/paramHelp";

interface Props {
  help: ParamHelpEntry;
  value: string;
  onChange: (value: string) => void;
  type?: "text" | "number";
  step?: number;
}

export default function ParamHelpField({ help, value, onChange, type = "text", step }: Props) {
  const [open, setOpen] = useState(false);

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
      <input
        className="input numeric"
        type={type}
        step={step}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      {open && (
        <div className="mt-2 space-y-1 rounded-lg border border-border bg-elevated/80 px-3 py-2 text-xs text-muted">
          <p>{help.summary}</p>
          {help.range && <p>建议范围：{help.range}</p>}
          {help.impact && <p>影响：{help.impact}</p>}
          {help.debugTip && <p className="text-primary/80">调试：{help.debugTip}</p>}
        </div>
      )}
    </div>
  );
}
