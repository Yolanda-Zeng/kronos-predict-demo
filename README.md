# Kronos A股K线预测工具 · 使用手册

> 本工具基于 Kronos 金融时间序列模型，支持对 A 股、港美股 日线数据做历史回测和未来走势预测，输出"预测 vs 真实"K线对比图和 csv 结果文件。

---

## 目录结构

```
kronos_demo/
├── kronos_qlib_predict.py    ← 主脚本（本手册描述的就是这个）
├── README.md                  ← 本手册
├── model/                     ← Kronos 模型权重（从 HuggingFace 下载）
├── tokenizer/                 ← Kronos tokenizer（从 HuggingFace 下载）
├── Kronos/                    ← 官方源码仓库（git clone 下来的）
├── qlib_data/                 ← 本地 qlib 历史数据（可选，见下方说明）
├── predictions/               ← 所有输出结果自动存放在这里（脚本自动创建）
└── kronos_env/                ← Python 虚拟环境
```

---

## 快速开始

### 第一步：激活虚拟环境

每次打开终端都要先执行这一步：

```bash
cd ~/kronos_demo
source kronos_env/bin/activate
```

激活成功后，终端最前面会出现 `(kronos_env)` 字样。

### 第二步：跑第一次预测

**模式A：联网获取最新数据（推荐，数据最新）**

> 注意：运行前请确保关闭 Clash 等代理软件的"系统代理"开关（东方财富是国内接口，走代理反而连不上）。

```bash
PYTHONPATH=./Kronos python kronos_qlib_predict.py \
  --data-source akshare \
  --instrument 600519 \
  --start 2024-01-01 \
  --end 2026-06-20 \
  --model-path ./model \
  --tokenizer-path ./tokenizer \
  --window 64 \
  --horizon 5 \
  --seed 40
```

**模式B：使用本地 qlib 历史数据（离线，数据截止 2020-09-25）**

```bash
PYTHONPATH=./Kronos python kronos_qlib_predict.py \
  --data-source qlib \
  --provider-uri ./qlib_data \
  --instrument SH600519 \
  --start 2018-01-01 \
  --end 2020-09-25 \
  --model-path ./model \
  --tokenizer-path ./tokenizer \
  --window 64 \
  --horizon 5 \
  --seed 40
```

运行成功后，预测图和 csv 结果会自动保存到 `predictions/` 文件夹，文件名里带有股票代码和预测日期区间，不会互相覆盖。

---

## 两种预测模式

### 模式一：历史回测模式（默认，不加任何额外参数）

脚本会自动把你给的数据里**最后 `horizon` 天扣留下来**，当作"真实答案"，和模型预测结果对比，在图上画出：

- 🔵 蓝线：历史真实收盘价
- 🔴 红虚线：模型预测收盘价
- 🟢 绿线：真实收盘价（用于与预测对比）

同时在终端输出误差指标（MAE / RMSE / MAPE），数值越小说明预测越准。

**适合用来：** 检验模型在某段历史区间预测得准不准，做参数调优时用这个模式。

```bash
# 示例：用 2024 全年数据做历史回测，扣留最后 5 天对比
PYTHONPATH=./Kronos python kronos_qlib_predict.py \
  --data-source akshare \
  --instrument 600519 \
  --start 2024-01-01 \
  --end 2026-06-20 \   # end 比今天早几天，确保"扣留的5天"都是真实已发生的数据
  --model-path ./model \
  --tokenizer-path ./tokenizer \
  --window 64 \
  --horizon 5 \
  --seed 40
```

---

### 模式二：真实未来预测模式（加 `--future` 参数）

用你给的**全部历史数据**作为输入，预测真正还没发生的未来 `horizon` 天。图上没有绿色对比线（因为未来还没发生，没有真实值可对比）。

**适合用来：** 看模型对接下来几天走势的判断。

```bash
# 示例：预测贵州茅台接下来 5 个交易日的走势
PYTHONPATH=./Kronos python kronos_qlib_predict.py \
  --data-source akshare \
  --instrument 600519 \
  --start 2024-01-01 \
  --end 2026-06-29 \   # end 设成最新的交易日
  --model-path ./model \
  --tokenizer-path ./tokenizer \
  --window 64 \
  --horizon 5 \
  --seed 40 \
  --future
```

