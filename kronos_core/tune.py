from __future__ import annotations

import itertools
import os
from dataclasses import dataclass
from typing import Any, Callable, Optional

import numpy as np
import pandas as pd

from kronos_core.data import load_kline_data
from kronos_core.metrics import compute_metrics, set_seed
from kronos_core.params import TuneParams
from kronos_core.paths import build_output_path
from kronos_core.predictor import get_shared_predictor, load_kronos_predictor


@dataclass
class TuneResult:
    csv_path: str
    results: list[dict[str, Any]]
    best: dict[str, Any]


ProgressCallback = Callable[[str, Optional[float]], None]


def _noop_progress(message: str, progress: Optional[float] = None) -> None:
    if message:
        print(f"[INFO] {message}")


def execute_tune(
    params: TuneParams,
    *,
    use_shared_predictor: bool = False,
    on_progress: ProgressCallback | None = None,
) -> TuneResult:
    progress = on_progress or _noop_progress
    set_seed(params.seed)

    if params.tune_out is None:
        params.tune_out = build_output_path(params.output_dir, params.instrument, "tune", "csv")

    progress("正在获取行情数据", 0.05)
    df = load_kline_data(params)
    print(f"[INFO] 共取到 {len(df)} 条历史K线，用于滚动回测调参。")

    windows = [int(x) for x in params.grid_window.split(",")]
    temps = [float(x) for x in params.grid_temp.split(",")]
    top_ps = [float(x) for x in params.grid_top_p.split(",")]
    sample_counts = [int(x) for x in params.grid_sample_count.split(",")]

    progress("正在加载模型", 0.1)
    if use_shared_predictor:
        predictor = get_shared_predictor(
            params.model_path, params.tokenizer_path, params.max_context, params.device
        )
    else:
        predictor = load_kronos_predictor(
            params.model_path, params.tokenizer_path, params.max_context, params.device
        )

    results = []
    combos = list(itertools.product(windows, temps, top_ps, sample_counts))
    print(f"[INFO] 共 {len(combos)} 组参数组合，每组最多评估 {params.tune_max_windows} 个滚动窗口。")

    for combo_idx, (window, T, top_p, sample_count) in enumerate(combos, start=1):
        progress(
            f"调参进度 {combo_idx}/{len(combos)}: window={window}, T={T}, top_p={top_p}, sample_count={sample_count}",
            combo_idx / len(combos),
        )

        max_lookback_end = len(df) - params.horizon
        min_lookback_end = window
        if max_lookback_end <= min_lookback_end:
            print(f"[WARN] 数据量不足以支撑 window={window}，跳过该组合。")
            continue

        eval_points = list(range(min_lookback_end, max_lookback_end, params.tune_stride))
        if len(eval_points) > params.tune_max_windows:
            idx = np.linspace(0, len(eval_points) - 1, params.tune_max_windows).astype(int)
            eval_points = [eval_points[i] for i in idx]

        errors = []
        for lookback_end in eval_points:
            lookback_start = lookback_end - window
            x_df = df.loc[
                lookback_start : lookback_end - 1, ["open", "high", "low", "close", "volume", "amount"]
            ].reset_index(drop=True)
            x_timestamp = df.loc[lookback_start : lookback_end - 1, "timestamps"].reset_index(drop=True)
            y_timestamp = df.loc[lookback_end : lookback_end + params.horizon - 1, "timestamps"].reset_index(
                drop=True
            )
            gt_close = df.loc[lookback_end : lookback_end + params.horizon - 1, "close"].values

            try:
                pred_df = predictor.predict(
                    df=x_df,
                    x_timestamp=x_timestamp,
                    y_timestamp=y_timestamp,
                    pred_len=params.horizon,
                    T=T,
                    top_p=top_p,
                    sample_count=sample_count,
                    verbose=False,
                )
            except Exception as e:
                print(f"[WARN] 第 {lookback_end} 个窗口预测失败，跳过：{e}")
                continue

            if len(pred_df) != len(gt_close):
                continue
            errors.append(compute_metrics(gt_close, pred_df["close"].values))

        if not errors:
            continue

        mae = np.mean([e["mae"] for e in errors])
        rmse = np.mean([e["rmse"] for e in errors])
        mape = np.mean([e["mape"] for e in errors])

        print(
            f"[{combo_idx}/{len(combos)}] window={window}, T={T}, top_p={top_p}, "
            f"sample_count={sample_count} -> MAE={mae:.4f}, RMSE={rmse:.4f}, MAPE={mape:.2f}%  "
            f"(评估了 {len(errors)} 个窗口)"
        )

        results.append(
            {
                "window": int(window),
                "T": float(T),
                "top_p": float(top_p),
                "sample_count": int(sample_count),
                "mae": float(mae),
                "rmse": float(rmse),
                "mape": float(mape),
                "n_eval_windows": len(errors),
            }
        )

    if not results:
        raise RuntimeError("没有任何参数组合成功完成回测，请检查数据量是否足够，或调小 grid 范围。")

    result_df = pd.DataFrame(results).sort_values("rmse").reset_index(drop=True)
    out_path = os.path.abspath(params.tune_out)
    result_df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[INFO] 调参结果已保存到: {out_path}")

    best = result_df.iloc[0].to_dict()
    best["window"] = int(best["window"])
    best["sample_count"] = int(best["sample_count"])
    print("=" * 60)
    print("[BEST] 最优参数组合（按 RMSE 排序）：")
    print(
        f"  window={best['window']}, T={best['T']}, top_p={best['top_p']}, "
        f"sample_count={best['sample_count']}"
    )
    print(f"  MAE={best['mae']:.4f}, RMSE={best['rmse']:.4f}, MAPE={best['mape']:.2f}%")
    print("=" * 60)

    progress("完成", 1.0)
    return TuneResult(
        csv_path=out_path,
        results=result_df.to_dict(orient="records"),
        best=best,
    )


def run_tune_cli(params: TuneParams) -> TuneResult:
    return execute_tune(params, use_shared_predictor=False)
