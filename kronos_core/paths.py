import os
from datetime import datetime
from typing import Optional

from kronos_core.params import PredictParams


def build_output_path(
    output_dir,
    instrument,
    tag,
    ext,
    window=None,
    horizon=None,
    pred_start=None,
    pred_end=None,
):
    os.makedirs(output_dir, exist_ok=True)
    run_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    parts = [instrument]
    if pred_start and pred_end:
        if pred_start == pred_end:
            parts.append(f"pred{pred_start}")
        else:
            parts.append(f"pred{pred_start}-{pred_end}")
    if window is not None:
        parts.append(f"w{window}")
    if horizon is not None:
        parts.append(f"h{horizon}")
    parts.append(f"run{run_timestamp}")
    parts.append(tag)
    filename = "_".join(parts) + f".{ext}"
    return os.path.join(output_dir, filename)


def resolve_out_paths(params: PredictParams, pred_start=None, pred_end=None) -> PredictParams:
    if params.out is None:
        params.out = build_output_path(
            params.output_dir,
            params.instrument,
            "predict",
            "csv",
            window=params.window,
            horizon=params.horizon,
            pred_start=pred_start,
            pred_end=pred_end,
        )
    if params.chart_out is None:
        params.chart_out = build_output_path(
            params.output_dir,
            params.instrument,
            "predict",
            "png",
            window=params.window,
            horizon=params.horizon,
            pred_start=pred_start,
            pred_end=pred_end,
        )
    return params