---

## 全部参数说明

### 基础参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--data-source` | `qlib` | 数据来源：`qlib`（本地数据）或 `akshare`（联网实时） |
| `--provider-uri` | 无 | qlib 本地数据路径，`--data-source qlib` 时必填 |
| `--instrument` | 必填 | 股票代码。qlib模式用 `SH600519`；akshare模式用 `600519`（纯6位数字） |
| `--start` | 必填 | 历史数据起始日期，格式 `YYYY-MM-DD` |
| `--end` | 必填 | 历史数据结束日期，格式 `YYYY-MM-DD` |
| `--future` | 关闭 | 加上此参数则预测真正的未来（不做历史回测） |
| `--adjust` | `qfq` | akshare模式的复权方式：`qfq`=前复权 / `hfq`=后复权 / 空=不复权 |

### 模型参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--model-path` | 必填 | Kronos 模型权重所在文件夹路径 |
| `--tokenizer-path` | 必填 | Kronos tokenizer 所在文件夹路径 |
| `--device` | `cpu` | 运行设备，CPU 环境保持默认即可 |
| `--max-context` | `512` | 模型支持的最大上下文长度，不建议改动 |

### 预测参数（影响预测效果，可调优）

| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|---------|
| `--window` | `64` | 给模型看多少天历史K线作为输入 | 最关键参数，建议尝试 64/128/256/384 |
| `--horizon` | `5` | 预测未来多少个交易日 | 数字越大越难准，先从 5 开始 |
| `--seed` | `40` | 随机种子，固定后结果可复现 | 对比不同参数时保持不变 |
| `--temperature` | `1.0` | 采样温度，越低结果越保守/稳定 | 可尝试 1.0 / 0.9 / 0.7 |
| `--top-p` | `0.9` | nucleus sampling 概率 | 可尝试 0.95 / 0.9 / 0.8 |
| `--sample-count` | `1` | 采样次数，多次取均值更稳定 | 可尝试 1 / 5 / 10，数值越大越慢 |

### 输出参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--output-dir` | `predictions` | 所有结果文件统一存放的文件夹 |
| `--out` | 自动生成 | 手动指定 csv 输出路径（不填则自动命名） |
| `--chart-out` | 自动生成 | 手动指定图片输出路径（不填则自动命名） |

**自动生成的文件名格式：**

```
predictions/600519_pred20260701-20260707_w64_h5_run20260630-165530_predict.csv
predictions/600519_pred20260701-20260707_w64_h5_run20260630-165530_predict.png
```

文件名里包含：股票代码、预测日期区间（pred）、窗口参数、运行时间，不同次运行不会互相覆盖。

---

## 误差指标解读

历史回测模式下，终端会输出：

```
[INFO] 预测区间误差（与真实值对比）：MAE=0.0639, RMSE=0.0773, MAPE=0.80%
```

| 指标 | 全称 | 含义 | 怎么看 |
|------|------|------|--------|
| MAE | 平均绝对误差 | 预测价格平均偏离真实价格多少元 | 绝对值，受股价大小影响，横向对比不同股票时参考价值有限 |
| RMSE | 均方根误差 | 和MAE类似，但对"偏差特别大的天"惩罚更重 | 通常 ≥ MAE；两者越接近说明每天误差越均匀 |
| MAPE | 平均绝对百分比误差 | 预测价格平均偏离真实价格的百分比 | **最值得看的指标**，不受股价绝对值影响，横向对比最公平 |

> MAPE < 1% 算相当不错；横向对比不同股票/参数组合时，优先看 MAPE 排序。

---

## 自动调参模式（--tune）

如果想系统性地找出**哪组参数在历史上效果最好**，可以开启网格搜索模式。脚本会对所有候选参数组合做滚动回测，自动打印最优参数。

> ⚠️ 这个模式比较耗时（参数组合数 × 回测窗口数），建议在不赶时间时跑（挂着跑一晚上）。

**基础用法：**

