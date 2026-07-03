import pandas as pd

from kronos_core.params import PredictParams

_EASTMONEY_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://quote.eastmoney.com/",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
}

_EASTMONEY_HOSTS = (
    "https://push2his.eastmoney.com",
    "https://82.push2his.eastmoney.com",
    "https://91.push2his.eastmoney.com",
)

_PROXY_ENV_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "NO_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "no_proxy",
    "SOCKS_PROXY",
    "SOCKS5_PROXY",
    "socks_proxy",
    "socks5_proxy",
)


def _without_proxy_env():
    import os
    from contextlib import contextmanager

    @contextmanager
    def _ctx():
        saved = {k: os.environ.pop(k) for k in _PROXY_ENV_KEYS if k in os.environ}
        try:
            yield
        finally:
            os.environ.update(saved)

    return _ctx()


def _direct_http_get(url: str, timeout: int = 15) -> str:
    """直连 HTTP GET，忽略所有代理配置。"""
    import urllib.error
    import urllib.request

    request = urllib.request.Request(url, headers=_EASTMONEY_HEADERS)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    with _without_proxy_env():
        try:
            with opener.open(request, timeout=timeout) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raise ConnectionError(f"HTTP {e.code}: {e.reason}") from e
        except urllib.error.URLError as e:
            raise ConnectionError(str(e.reason or e)) from e


def _eastmoney_get(path: str, params: dict, timeout: int = 15):
    import json
    import time
    import urllib.parse

    query = urllib.parse.urlencode(params)
    errors = []

    for host in _EASTMONEY_HOSTS:
        url = f"{host}{path}?{query}"
        for attempt in range(2):
            try:
                body = _direct_http_get(url, timeout=timeout)
                data = json.loads(body)

                class _Response:
                    def json(self):
                        return data

                return _Response()
            except Exception as e:
                errors.append(f"{host}#{attempt + 1}: {e}")
                time.sleep(0.6)

    raise ConnectionError("; ".join(errors[-3:]))


def _parse_eastmoney_klines(data: dict) -> list[dict]:
    records = []
    for line in data["data"]["klines"]:
        parts = line.split(",")
        close = float(parts[2])
        volume = float(parts[5])
        records.append(
            {
                "timestamps": pd.to_datetime(parts[0]),
                "open": float(parts[1]),
                "close": close,
                "high": float(parts[3]),
                "low": float(parts[4]),
                "volume": volume,
                "amount": float(parts[6]) if len(parts) > 6 else close * volume,
            }
        )
    return records


def _load_tencent_a_kline(code: str, start: str, end: str, adjust: str = "qfq"):
    """A 股备用数据源：腾讯财经（东财限流/封 IP 时自动切换）。"""
    import json
    import re
    import urllib.parse

    tx_code = ("sh" if code.startswith("6") else "sz") + code
    if adjust == "hfq":
        adjust_tag = "hfq"
        series_key = "hfqday"
    elif adjust == "qfq":
        adjust_tag = "qfq"
        series_key = "qfqday"
    else:
        adjust_tag = ""
        series_key = "day"

    param = f"{tx_code},day,{start},{end},1000"
    if adjust_tag:
        param = f"{param},{adjust_tag}"
    var = f"kline_day{adjust_tag}" if adjust_tag else "kline_day"
    url = (
        "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?"
        + urllib.parse.urlencode({"param": param, "_var": var})
    )

    print(f"[INFO] 东财不可用，改用腾讯财经接口获取 {code}（{start} ~ {end}）...")
    body = _direct_http_get(url)
    match = re.search(r"\{.*\}\s*$", body, re.DOTALL)
    if not match:
        raise RuntimeError(f"腾讯财经接口返回异常：{body[:300]}")
    payload = json.loads(match.group(0))
    if payload.get("code") != 0:
        raise RuntimeError(f"腾讯财经接口返回 code={payload.get('code')} msg={payload.get('msg')}")

    stock_data = payload.get("data", {}).get(tx_code, {})
    rows = stock_data.get(series_key) or stock_data.get("day") or stock_data.get("qfqday") or []
    if not rows:
        raise RuntimeError(f"腾讯财经未返回 {code} 在 {start}~{end} 的K线数据")

    records = []
    for parts in rows:
        close = float(parts[2])
        volume = float(parts[5])
        records.append(
            {
                "timestamps": pd.to_datetime(parts[0]),
                "open": float(parts[1]),
                "close": close,
                "high": float(parts[3]),
                "low": float(parts[4]),
                "volume": volume,
                "amount": close * volume,
            }
        )
    return records


