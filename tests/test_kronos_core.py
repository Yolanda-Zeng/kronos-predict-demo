"""Smoke tests for kronos_core package structure."""

import importlib
import json
import tempfile
from pathlib import Path

import pandas as pd


def test_core_modules_importable():
    modules = [
        "kronos_core.params",
        "kronos_core.metrics",
        "kronos_core.data",
        "kronos_core.chart",
        "kronos_core.predict",
        "kronos_core.tune",
        "kronos_core.history",
        "kronos_core.predictor",
    ]
    for name in modules:
        importlib.import_module(name)


def test_predict_params_from_namespace():
    class Args:
        data_source = "qlib"
        provider_uri = "./qlib_data"
        instrument = "SH600519"
        start = "2018-01-01"
        end = "2020-09-25"
        future = False
        adjust = "qfq"
        model_path = "./model"
        tokenizer_path = "./tokenizer"
        window = 64
        horizon = 5
        seed = 40
        temperature = 1.0
        top_p = 0.9
        sample_count = 1
        output_dir = "predictions"
        out = None
        chart_out = None
        max_context = 512
        device = "cpu"

    params = __import__("kronos_core.params", fromlist=["PredictParams"]).PredictParams.from_namespace(Args())
    assert params.instrument == "SH600519"
    assert params.window == 64


def test_make_future_timestamps_after_last_ts():
    from kronos_core.data import make_future_timestamps

    last = pd.Timestamp("2024-06-28")
    future = make_future_timestamps(last, 5)
    assert len(future) == 5
    assert all(pd.Timestamp(t) > last for t in future)


def test_build_chart_series_future_extends_beyond_history():
    from kronos_core.chart import build_chart_series

    n = 10
    x_timestamp = pd.bdate_range("2024-01-01", periods=n, freq="B")
    x_df = pd.DataFrame({"close": range(n)})
    last_ts = x_timestamp[-1]
    pred_ts = pd.bdate_range(last_ts + pd.Timedelta(days=1), periods=3, freq="B")
    pred_df = pd.DataFrame({"timestamps": pred_ts, "close": [100.0, 101.0, 102.0]})

    chart = build_chart_series(x_df, x_timestamp, pred_df, gt_df=None)
    hist_max = max(pd.Timestamp(t) for t in chart["history"]["timestamps"])
    pred_max = max(pd.Timestamp(t) for t in chart["predicted"]["timestamps"])
    assert pred_max > hist_max


def test_save_and_load_run_metadata_roundtrip():
    from kronos_core.history import load_run_metadata, save_run_metadata

    chart = {
        "history": {"timestamps": ["2024-01-01"], "close": [1.0]},
        "predicted": {"timestamps": ["2024-01-02"], "close": [2.0]},
        "actual": None,
        "bridge": {"timestamp": "2024-01-01", "close": 1.0},
    }
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = str(Path(tmp) / "600519_pred20240101-20240105_w64_h5_run2024-01-01_predict.csv")
        Path(csv_path).write_text("timestamps,close\n2024-01-02,2.0\n", encoding="utf-8")
        save_run_metadata(
            csv_path,
            mode="future",
            chart=chart,
            metrics=None,
            pred_start="20240101",
            pred_end="20240105",
        )
        loaded = load_run_metadata(csv_path)
        assert loaded is not None
        assert loaded["version"] == 1
        assert loaded["mode"] == "future"
        assert loaded["chart"]["predicted"]["close"] == [2.0]


def test_list_predictions_legacy_chart_complete_false():
    from kronos_core.history import list_predictions

    with tempfile.TemporaryDirectory() as tmp:
        csv_name = "600519_pred20240101-20240105_w64_h5_run2024-01-01_predict.csv"
        csv_path = Path(tmp) / csv_name
        csv_path.write_text("timestamps,close\n2024-01-02,2.0\n", encoding="utf-8")
        items = list_predictions(str(tmp))
        assert len(items) == 1
        assert items[0]["chart_complete"] is False
        assert items[0]["metrics"] is None


def test_make_future_timestamps_until_through_end_date():
    from kronos_core.data import make_future_timestamps_until

    last = pd.Timestamp("2026-07-03")
    end = "2026-07-10"
    future = make_future_timestamps_until(last, end)
    assert len(future) > 0
    assert pd.Timestamp(future.iloc[-1]).normalize() == pd.Timestamp("2026-07-10").normalize()
    assert all(pd.Timestamp(t) > last for t in future)


def test_resolve_future_prediction_timestamps_fallback_horizon():
    from kronos_core.data import resolve_future_prediction_timestamps

    last = pd.Timestamp("2026-07-03")
    y_ts, source = resolve_future_prediction_timestamps(last, "2026-07-03", horizon=5)
    assert source == "horizon"
    assert len(y_ts) == 5


def test_resolve_future_prediction_timestamps_until_end():
    from kronos_core.data import resolve_future_prediction_timestamps

    last = pd.Timestamp("2026-07-03")
    y_ts, source = resolve_future_prediction_timestamps(last, "2026-07-10", horizon=3)
    assert source == "until_end"
    assert pd.Timestamp(y_ts.iloc[-1]).normalize() == pd.Timestamp("2026-07-10").normalize()
    assert len(y_ts) > 3


def test_backtest_y_timestamp_uses_data_slice():
    """Backtest path: y_timestamp is last horizon rows from dataframe (unchanged semantics)."""
    horizon = 3
    n = 20
    df = pd.DataFrame(
        {
            "timestamps": pd.bdate_range("2024-01-01", periods=n, freq="B"),
            "close": range(n),
        }
    )
    lookback_end = len(df) - horizon
    y_timestamp = df.loc[lookback_end : lookback_end + horizon - 1, "timestamps"]
    assert len(y_timestamp) == horizon
    assert pd.Timestamp(y_timestamp.iloc[-1]) == pd.Timestamp(df["timestamps"].iloc[-1])


if __name__ == "__main__":
    test_core_modules_importable()
    test_predict_params_from_namespace()
    test_make_future_timestamps_after_last_ts()
    test_make_future_timestamps_until_through_end_date()
    test_resolve_future_prediction_timestamps_fallback_horizon()
    test_resolve_future_prediction_timestamps_until_end()
    test_backtest_y_timestamp_uses_data_slice()
    test_build_chart_series_future_extends_beyond_history()
    test_save_and_load_run_metadata_roundtrip()
    test_list_predictions_legacy_chart_complete_false()
    print("kronos_core smoke tests passed")
