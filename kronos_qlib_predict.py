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

import argparse
import warnings

import matplotlib

matplotlib.use("Agg")
warnings.filterwarnings("ignore")

from kronos_core.chart import configure_matplotlib_fonts
from kronos_core.params import PredictParams, TuneParams
from kronos_core.predict import run_single_predict_cli
from kronos_core.tune import run_tune_cli


def parse_args():
    p = argparse.ArgumentParser(description="Kronos + qlib A股K线预测脚本")

    p.add_argument(
        "--data-source",
        type=str,
        default="qlib",
        choices=["qlib", "akshare", "hkshare", "usstock"],
        help=(
            "行情数据来源：\n"
            "  qlib    本地 qlib 数据（需要 --provider-uri，数据截止2020年）\n"
            "  akshare A股联网实时数据，通过东方财富接口（6位数字代码，如 600519）\n"
            "  hkshare 港股联网实时数据，通过东方财富接口（5位数字代码，如 00700）\n"
            "  usstock 美股联网实时数据，通过 yfinance（需先 pip install yfinance，ticker如 AAPL）"
        ),
    )
    p.add_argument(
        "--provider-uri",
        type=str,
        default=None,
        help="qlib 本地数据目录（--data-source qlib 时必填）",
    )
    p.add_argument(
        "--instrument",
        type=str,
        required=True,
        help="股票代码。qlib模式下如 SH600519；akshare模式下如 600519（不带前缀，6位数字代码即可）",
    )
    p.add_argument("--start", type=str, required=True, help="历史数据起始日期 YYYY-MM-DD")
    p.add_argument("--end", type=str, required=True, help="历史数据结束日期 YYYY-MM-DD")
    p.add_argument(
        "--future",
        action="store_true",
        help="开启后强制预测真正的未来（用全部历史数据作为输入窗口，往后预测，"
        "不会从数据里扣留最后几天当真实值对比）。"
        "不开启时，如果数据量够长，脚本默认会做历史回测（扣留最后horizon天对比，"
        "适合检验模型准不准；如果用akshare拿到了最新数据又想看真未来，请加上这个参数）",
    )
    p.add_argument(
        "--adjust",
        type=str,
        default="qfq",
        choices=["", "qfq", "hfq"],
        help="akshare模式下的复权方式：qfq前复权（默认，推荐）/ hfq后复权 / 空字符串不复权",
    )
    p.add_argument("--model-path", type=str, required=True, help="Kronos 模型目录或 HF repo id")
    p.add_argument("--tokenizer-path", type=str, required=True, help="Kronos tokenizer 目录或 HF repo id")

    p.add_argument("--window", type=int, default=64, help="输入给模型的历史K线窗口长度（lookback）")
    p.add_argument("--horizon", type=int, default=5, help="预测未来多少个交易日")
    p.add_argument("--seed", type=int, default=40, help="随机种子，保证结果可复现")

    p.add_argument("--temperature", "--temp", dest="temperature", type=float, default=1.0, help="采样温度 T")
    p.add_argument("--top-p", type=float, default=0.9, help="nucleus sampling 概率")
    p.add_argument("--sample-count", type=int, default=1, help="采样次数，多次采样取均值更稳")

    p.add_argument(
        "--output-dir",
        type=str,
        default="predictions",
        help="统一保存预测结果的文件夹，默认 predictions（脚本会自动创建）",
    )
    p.add_argument(
        "--out",
        type=str,
        default=None,
        help="预测结果输出 csv 路径。不填则自动按股票代码+参数+时间戳生成文件名，存入 --output-dir",
    )
    p.add_argument(
        "--chart-out",
        type=str,
        default=None,
        help="预测对比图输出路径。不填则自动按股票代码+参数+时间戳生成文件名，存入 --output-dir",
    )

    p.add_argument("--max-context", type=int, default=512, help="模型支持的最大上下文长度")
    p.add_argument("--device", type=str, default="cpu", help="运行设备，CPU 环境写 cpu 即可")

    p.add_argument("--tune", action="store_true", help="开启自动网格搜索调参模式")
    p.add_argument("--grid-window", type=str, default="64,128,256", help="window 候选值，逗号分隔")
    p.add_argument("--grid-temp", type=str, default="1.0,0.9", help="温度候选值，逗号分隔")
    p.add_argument("--grid-top-p", type=str, default="0.95,0.9", help="top_p 候选值，逗号分隔")
    p.add_argument("--grid-sample-count", type=str, default="1,5", help="sample_count 候选值，逗号分隔")
    p.add_argument("--tune-stride", type=int, default=5, help="滚动回测的步长（每隔多少天评估一次）")
    p.add_argument("--tune-max-windows", type=int, default=120, help="滚动回测最多评估多少个窗口（控制耗时）")
    p.add_argument(
        "--tune-out",
        type=str,
        default=None,
        help="调参结果输出 csv 路径。不填则自动按股票代码+参数+时间戳生成文件名，存入 --output-dir",
    )

    args = p.parse_args()
    if args.data_source == "qlib" and not args.provider_uri:
        p.error("--data-source qlib 模式下必须指定 --provider-uri")
    return args


def main():
    args = parse_args()
    configure_matplotlib_fonts()

    if args.tune:
        run_tune_cli(TuneParams.from_namespace(args))
    else:
        run_single_predict_cli(PredictParams.from_namespace(args))


if __name__ == "__main__":
    main()