def _records_to_dataframe(records: list[dict], source_label: str) -> pd.DataFrame:
    df = pd.DataFrame(records)
    df = df.sort_values("timestamps").reset_index(drop=True)
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    print(
        f"[INFO] 成功通过{source_label}获取 {len(df)} 条K线"
        f"（{df['timestamps'].iloc[0].date()} ~ {df['timestamps'].iloc[-1].date()}）"
    )
    return df


def load_qlib_kline(provider_uri, instrument, start, end):
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

    df = df.droplevel(0)
    df = df.rename(
        columns={
            "$open": "open",
            "$high": "high",
            "$low": "low",
            "$close": "close",
            "$volume": "volume",
        }
    )
    df["amount"] = df["close"] * df["volume"]
    df = df.sort_index()
    df = df.reset_index().rename(columns={"datetime": "timestamps"})
    df["timestamps"] = pd.to_datetime(df["timestamps"])
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    return df


def load_akshare_kline(instrument, start, end, adjust="qfq"):
    code = instrument.upper().replace("SH", "").replace("SZ", "").strip()
    market = "1" if code.startswith("6") else "0"
    adjust_map = {"": "0", "qfq": "1", "hfq": "2"}
    fqt = adjust_map.get(adjust, "1")

    start_fmt = start.replace("-", "")
    end_fmt = end.replace("-", "")

    params = {
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "klt": "101",
        "fqt": fqt,
        "secid": f"{market}.{code}",
        "beg": start_fmt,
        "end": end_fmt,
    }

    print(f"[INFO] 正在通过东方财富接口获取 {code} 的行情数据（{start} ~ {end}）...")
    try:
        r = _eastmoney_get("/api/qt/stock/kline/get", params)
        data = r.json()
        if data.get("rc") != 0 or not data.get("data") or not data["data"].get("klines"):
            raise RuntimeError(
                f"东方财富返回异常 rc={data.get('rc')}，原始：{str(data)[:200]}"
            )
        records = _parse_eastmoney_klines(data)
        return _records_to_dataframe(records, "东方财富")
    except Exception as eastmoney_error:
        print(f"[WARN] 东方财富接口失败：{eastmoney_error}")
        try:
            records = _load_tencent_a_kline(code, start, end, adjust=adjust)
            return _records_to_dataframe(records, "腾讯财经（备用）")
        except Exception as tencent_error:
            raise RuntimeError(
                f"行情获取失败。东方财富：{eastmoney_error}；腾讯财经：{tencent_error}。"
                f"东财常见原因是 IP 被限流/封禁（Remote end closed connection），"
                f"可等待几小时后重试，或暂时改用 --data-source qlib 本地数据。"
            ) from tencent_error


def load_hkstock_kline(instrument, start, end):
    code = instrument.upper().replace("HK", "").strip()
    code = code.zfill(5)

    start_fmt = start.replace("-", "")
    end_fmt = end.replace("-", "")

    params = {
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "klt": "101",
        "fqt": "1",
        "secid": f"116.{code}",
        "beg": start_fmt,
        "end": end_fmt,
    }

    print(f"[INFO] 正在通过东方财富接口获取港股 {code} 的行情数据（{start} ~ {end}）...")
    try:
        r = _eastmoney_get("/api/qt/stock/kline/get", params)
    except Exception as e:
        raise RuntimeError(
            f"请求东方财富港股接口失败：{e}。"
            f"若报 Remote end closed connection，可能是东财临时封 IP，请稍后重试。"
        ) from e

    data = r.json()
    if data.get("rc") != 0 or not data.get("data") or not data["data"].get("klines"):
        raise RuntimeError(
            f"东方财富港股接口返回异常，rc={data.get('rc')}，"
            f"港股代码 {code} 在 {start}~{end} 可能没有数据。\n"
            f"请检查代码格式（5位数字，如 00700 表示腾讯）。\n原始返回：{str(data)[:300]}"
        )

    records = _parse_eastmoney_klines(data)
    df = pd.DataFrame(records)
    df = df.sort_values("timestamps").reset_index(drop=True)
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    stock_name = data["data"].get("name", code)
    print(
        f"[INFO] 成功获取港股「{stock_name}」{len(df)} 条K线（{df['timestamps'].iloc[0].date()} ~ {df['timestamps'].iloc[-1].date()}）"
    )
    return df