```bash
PYTHONPATH=./Kronos python kronos_qlib_predict.py \
  --data-source akshare \
  --instrument 600519 \
  --start 2023-01-01 \
  --end 2026-06-20 \
  --model-path ./model \
  --tokenizer-path ./tokenizer \
  --horizon 5 \
  --seed 40 \
  --tune \
  --grid-window 64,128,256 \
  --grid-temp 1.0,0.9 \
  --grid-top-p 0.95,0.9 \
  --grid-sample-count 1,5 \
  --tune-stride 5 \
  --tune-max-windows 120
```

**调参相关参数说明：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--tune` | 关闭 | 加上此参数开启调参模式 |
| `--grid-window` | `64,128,256` | window 候选值，逗号分隔，会逐一测试 |
| `--grid-temp` | `1.0,0.9` | 采样温度候选值 |
| `--grid-top-p` | `0.95,0.9` | top_p 候选值 |
| `--grid-sample-count` | `1,5` | 采样次数候选值 |
| `--tune-stride` | `5` | 滚动回测步长（每隔多少天评估一次），越小越准但越慢 |
| `--tune-max-windows` | `120` | 每组参数最多评估多少个窗口（控制总耗时） |
| `--tune-out` | 自动生成 | 调参结果 csv 路径 |

**跑完后你会看到：**

```
[BEST] 最优参数组合（按 RMSE 排序）：
  window=128, T=0.9, top_p=0.95, sample_count=5
  MAE=0.0412, RMSE=0.0531, MAPE=0.62%
```

把最优参数填入普通预测命令，再跑一次正式预测即可：

```bash
PYTHONPATH=./Kronos python kronos_qlib_predict.py \
  --data-source akshare \
  --instrument 600519 \
  --start 2024-01-01 \
  --end 2026-06-29 \
  --model-path ./model \
  --tokenizer-path ./tokenizer \
  --window 128 \         # ← 换成最优参数
  --horizon 5 \
  --temperature 0.9 \   # ← 换成最优参数
  --top-p 0.95 \        # ← 换成最优参数
  --sample-count 5 \    # ← 换成最优参数
  --seed 40 \
  --future
```

---

## 支持的市场和股票

### A股（--data-source akshare）

理论上支持所有 A 股上市公司，`--instrument` 填 6 位数字股票代码（不带 SH/SZ 前缀）：

```
沪市（6开头）：600519（茅台）、600036（招商银行）、600276（恒瑞医药）...
深市（0/3开头）：000858（五粮液）、000333（美的）、300750（宁德时代）...
```

> 注意：运行前请关闭系统代理（东方财富是国内接口，走代理反而会报错）

**示例命令：**
```bash
PYTHONPATH=./Kronos python kronos_qlib_predict.py \
  --data-source akshare \
  --instrument 600519 \
  --start 2024-01-01 --end 2026-06-20 \
  --model-path ./model --tokenizer-path ./tokenizer \
  --window 64 --horizon 5 --seed 40
```

---

### 港股（--data-source hkshare）

通过东方财富接口获取，`--instrument` 填 5 位数字港股代码（不带 HK 前缀）：

```
00700  腾讯控股
09988  阿里巴巴（港股）
00941  中国移动
03690  美团
01810  小米集团
02318  中国平安
00005  汇丰控股
```

> 注意：同样需要关闭系统代理（东方财富港股接口也是走国内线路）

**示例命令：**
```bash
PYTHONPATH=./Kronos python kronos_qlib_predict.py \
  --data-source hkshare \
  --instrument 00700 \
  --start 2024-01-01 --end 2026-06-20 \
  --model-path ./model --tokenizer-path ./tokenizer \
  --window 64 --horizon 5 --seed 40
```

---

### 美股（--data-source usstock）

通过 yfinance 获取，`--instrument` 填美股 ticker（大小写均可）：

```
AAPL   苹果
TSLA   特斯拉
MSFT   微软
GOOGL  谷歌
AMZN   亚马逊
NVDA   英伟达
META   Meta（Facebook）
QQQ    纳斯达克100 ETF
SPY    标普500 ETF
```

> 注意：yfinance 需要访问 Yahoo Finance（境外网站），这个模式**需要开 VPN**

**先安装依赖：**
```bash
pip install yfinance
```

**示例命令：**
```bash
PYTHONPATH=./Kronos python kronos_qlib_predict.py \
  --data-source usstock \
  --instrument AAPL \
  --start 2024-01-01 --end 2026-06-20 \
  --model-path ./model --tokenizer-path ./tokenizer \
  --window 64 --horizon 5 --seed 40
