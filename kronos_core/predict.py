from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable, Optional

import pandas as pd

from kronos_core.chart import build_chart_series, plot_prediction
from kronos_core.data import load_kline_data, resolve_future_prediction_timestamps
from kronos_core.history import save_run_metadata
from kronos_core.metrics import compute_metrics, set_seed
from kronos_core.params import PredictParams
from kronos_core.paths import resolve_out_paths
from kronos_core.predictor import get_shared_predictor, load_kronos_predictor


@dataclass
class PredictResult:
    instrument: str
    mode: str
    csv_path: str
    chart_path: str
    metrics: Optional[dict[str, float]]
    predictions: list[dict[str, Any]]
    chart: dict[str, Any]
    pred_start: str
    pred_end: str


ProgressCallback = Callable[[str, Optional[float]], None]


def _noop_progress(message: str, progress: Optional[float] = None) -> None:
    if message:
        print(f"[INFO] {message}")


def execute_predict(
    params: PredictParams,
    *,
    use_shared_predictor: bool = False,
    on_progress: ProgressCallback | None = None,
) -> PredictResult:
    progress = on_progress or _noop_progress
    set_seed(params.seed)

    progress("正在获取行情数据", 0.1)
    df = load_kline_data(params)
    print(
        f"[INFO] 共取到 {len(df)} 条历史K线（{df['timestamps'].iloc[0].date()} ~ {df['timestamps'].iloc[-1].date()}）"
    )

    not_enough_data = len(df) < params.window + params.horizon

    if params.future or not_enough_data:
        mode = "future"
        last_ts = df["timestamps"].iloc[-1]
        y_timestamp, ts_source = resolve_future_prediction_timestamps(
            last_ts, params.end, params.horizon
        )
        pred_len = len(y_timestamp)
        if not_enough_data and not params.future:
            print(
                f"[WARN] 历史数据量({len(df)})小于 window+horizon({params.window + params.horizon})，"
                f"自动切换为预测真正未来模式（不含真实值对比）。"
            )
        elif ts_source == "until_end":
            print(
                f"[INFO] --future 模式：最后 K 线 {pd.Timestamp(last_ts).date()}，"
                f"预测延伸至 {params.end}（共 {pred_len} 个交易日），不做历史回测对比。"
            )
        else:
            print(
                f"[INFO] --future 模式：最后 K 线 {pd.Timestamp(last_ts).date()}，"
                f"结束日不晚于最后 K 线，按 horizon={params.horizon} 预测 {pred_len} 个交易日。"
            )
        x_df = df[["open", "high", "low", "close", "volume", "amount"]]
        x_timestamp = df["timestamps"]
        gt_df = None
    else:
        mode = "backtest"
        print(
            f"[INFO] 历史回测模式：扣留最后 {params.horizon} 天真实数据用于对比评分。"
            f"如果想预测真正的未来，请加上 --future 参数。"
        )
        lookback_end = len(df) - params.horizon
        lookback_start = max(0, lookback_end - params.window)

        x_df = df.loc[lookback_start : lookback_end - 1, ["open", "high", "low", "close", "volume", "amount"]]
        x_timestamp = df.loc[lookback_start : lookback_end - 1, "timestamps"]
        y_timestamp = df.loc[lookback_end : lookback_end + params.horizon - 1, "timestamps"]
        gt_df = df.loc[lookback_end : lookback_end + params.horizon - 1].reset_index(drop=True)
        pred_len = params.horizon

    pred_start = pd.Timestamp(y_timestamp.iloc[0]).strftime("%Y%m%d")
    pred_end = pd.Timestamp(y_timestamp.iloc[-1]).strftime("%Y%m%d")
    params = resolve_out_paths(params, pred_start=pred_start, pred_end=pred_end)

    progress("正在加载模型", 0.25)
    if use_shared_predictor:
        predictor = get_shared_predictor(
            params.model_path, params.tokenizer_path, params.max_context, params.device
        )
    else:
        predictor = load_kronos_predictor(
            params.model_path, params.tokenizer_path, params.max_context, params.device
        )

    progress("正在推理预测", 0.5)
    print(
        f"[INFO] 开始预测：window={len(x_df)}, pred_len={pred_len}, "
        f"T={params.temperature}, top_p={params.top_p}, sample_count={params.sample_count}"
    )
    print(
        f"[INFO] 预测区间：{pd.Timestamp(y_timestamp.iloc[0]).date()} ~ "
        f"{pd.Timestamp(y_timestamp.iloc[-1]).date()}"
    )

    pred_df = predictor.predict(
        df=x_df.reset_index(drop=True),
        x_timestamp=x_timestamp.reset_index(drop=True),
        y_timestamp=y_timestamp.reset_index(drop=True),
        pred_len=pred_len,
        T=params.temperature,
        top_p=params.top_p,
        sample_count=params.sample_count,
        verbose=True,
    )
    pred_df = pred_df.reset_index(drop=True)
    pred_df.insert(0, "timestamps", y_timestamp.reset_index(drop=True).values)

    progress("正在保存结果", 0.85)
    out_path = os.path.abspath(params.out)
    pred_df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[INFO] 预测结果已保存到: {out_path}")

    chart_path = os.path.abspath(params.chart_out)
    plot_prediction(
        x_df=x_df,
        x_timestamp=x_timestamp,
        pred_df=pred_df,
        gt_df=gt_df,
        instrument=params.instrument,
        save_path=chart_path,
    )
    print(f"[INFO] 预测K线图已保存到: {chart_path}")

    metrics = None
    if gt_df is not None:
        metrics = compute_metrics(gt_df["close"].values, pred_df["close"].values)
        print(
            f"[INFO] 预测区间误差（与真实值对比）：MAE={metrics['mae']:.4f}, "
            f"RMSE={metrics['rmse']:.4f}, MAPE={metrics['mape']:.2f}%"
        )

    chart = build_chart_series(x_df, x_timestamp, pred_df, gt_df)
    predictions = pred_df.assign(timestamps=pred_df["timestamps"].astype(str)).to_dict(orient="records")

    if mode == "future":
        hist_last = pd.Timestamp(chart["bridge"]["timestamp"])
        pred_times = [pd.Timestamp(t) for t in chart["predicted"]["timestamps"]]
        if not any(t > hist_last for t in pred_times):
            print(
                "[WARN] future 模式：predicted 时间戳未延伸到最后已知 K 线之后，"
                "请检查 make_future_timestamps 与 chart 序列。"
            )

    save_run_metadata(
        out_path,
        mode=mode,
        chart=chart,
        metrics=metrics,
        pred_start=pred_start,
        pred_end=pred_end,
    )

    progress("完成", 1.0)
    return PredictResult(
        instrument=params.instrument,
        mode=mode,
        csv_path=out_path,
        chart_path=chart_path,
        metrics=metrics,
        predictions=predictions,
        chart=chart,
        pred_start=pred_start,
        pred_end=pred_end,
    )


def run_single_predict_cli(params: PredictParams) -> PredictResult:
    return execute_predict(params, use_shared_predictor=False)
