from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd


def _ts_values(series) -> list[str]:
    return [pd.Timestamp(v).isoformat() for v in series]


def build_chart_series(x_df, x_timestamp, pred_df, gt_df=None) -> dict:
    last_ts = x_timestamp.values[-1]
    last_close = float(x_df["close"].values[-1])

    history = {
        "timestamps": _ts_values(x_timestamp.values),
        "close": [float(v) for v in x_df["close"].values],
    }

    pred_plot_ts = np.concatenate([[last_ts], pred_df["timestamps"].values])
    pred_plot_close = np.concatenate([[last_close], pred_df["close"].values])
    predicted = {
        "timestamps": _ts_values(pred_plot_ts),
        "close": [float(v) for v in pred_plot_close],
    }

    actual = None
    if gt_df is not None:
        gt_plot_ts = np.concatenate([[last_ts], gt_df["timestamps"].values])
        gt_plot_close = np.concatenate([[last_close], gt_df["close"].values])
        actual = {
            "timestamps": _ts_values(gt_plot_ts),
            "close": [float(v) for v in gt_plot_close],
        }

    return {
        "history": history,
        "predicted": predicted,
        "actual": actual,
        "bridge": {"timestamp": pd.Timestamp(last_ts).isoformat(), "close": last_close},
    }


def plot_prediction(x_df, x_timestamp, pred_df, gt_df, instrument, save_path):
    """Save chart to PNG using non-interactive Agg backend (safe in worker threads)."""
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    fig = Figure(figsize=(11, 5))
    FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)

    ax.plot(x_timestamp.values, x_df["close"].values, label="历史真实收盘价", color="#2c3e50", linewidth=1.5)

    last_ts = x_timestamp.values[-1]
    last_close = x_df["close"].values[-1]

    pred_plot_ts = np.concatenate([[last_ts], pred_df["timestamps"].values])
    pred_plot_close = np.concatenate([[last_close], pred_df["close"].values])
    ax.plot(
        pred_plot_ts,
        pred_plot_close,
        label="预测收盘价",
        color="#e74c3c",
        linewidth=1.8,
        linestyle="--",
        marker="o",
        markersize=3,
    )

    if gt_df is not None:
        gt_plot_ts = np.concatenate([[last_ts], gt_df["timestamps"].values])
        gt_plot_close = np.concatenate([[last_close], gt_df["close"].values])
        ax.plot(
            gt_plot_ts,
            gt_plot_close,
            label="真实收盘价（对比）",
            color="#27ae60",
            linewidth=1.8,
            marker="o",
            markersize=3,
        )

    ax.set_title(f"{instrument} Kronos 预测 vs 真实 K线（收盘价）")
    ax.set_xlabel("日期")
    ax.set_ylabel("价格")
    ax.legend(loc="best")
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)


def configure_matplotlib_fonts() -> None:
    try:
        matplotlib.rcParams["font.sans-serif"] = [
            "PingFang SC",
            "Microsoft YaHei",
            "SimHei",
            "Arial Unicode MS",
        ]
        matplotlib.rcParams["axes.unicode_minus"] = False
    except Exception:
        pass
