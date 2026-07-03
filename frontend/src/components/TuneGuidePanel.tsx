import { useState } from "react";
import { tunePlaybook } from "../content/paramHelp";

export default function TuneGuidePanel() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <div className="card space-y-2">
      <div>
        <h3 className="text-sm font-semibold">调试指南</h3>
        <p className="text-xs text-muted">调参顺序、指标解读与常见问题，无需翻 README。</p>
      </div>
      {tunePlaybook.map((section, idx) => {
        const open = openIndex === idx;
        return (
          <div key={section.title} className="rounded-lg border border-border">
            <button
              type="button"
              className="flex w-full items-center justify-between px-3 py-2 text-left text-sm font-medium hover:bg-elevated"
              onClick={() => setOpenIndex(open ? null : idx)}
            >
              <span>{section.title}</span>
              <span className="text-muted">{open ? "−" : "+"}</span>
            </button>
            {open && (
              <ol className="list-decimal space-y-1 border-t border-border px-3 py-2 pl-6 text-xs text-muted">
                {section.steps.map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ol>
            )}
          </div>
        );
      })}
    </div>
  );
}