```

---

### qlib 本地数据（--data-source qlib）

数据截止 2020-09-25，已验证可用的股票：

| 代码 | 公司 | 数据起始 |
|------|------|---------|
| SH600519 | 贵州茅台 | 2001-08-27 |
| SH600036 | 招商银行 | 2002-04-09 |
| SH600276 | 恒瑞医药 | 2000-10-18 |
| SH600900 | 长江电力 | 2003-11-18 |
| SH601318 | 中国平安 | 2007-03-01 |
| SH601888 | 中国中免 | 2009-10-15 |
| SZ000333 | 美的集团 | 2013-09-18 |
| SZ000858 | 五粮液   | 1999-11-10 |

查询某只股票是否在本地数据里：
```bash
grep "600519" qlib_data/instruments/all.txt
```

---

## 常见问题 / 报错处理

### 问题1：akshare / hkshare 模式报 ProxyError / RemoteDisconnected

东方财富是国内接口（A股和港股都走这个），走代理反而会失败。解决方法：

```bash
# 临时关掉系统代理
networksetup -setwebproxystate "Wi-Fi" off
networksetup -setsecurewebproxystate "Wi-Fi" off

# 用完想恢复
networksetup -setwebproxystate "Wi-Fi" on
networksetup -setsecurewebproxystate "Wi-Fi" on
```

或者在 Clash 等代理软件的规则里，把 `eastmoney.com` 加入直连(DIRECT)名单。

### 问题1b：usstock 模式连不上 / 超时

Yahoo Finance 是境外网站，美股模式**需要开 VPN** 才能访问。如果 VPN 已开但还是超时，检查 VPN 是否正常工作（可以先在浏览器里打开 `https://finance.yahoo.com` 验证）。

### 问题2：ModuleNotFoundError: No module named 'einops'（或其他模块）

缺少 Kronos 依赖库，一次性装齐：

```bash
pip install -r Kronos/requirements.txt
```

### 问题3：PYTHONPATH 忘了加，报 No module named 'model'

命令最前面必须加 `PYTHONPATH=./Kronos`，缺了这个 Python 找不到 Kronos 的源码：

```bash
PYTHONPATH=./Kronos python kronos_qlib_predict.py ...
```

### 问题4：RuntimeError: 没有取到数据

- **akshare 模式**：检查股票代码格式（6位纯数字，不带SH/SZ），以及网络/代理状态
- **qlib 模式**：检查 `--instrument` 是否带了 SH/SZ 前缀（qlib 需要），以及 `--start/--end` 是否在数据覆盖范围内（截止 2020-09-25）

### 问题5：预测很慢

- CPU 推理本身就比 GPU 慢，`window=64, sample_count=1` 是最快的参数组合
- 不要把 `--window` 和 `--sample-count` 都调很大，会成倍增加时间
- 第一次运行还需要把模型加载进内存，会比后续跑更慢一些，属正常现象

### 问题6：图上三条线没有衔接

是正常现象，蓝线（历史）和红/绿线（预测/真实）是分开画的，视觉上有个小跳跃。如果很在意外观，可以联系开发者修改画图逻辑。

---

## 调参最佳实践（按优先级）

1. **先固定 `--seed`，建立 baseline**：用默认参数跑通一次，记录 MAPE 作为基准线
2. **优先调 `--window`**：这是对结果影响最大的参数，建议网格 `64,128,256,384`
3. **在最优 window 上调采样参数**：`--temperature` / `--top-p` / `--sample-count`
4. **不同股票单独调参**：A 股不同标的波动结构差异大，最好每只股票单独找最优参数，不要用一套参数通吃所有标的
5. **对比多只股票时用 MAPE 排序**：不受股价绝对值影响，最公平

---

*文档版本：v1.0 · 2026年6月*