def load_usstock_kline(instrument, start, end):
    try:
        import yfinance as yf
    except ImportError as e:
        raise RuntimeError(
            "没有安装 yfinance，请先执行：\n"
            "  pip install yfinance\n"
            "（国内网络通常能直接安装，如果慢可以加 -i https://pypi.tuna.tsinghua.edu.cn/simple）"
        ) from e

    ticker = instrument.upper().strip()
    print(f"[INFO] 正在通过 yfinance 获取美股 {ticker} 的行情数据（{start} ~ {end}）...")

    end_dt = (pd.Timestamp(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    raw = yf.download(ticker, start=start, end=end_dt, progress=False, auto_adjust=True)

    if raw is None or len(raw) == 0:
        raise RuntimeError(
            f"yfinance 没有取到 {ticker} 在 {start}~{end} 的数据，"
            f"请检查 ticker 是否正确（如苹果是 AAPL，特斯拉是 TSLA），"
            f"以及网络是否能访问 Yahoo Finance（需要能连境外网络）。"
        )

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    df = raw.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    df = df[["open", "high", "low", "close", "volume"]].copy()
    df["amount"] = df["close"] * df["volume"]
    df = df.reset_index().rename(columns={"Date": "timestamps", "Datetime": "timestamps"})
    df["timestamps"] = pd.to_datetime(df["timestamps"]).dt.tz_localize(None)
    df = df[["timestamps", "open", "high", "low", "close", "volume", "amount"]]
    df = df.sort_values("timestamps").reset_index(drop=True)
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    print(
        f"[INFO] 成功获取美股「{ticker}」{len(df)} 条K线（{df['timestamps'].iloc[0].date()} ~ {df['timestamps'].iloc[-1].date()}）"
    )
    return df


def load_kline_data(params: PredictParams):
    if params.data_source == "akshare":
        return load_akshare_kline(params.instrument, params.start, params.end, adjust=params.adjust)
    if params.data_source == "hkshare":
        return load_hkstock_kline(params.instrument, params.start, params.end)
    if params.data_source == "usstock":
        return load_usstock_kline(params.instrument, params.start, params.end)
    if not params.provider_uri:
        raise RuntimeError("--data-source qlib 模式下必须指定 provider_uri")
    return load_qlib_kline(params.provider_uri, params.instrument, params.start, params.end)


def make_future_timestamps(last_ts, horizon):
    future = pd.bdate_range(start=last_ts + pd.Timedelta(days=1), periods=horizon, freq="B")
    return pd.Series(future)


def make_future_timestamps_until(last_ts, end_ts, *, max_periods: int = 60) -> pd.Series:
    """Business days strictly after last_ts through end_ts (inclusive). Empty if end <= last_ts."""
    last = pd.Timestamp(last_ts).normalize()
    end = pd.Timestamp(end_ts).normalize()
    if end <= last:
        return pd.Series(dtype="datetime64[ns]")
    future = pd.bdate_range(start=last + pd.Timedelta(days=1), end=end, freq="B")
    if len(future) > max_periods:
        print(
            f"[WARN] 预测区间 {len(future)} 个交易日超过上限 {max_periods}，"
            f"已截断至前 {max_periods} 天。"
        )
        future = future[:max_periods]
    return pd.Series(future)


def resolve_future_prediction_timestamps(
    last_ts,
    end_date: str,
    horizon: int,
    *,
    max_periods: int = 60,
) -> tuple[pd.Series, str]:
    """Return (y_timestamp, source) where source is 'until_end' or 'horizon'."""
    y_until = make_future_timestamps_until(last_ts, end_date, max_periods=max_periods)
    if len(y_until) > 0:
        return y_until, "until_end"
    return make_future_timestamps(last_ts, horizon), "horizon"
