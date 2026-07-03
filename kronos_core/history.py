from __future__ import annotations

import glob
import json
import os
import re
from typing import Any, Optional

import pandas as pd

_META_VERSION = 1

_PREDICT_CSV_RE = re.compile(
    r"^(?P<instrument>.+)_pred(?P<pred_range>[0-9-]+)_w(?P<window>\d+)_h(?P<horizon>\d+)_run(?P<run>[0-9-]+)_predict\.csv$"
)


def meta_path_for_csv(csv_path: str) -> str:
    if csv_path.endswith("_predict.csv"):
        return csv_path[: -len("_predict.csv")] + "_meta.json"
    base, _ = os.path.splitext(csv_path)
    return f"{base}_meta.json"


def save_run_metadata(
    csv_path: str,
    *,
    mode: str,
    chart: dict[str, Any],
    metrics: Optional[dict[str, float]] = None,
    pred_start: Optional[str] = None,
    pred_end: Optional[str] = None,
) -> str:
    """Write sidecar JSON beside prediction CSV with full chart replay data."""
    meta_path = meta_path_for_csv(csv_path)
    payload = {
        "version": _META_VERSION,
        "mode": mode,
        "pred_start": pred_start,
        "pred_end": pred_end,
        "metrics": metrics,
        "chart": chart,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return os.path.abspath(meta_path)


def load_run_metadata(csv_path: str) -> Optional[dict[str, Any]]:
    meta_path = meta_path_for_csv(csv_path)
    if not os.path.isfile(meta_path):
        return None
    try:
        with open(meta_path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "chart" not in data:
            return None
        return data
    except (OSError, json.JSONDecodeError):
        return None


def _parse_predict_filename(filename: str) -> Optional[dict[str, Any]]:
    match = _PREDICT_CSV_RE.match(filename)
    if not match:
        return None
    info = match.groupdict()
    pred_range = info["pred_range"]
    if "-" in pred_range:
        pred_start, pred_end = pred_range.split("-", 1)
    else:
        pred_start = pred_end = pred_range
    return {
        "instrument": info["instrument"],
        "pred_start": pred_start,
        "pred_end": pred_end,
        "window": int(info["window"]),
        "horizon": int(info["horizon"]),
        "run_timestamp": info["run"],
    }


def _load_chart_from_csv(csv_path: str) -> Optional[dict[str, Any]]:
    try:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        if "timestamps" not in df.columns or "close" not in df.columns:
            return None
        return {
            "predicted": {
                "timestamps": df["timestamps"].astype(str).tolist(),
                "close": df["close"].astype(float).tolist(),
            }
        }
    except Exception:
        return None


def _legacy_chart_from_csv(csv_path: str) -> dict[str, Any]:
    partial = _load_chart_from_csv(csv_path) or {}
    predicted = partial.get("predicted") or {"timestamps": [], "close": []}
    return {
        "history": {"timestamps": [], "close": []},
        "predicted": predicted,
        "actual": None,
        "bridge": {"timestamp": "", "close": 0},
    }


def list_predictions(output_dir: str = "predictions") -> list[dict[str, Any]]:
    if not os.path.isdir(output_dir):
        return []

    entries: list[dict[str, Any]] = []
    for csv_path in glob.glob(os.path.join(output_dir, "*_predict.csv")):
        filename = os.path.basename(csv_path)
        meta = _parse_predict_filename(filename)
        if not meta:
            continue

        png_path = csv_path.replace("_predict.csv", "_predict.png")
        png_exists = os.path.isfile(png_path)
        sidecar = load_run_metadata(csv_path)

        if sidecar:
            chart = sidecar.get("chart")
            metrics = sidecar.get("metrics")
            mode = sidecar.get("mode", "backtest")
            chart_complete = True
        else:
            chart = _legacy_chart_from_csv(csv_path)
            metrics = None
            mode = "unknown"
            chart_complete = False

        entry: dict[str, Any] = {
            "id": filename,
            "instrument": meta["instrument"],
            "pred_start": meta["pred_start"],
            "pred_end": meta["pred_end"],
            "window": meta["window"],
            "horizon": meta["horizon"],
            "run_timestamp": meta["run_timestamp"],
            "csv_path": os.path.abspath(csv_path),
            "png_path": os.path.abspath(png_path) if png_exists else None,
            "metrics": metrics,
            "mode": mode,
            "chart": chart,
            "chart_complete": chart_complete,
        }
        entries.append(entry)

    entries.sort(key=lambda e: e["run_timestamp"], reverse=True)
    return entries
