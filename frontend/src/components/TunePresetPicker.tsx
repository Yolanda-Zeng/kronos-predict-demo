import { tunePresets, type TunePreset } from "../content/paramHelp";

interface Props {
  selected: TunePreset["id"];
  onSelect: (preset: TunePreset) => void;
}

export default function TunePresetPicker({ selected, onSelect }: Props) {
  return (
    <div className="space-y-2">
      <p className="text-xs font-medium text-muted">预设方案</p>
      <div className="flex flex-wrap gap-2">
        {tunePresets.map((preset) => (
          <button
            key={preset.id}
            type="button"
            className={`rounded-lg border px-3 py-1.5 text-xs transition ${
              selected === preset.id
                ? "border-accent bg-accent/10 text-primary"
                : "border-border text-muted hover:border-accent/30 hover:text-primary"
            }`}
            onClick={() => onSelect(preset)}
          >
            {preset.name}
          </button>
        ))}
      </div>
      <p className="text-xs text-muted">
        {tunePresets.find((p) => p.id === selected)?.description} · 每只股票建议单独调参
      </p>
    </div>
  );
}
