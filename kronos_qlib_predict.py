#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
kronos_qlib_predict.py

用 qlib 本地行情数据 + Kronos 模型，对指定股票做未来K线预测，
输出预测结果 csv 和"预测 vs 真实" K线对比图。

支持两种模式：
1. 普通预测模式（默认）：用最后一段历史窗口预测未来 horizon 天，
   如果预测区间本身有真实数据，会画出对比图。
2. 调参模式（--tune）：在历史区间上做滚动回测，对
   window / T(temperature) / top_p / sample_count 做网格搜索，
   按 close 价格的 MAE / RMSE / MAPE 打分，找出最优参数组合。

用法示例见项目说明文档。
"""

import os
import sys
import argparse
import itertools
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # 服务器/无图形界面环境下也能画图保存
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")


# ----------------------------------------------------------------------
# 1. 命令行参数
# ----------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Kronos + qlib A股K线预测脚本")

    p.add_argument("--data-source", type=str, default="qlib",
                    choices=["qlib", "akshare", "hkshare", "usstock"],
                    help=(
                        "行情数据来源：\n"
                        "  qlib    本地 qlib 数据（需要 --provider-uri，数据截止2020年）\n"
                        "  akshare A股联网实时数据，通过东方财富接口（6位数字代码，如 600519）\n"
                        "  hkshare 港股联网实时数据，通过东方财富接口（5位数字代码，如 00700）\n"
                        "  usstock 美股联网实时数据，通过 yfinance（需先 pip install yfinance，ticker如 AAPL）"
                    ))
    p.add_argument("--provider-uri", type=str, default=None,
                    help="qlib 本地数据目录（--data-source qlib 时必填）")
    p.add_argument("--instrument", type=str, required=True,
                    help="股票代码。qlib模式下如 SH600519；akshare模式下如 600519（不带前缀，6位数字代码即可）")
    p.add_argument("--start", type=str, required=True, help="历史数据起始日期 YYYY-MM-DD")
    p.add_argument("--end", type=str, required=True, help="历史数据结束日期 YYYY-MM-DD")
    p.add_argument("--future", action="store_true",
                    help="开启后强制预测真正的未来（用全部历史数据作为输入窗口，往后预测，"
                         "不会从数据里扣留最后几天当真实值对比）。"
                         "不开启时，如果数据量够长，脚本默认会做历史回测（扣留最后horizon天对比，"
                         "适合检验模型准不准；如果用akshare拿到了最新数据又想看真未来，请加上这个参数）")
    p.add_argument("--adjust", type=str, default="qfq", choices=["", "qfq", "hfq"],
                    help="akshare模式下的复权方式：qfq前复权（默认，推荐）/ hfq后复权 / 空字符串不复权")
    p.add_argument("--model-path", type=str, required=True, help="Kronos 模型目录或 HF repo id")
    p.add_argument("--tokenizer-path", type=str, required=True, help="Kronos tokenizer 目录或 HF repo id")

    p.add_argument("--window", type=int, default=64, help="输入给模型的历史K线窗口长度（lookback）")
    p.add_argument("--horizon", type=int, default=5, help="预测未来多少个交易日")
    p.add_argument("--seed", type=int, default=40, help="随机种子，保证结果可复现")

    p.add_argument("--temperature", "--temp", dest="temperature", type=float, default=1.0, help="采样温度 T")
    p.add_argument("--top-p", type=float, default=0.9, help="nucleus sampling 概率")
    p.add_argument("--sample-count", type=int, default=1, help="采样次数，多次采样取均值更稳")

    p.add_argument("--output-dir", type=str, default="predictions",
                    help="统一保存预测结果的文件夹，默认 predictions（脚本会自动创建）")
    p.add_argument("--out", type=str, default=None,
                    help="预测结果输出 csv 路径。不填则自动按股票代码+参数+时间戳生成文件名，存入 --output-dir")
    p.add_argument("--chart-out", type=str, default=None,
                    help="预测对比图输出路径。不填则自动按股票代码+参数+时间戳生成文件名，存入 --output-dir")

    p.add_argument("--max-context", type=int, default=512, help="模型支持的最大上下文长度")
    p.add_argument("--device", type=str, default="cpu", help="运行设备，CPU 环境写 cpu 即可")

    # ---- 调参模式相关参数 ----
    p.add_argument("--tune", action="store_true", help="开启自动网格搜索调参模式")
    p.add_argument("--grid-window", type=str, default="64,128,256", help="window 候选值，逗号分隔")
    p.add_argument("--grid-temp", type=str, default="1.0,0.9", help="温度候选值，逗号分隔")
    p.add_argument("--grid-top-p", type=str, default="0.95,0.9", help="top_p 候选值，逗号分隔")
    p.add_argument("--grid-sample-count", type=str, default="1,5", help="sample_count 候选值，逗号分隔")
    p.add_argument("--tune-stride", type=int, default=5, help="滚动回测的步长（每隔多少天评估一次）")
    p.add_argument("--tune-max-windows", type=int, default=120, help="滚动回测最多评估多少个窗口（控制耗时）")
    p.add_argument("--tune-out", type=str, default=None,
                    help="调参结果输出 csv 路径。不填则自动按股票代码+参数+时间戳生成文件名，存入 --output-dir")

    args = p.parse_args()
    if args.data_source == "qlib" and not args.provider_uri:
        p.error("--data-source qlib 模式下必须指定 --provider-uri")
    return args


# ----------------------------------------------------------------------
# 2. 从 qlib 读取数据，整理成 Kronos 需要的格式
# ----------------------------------------------------------------------
def load_qlib_kline(provider_uri, instrument, start, end):
    """
    返回一个按时间升序排列的 DataFrame，
    包含列：timestamps, open, high, low, close, volume, amount
    """
    import qlib
    from qlib.data import D

    qlib.init(provider_uri=provider_uri, region="cn")

    fields = ["$open", "$high", "$low", "$close", "$volume"]
    df = D.features([instrument], fields, start_time=start, end_time=end, freq="day")

    if df is None or len(df) == 0:
        raise RuntimeError(
            f"没有取到 {instrument} 在 {start} ~ {end} 的数据，"
            f"请检查 provider-uri 路径、股票代码格式，以及该区间是否有交易日数据。"
        )

    df = df.droplevel(0)  # 去掉 instrument 这一层 MultiIndex
    df = df.rename(
        columns={
            "$open": "open",
            "$high": "high",
            "$low": "low",
            "$close": "close",
            "$volume": "volume",
        }
    )
    df["amount"] = df["close"] * df["volume"]  # qlib 默认不直接给 amount，这里用近似值代替
    df = df.sort_index()
    df = df.reset_index().rename(columns={"datetime": "timestamps"})
    df["timestamps"] = pd.to_datetime(df["timestamps"])
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    return df


# ----------------------------------------------------------------------
# 2.5 直接用 requests 请求东方财富接口获取最新行情（不依赖 akshare）
# 经测试，东财接口需要带 Referer 和 User-Agent 才会正常返回数据
# ----------------------------------------------------------------------
def load_akshare_kline(instrument, start, end, adjust="qfq"):
    """
    直接请求东方财富行情接口，获取 A 股日线历史数据（支持获取到当前最新交易日）。
    instrument: 6位股票代码，如 '600519'，或带 SH/SZ 前缀，脚本会自动去掉前缀
    adjust: 复权方式，qfq=前复权（默认）/ hfq=后复权 / 空字符串=不复权
    返回格式和 load_qlib_kline 一致：timestamps, open, high, low, close, volume, amount
    """
    import requests as req

    # 去掉可能带的 sh/sz/SH/SZ 前缀
    code = instrument.upper().replace("SH", "").replace("SZ", "").strip()

    # 判断市场：6开头是沪市(1)，其余是深市(0)
    market = "1" if code.startswith("6") else "0"

    # 复权参数：0=不复权 1=前复权 2=后复权
    adjust_map = {"": "0", "qfq": "1", "hfq": "2"}
    fqt = adjust_map.get(adjust, "1")

    start_fmt = start.replace("-", "")
    end_fmt = end.replace("-", "")

    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "klt": "101",   # 日线
        "fqt": fqt,
        "secid": f"{market}.{code}",
        "beg": start_fmt,
        "end": end_fmt,
    }
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://quote.eastmoney.com/",
    }

    print(f"[INFO] 正在通过东方财富接口获取 {code} 的行情数据（{start} ~ {end}）...")
    try:
        r = req.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"请求东方财富接口失败：{e}")

    data = r.json()
    if data.get("rc") != 0 or not data.get("data") or not data["data"].get("klines"):
        raise RuntimeError(
            f"东方财富接口返回异常，rc={data.get('rc')}，"
            f"股票代码 {code} 在 {start}~{end} 可能没有数据，"
            f"请检查代码是否正确、区间是否有交易日。\n原始返回：{str(data)[:300]}"
        )

    # 解析 klines 字段：每行格式为
    # "日期,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率"
    records = []
    for line in data["data"]["klines"]:
        parts = line.split(",")
        records.append({
            "timestamps": pd.to_datetime(parts[0]),
            "open":   float(parts[1]),
            "close":  float(parts[2]),
            "high":   float(parts[3]),
            "low":    float(parts[4]),
            "volume": float(parts[5]),
            "amount": float(parts[6]),
        })

    df = pd.DataFrame(records)
    df = df.sort_values("timestamps").reset_index(drop=True)
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    print(f"[INFO] 成功获取 {len(df)} 条K线数据（{df['timestamps'].iloc[0].date()} ~ {df['timestamps'].iloc[-1].date()}）")
    return df


def load_hkstock_kline(instrument, start, end):
    """
    通过东方财富接口获取港股日线数据。
    instrument: 港股代码，支持以下格式（脚本会自动统一处理）：
      - 纯数字：'00700'（腾讯）、'09988'（阿里）
      - 带前缀：'HK00700' 或 'hk00700'
    东方财富港股 secid 格式为 116.XXXXX（5位数字，不足5位前面补0）
    """
    import requests as req

    # 去掉可能带的 HK/hk 前缀，统一处理成纯数字
    code = instrument.upper().replace("HK", "").strip()
    # 港股代码统一补齐到5位（东财要求）
    code = code.zfill(5)

    start_fmt = start.replace("-", "")
    end_fmt = end.replace("-", "")

    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "klt": "101",
        "fqt": "1",          # 港股默认前复权
        "secid": f"116.{code}",  # 116 是东财港股市场标识
        "beg": start_fmt,
        "end": end_fmt,
    }
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://quote.eastmoney.com/",
    }

    print(f"[INFO] 正在通过东方财富接口获取港股 {code} 的行情数据（{start} ~ {end}）...")
    try:
        r = req.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"请求东方财富港股接口失败：{e}")

    data = r.json()
    if data.get("rc") != 0 or not data.get("data") or not data["data"].get("klines"):
        raise RuntimeError(
            f"东方财富港股接口返回异常，rc={data.get('rc')}，"
            f"港股代码 {code} 在 {start}~{end} 可能没有数据。\n"
            f"请检查代码格式（5位数字，如 00700 表示腾讯）。\n原始返回：{str(data)[:300]}"
        )

    records = []
    for line in data["data"]["klines"]:
        parts = line.split(",")
        records.append({
            "timestamps": pd.to_datetime(parts[0]),
            "open":   float(parts[1]),
            "close":  float(parts[2]),
            "high":   float(parts[3]),
            "low":    float(parts[4]),
            "volume": float(parts[5]),
            "amount": float(parts[6]),
        })

    df = pd.DataFrame(records)
    df = df.sort_values("timestamps").reset_index(drop=True)
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    stock_name = data["data"].get("name", code)
    print(f"[INFO] 成功获取港股「{stock_name}」{len(df)} 条K线（{df['timestamps'].iloc[0].date()} ~ {df['timestamps'].iloc[-1].date()}）")
    return df


def load_usstock_kline(instrument, start, end):
    """
    通过 yfinance 获取美股（及 ETF）日线数据。
    instrument: 美股 ticker，如 'AAPL'、'TSLA'、'QQQ'，大小写均可
    需要先安装：pip install yfinance
    """
    try:
        import yfinance as yf
    except ImportError:
        raise RuntimeError(
            "没有安装 yfinance，请先执行：\n"
            "  pip install yfinance\n"
            "（国内网络通常能直接安装，如果慢可以加 -i https://pypi.tuna.tsinghua.edu.cn/simple）"
        )

    ticker = instrument.upper().strip()
    print(f"[INFO] 正在通过 yfinance 获取美股 {ticker} 的行情数据（{start} ~ {end}）...")

    # yfinance end 日期是开区间，需要加一天才能包含 end 当天
    end_dt = (pd.Timestamp(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    raw = yf.download(ticker, start=start, end=end_dt, progress=False, auto_adjust=True)

    if raw is None or len(raw) == 0:
        raise RuntimeError(
            f"yfinance 没有取到 {ticker} 在 {start}~{end} 的数据，"
            f"请检查 ticker 是否正确（如苹果是 AAPL，特斯拉是 TSLA），"
            f"以及网络是否能访问 Yahoo Finance（需要能连境外网络）。"
        )

    # yfinance 返回 MultiIndex 列，把它展平
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    df = raw.rename(columns={
        "Open":   "open",
        "High":   "high",
        "Low":    "low",
        "Close":  "close",
        "Volume": "volume",
    })
    df = df[["open", "high", "low", "close", "volume"]].copy()
    df["amount"] = df["close"] * df["volume"]   # 美股通常没有直接的成交额字段，用近似值
    df = df.reset_index().rename(columns={"Date": "timestamps", "Datetime": "timestamps"})
    df["timestamps"] = pd.to_datetime(df["timestamps"]).dt.tz_localize(None)  # 去掉时区信息
    df = df[["timestamps", "open", "high", "low", "close", "volume", "amount"]]
    df = df.sort_values("timestamps").reset_index(drop=True)
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    print(f"[INFO] 成功获取美股「{ticker}」{len(df)} 条K线（{df['timestamps'].iloc[0].date()} ~ {df['timestamps'].iloc[-1].date()}）")
    return df


def load_kline_data(args):
    """统一入口：根据 --data-source 选择数据来源"""
    if args.data_source == "akshare":
        return load_akshare_kline(args.instrument, args.start, args.end, adjust=args.adjust)
    elif args.data_source == "hkshare":
        return load_hkstock_kline(args.instrument, args.start, args.end)
    elif args.data_source == "usstock":
        return load_usstock_kline(args.instrument, args.start, args.end)
    else:
        return load_qlib_kline(args.provider_uri, args.instrument, args.start, args.end)


def load_kronos_predictor(model_path, tokenizer_path, max_context, device):
    from model import Kronos, KronosTokenizer, KronosPredictor

    print(f"[INFO] 正在加载 tokenizer: {tokenizer_path}")
    tokenizer = KronosTokenizer.from_pretrained(tokenizer_path)

    print(f"[INFO] 正在加载模型: {model_path}")
    model = Kronos.from_pretrained(model_path)

    predictor = KronosPredictor(model, tokenizer, device=device, max_context=max_context)
    return predictor


# ----------------------------------------------------------------------
# 4. 生成未来交易日时间戳（简单按自然日跳过周末，足够日线场景使用）
# ----------------------------------------------------------------------
def make_future_timestamps(last_ts, horizon):
    future = pd.bdate_range(start=last_ts + pd.Timedelta(days=1), periods=horizon, freq="B")
    return pd.Series(future)


# ----------------------------------------------------------------------
# 4.5 自动生成不会互相覆盖、且能看出股票代码的输出文件名
# ----------------------------------------------------------------------
def build_output_path(output_dir, instrument, tag, ext, window=None, horizon=None,
                       pred_start=None, pred_end=None):
    """
    生成形如：predictions/SH600519_pred20260701-20260707_w64_h5_run20260630-165530_predict.csv 的路径
    pred_start / pred_end：本次预测覆盖的日期区间（YYYYMMDD），让文件名能直接看出预测的是哪几天
    tag: 'predict' 或 'tune'，用来区分是单次预测结果还是调参结果
    """
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
    parts.append(f"run{run_timestamp}")  # 同一天预测同一区间也不会互相覆盖
    parts.append(tag)
    filename = "_".join(parts) + f".{ext}"
    return os.path.join(output_dir, filename)


def resolve_out_paths(args, pred_start=None, pred_end=None):
    """
    如果用户没有手动指定 --out / --chart-out，就自动生成统一存放、互不覆盖的文件名，
    文件名里会带上本次预测覆盖的日期区间（pred_start ~ pred_end）。
    如果用户手动指定了，就尊重用户的指定（此时不保证不覆盖，由用户自己负责）。
    """
    if args.out is None:
        args.out = build_output_path(args.output_dir, args.instrument, "predict", "csv",
                                       window=args.window, horizon=args.horizon,
                                       pred_start=pred_start, pred_end=pred_end)
    if args.chart_out is None:
        args.chart_out = build_output_path(args.output_dir, args.instrument, "predict", "png",
                                             window=args.window, horizon=args.horizon,
                                             pred_start=pred_start, pred_end=pred_end)
    return args


# ----------------------------------------------------------------------
# 5. 单次预测 + 画图 + 导出 csv
# ----------------------------------------------------------------------
def run_single_predict(args):
    set_seed(args.seed)

    df = load_kline_data(args)
    print(f"[INFO] 共取到 {len(df)} 条历史K线（{df['timestamps'].iloc[0].date()} ~ {df['timestamps'].iloc[-1].date()}）")

    not_enough_data = len(df) < args.window + args.horizon

    if args.future or not_enough_data:
        if not_enough_data and not args.future:
            print(
                f"[WARN] 历史数据量({len(df)})小于 window+horizon({args.window + args.horizon})，"
                f"自动切换为预测真正未来模式（不含真实值对比）。"
            )
        else:
            print(f"[INFO] --future 模式：用全部历史数据作为输入窗口，预测真正还未发生的未来 {args.horizon} 天，不做历史回测对比。")
        x_df = df[["open", "high", "low", "close", "volume", "amount"]]
        x_timestamp = df["timestamps"]
        y_timestamp = make_future_timestamps(df["timestamps"].iloc[-1], args.horizon)
        gt_df = None
    else:
        # 历史回测模式：把最后 horizon 天留出来当作"真实值"用于对比评分
        print(f"[INFO] 历史回测模式：扣留最后 {args.horizon} 天真实数据用于对比评分。"
              f"如果想预测真正的未来，请加上 --future 参数。")
        lookback_end = len(df) - args.horizon
        lookback_start = max(0, lookback_end - args.window)

        x_df = df.loc[lookback_start:lookback_end - 1, ["open", "high", "low", "close", "volume", "amount"]]
        x_timestamp = df.loc[lookback_start:lookback_end - 1, "timestamps"]
        y_timestamp = df.loc[lookback_end:lookback_end + args.horizon - 1, "timestamps"]
        gt_df = df.loc[lookback_end:lookback_end + args.horizon - 1].reset_index(drop=True)

    # 现在已经知道预测的具体起止日期了，再生成输出文件名（文件名里会带上预测日期区间）
    pred_start = pd.Timestamp(y_timestamp.iloc[0]).strftime("%Y%m%d")
    pred_end = pd.Timestamp(y_timestamp.iloc[-1]).strftime("%Y%m%d")
    args = resolve_out_paths(args, pred_start=pred_start, pred_end=pred_end)

    predictor = load_kronos_predictor(args.model_path, args.tokenizer_path, args.max_context, args.device)

    print(f"[INFO] 开始预测：window={len(x_df)}, horizon={args.horizon}, "
          f"T={args.temperature}, top_p={args.top_p}, sample_count={args.sample_count}")

    pred_df = predictor.predict(
        df=x_df.reset_index(drop=True),
        x_timestamp=x_timestamp.reset_index(drop=True),
        y_timestamp=y_timestamp.reset_index(drop=True),
        pred_len=args.horizon,
        T=args.temperature,
        top_p=args.top_p,
        sample_count=args.sample_count,
        verbose=True,
    )
    pred_df = pred_df.reset_index(drop=True)
    pred_df.insert(0, "timestamps", y_timestamp.reset_index(drop=True).values)

    # 导出 csv
    out_path = os.path.abspath(args.out)
    pred_df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[INFO] 预测结果已保存到: {out_path}")

    # 画图
    chart_path = os.path.abspath(args.chart_out)
    plot_prediction(
        x_df=x_df,
        x_timestamp=x_timestamp,
        pred_df=pred_df,
        gt_df=gt_df,
        instrument=args.instrument,
        save_path=chart_path,
    )
    print(f"[INFO] 预测K线图已保存到: {chart_path}")

    if gt_df is not None:
        metrics = compute_metrics(gt_df["close"].values, pred_df["close"].values)
        print(f"[INFO] 预测区间误差（与真实值对比）：MAE={metrics['mae']:.4f}, "
              f"RMSE={metrics['rmse']:.4f}, MAPE={metrics['mape']:.2f}%")


# ----------------------------------------------------------------------
# 6. 画"预测 vs 真实"K线对比图
# ----------------------------------------------------------------------
def plot_prediction(x_df, x_timestamp, pred_df, gt_df, instrument, save_path):
    fig, ax = plt.subplots(figsize=(11, 5))

    # 历史真实K线（收盘价）
    ax.plot(x_timestamp.values, x_df["close"].values, label="历史真实收盘价", color="#2c3e50", linewidth=1.5)

    # 取历史最后一个点，作为预测线/真实对比线的起点，让三条线在视觉上连起来
    # （只影响画图，不影响导出的 csv 数据本身）
    last_ts = x_timestamp.values[-1]
    last_close = x_df["close"].values[-1]

    # 预测部分：在最前面拼接历史最后一个点
    pred_plot_ts = np.concatenate([[last_ts], pred_df["timestamps"].values])
    pred_plot_close = np.concatenate([[last_close], pred_df["close"].values])
    ax.plot(pred_plot_ts, pred_plot_close, label="预测收盘价", color="#e74c3c",
             linewidth=1.8, linestyle="--", marker="o", markersize=3)

    # 如果有真实未来值，也画出来做对比，同样从历史最后一点接上
    if gt_df is not None:
        gt_plot_ts = np.concatenate([[last_ts], gt_df["timestamps"].values])
        gt_plot_close = np.concatenate([[last_close], gt_df["close"].values])
        ax.plot(gt_plot_ts, gt_plot_close, label="真实收盘价（对比）", color="#27ae60",
                 linewidth=1.8, marker="o", markersize=3)

    ax.set_title(f"{instrument} Kronos 预测 vs 真实 K线（收盘价）")
    ax.set_xlabel("日期")
    ax.set_ylabel("价格")
    ax.legend(loc="best")
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


# ----------------------------------------------------------------------
# 7. 误差指标
# ----------------------------------------------------------------------
def compute_metrics(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    mape = np.mean(np.abs((y_true - y_pred) / np.clip(np.abs(y_true), 1e-8, None))) * 100
    return {"mae": mae, "rmse": rmse, "mape": mape}


def set_seed(seed):
    import random
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
    except ImportError:
        pass


# ----------------------------------------------------------------------
# 8. 调参模式：滚动回测 + 网格搜索
# ----------------------------------------------------------------------
def run_tune(args):
    set_seed(args.seed)
    if args.tune_out is None:
        args.tune_out = build_output_path(args.output_dir, args.instrument, "tune", "csv")

    df = load_kline_data(args)
    print(f"[INFO] 共取到 {len(df)} 条历史K线，用于滚动回测调参。")

    windows = [int(x) for x in args.grid_window.split(",")]
    temps = [float(x) for x in args.grid_temp.split(",")]
    top_ps = [float(x) for x in args.grid_top_p.split(",")]
    sample_counts = [int(x) for x in args.grid_sample_count.split(",")]

    predictor = load_kronos_predictor(args.model_path, args.tokenizer_path, args.max_context, args.device)

    results = []
    combos = list(itertools.product(windows, temps, top_ps, sample_counts))
    print(f"[INFO] 共 {len(combos)} 组参数组合，每组最多评估 {args.tune_max_windows} 个滚动窗口。")

    for combo_idx, (window, T, top_p, sample_count) in enumerate(combos, start=1):
        max_lookback_end = len(df) - args.horizon
        min_lookback_end = window
        if max_lookback_end <= min_lookback_end:
            print(f"[WARN] 数据量不足以支撑 window={window}，跳过该组合。")
            continue

        eval_points = list(range(min_lookback_end, max_lookback_end, args.tune_stride))
        if len(eval_points) > args.tune_max_windows:
            # 等间隔抽样，控制耗时
            idx = np.linspace(0, len(eval_points) - 1, args.tune_max_windows).astype(int)
            eval_points = [eval_points[i] for i in idx]

        errors = []
        for lookback_end in eval_points:
            lookback_start = lookback_end - window
            x_df = df.loc[lookback_start:lookback_end - 1, ["open", "high", "low", "close", "volume", "amount"]].reset_index(drop=True)
            x_timestamp = df.loc[lookback_start:lookback_end - 1, "timestamps"].reset_index(drop=True)
            y_timestamp = df.loc[lookback_end:lookback_end + args.horizon - 1, "timestamps"].reset_index(drop=True)
            gt_close = df.loc[lookback_end:lookback_end + args.horizon - 1, "close"].values

            try:
                pred_df = predictor.predict(
                    df=x_df, x_timestamp=x_timestamp, y_timestamp=y_timestamp,
                    pred_len=args.horizon, T=T, top_p=top_p, sample_count=sample_count, verbose=False,
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

        print(f"[{combo_idx}/{len(combos)}] window={window}, T={T}, top_p={top_p}, "
              f"sample_count={sample_count} -> MAE={mae:.4f}, RMSE={rmse:.4f}, MAPE={mape:.2f}%  "
              f"(评估了 {len(errors)} 个窗口)")

        results.append({
            "window": window, "T": T, "top_p": top_p, "sample_count": sample_count,
            "mae": mae, "rmse": rmse, "mape": mape, "n_eval_windows": len(errors),
        })

    if not results:
        print("[ERROR] 没有任何参数组合成功完成回测，请检查数据量是否足够，或调小 grid 范围。")
        return

    result_df = pd.DataFrame(results).sort_values("rmse").reset_index(drop=True)
    out_path = os.path.abspath(args.tune_out)
    result_df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[INFO] 调参结果已保存到: {out_path}")

    best = result_df.iloc[0]
    print("=" * 60)
    print(f"[BEST] 最优参数组合（按 RMSE 排序）：")
    print(f"  window={int(best['window'])}, T={best['T']}, top_p={best['top_p']}, "
          f"sample_count={int(best['sample_count'])}")
    print(f"  MAE={best['mae']:.4f}, RMSE={best['rmse']:.4f}, MAPE={best['mape']:.2f}%")
    print("=" * 60)


# ----------------------------------------------------------------------
# 9. 主入口
# ----------------------------------------------------------------------
def main():
    args = parse_args()

    # 让中文在 matplotlib 图里正常显示
    try:
        plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "SimHei", "Arial Unicode MS"]
        plt.rcParams["axes.unicode_minus"] = False
    except Exception:
        pass

    if args.tune:
        run_tune(args)
    else:
        run_single_predict(args)


if __name__ == "__main__":
    main()
