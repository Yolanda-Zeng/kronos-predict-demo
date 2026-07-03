## Context

当前 future 分支（`predict.py` L56-69）：

```python
y_timestamp = make_future_timestamps(df["timestamps"].iloc[-1], params.horizon)
pred_len = params.horizon
```

`make_future_timestamps` 固定 `periods=horizon`，与表单 `end` 无关。

用户场景：today=7/3，end=7/10，future 模式 → 期望预测 7/4~7/10 共 ~5 个交易日；若 horizon=5 且 last=7/3 其实已接近，但若 horizon=3 则只到 7/8。更关键的是用户**以为改 end 就能延长预测**，而系统完全忽略 end。

若用户留在回测模式，end=7/10 只影响拉数上界，最后一根 bar 仍是 7/3，预测对比段也止于 7/3——这与用户期望完全不符。

## Goals / Non-Goals

**Goals:**
- future 模式 + `end > last_kline`：预测至 `end`（含该日若为交易日）。
- UI 让用户理解：历史线止于最新 K 线，红色预测线可延伸到 `end`。
- 保持 backtest 模式行为不变。

**Non-Goals:**
- 不伪造 7/4~7/10 的「真实」绿色对比线。
- 不改变行情 API 能拉到的历史数据范围（仍 ≤ 最新交易日）。

## Decisions

### 1. 预测时间轴生成

```python
def make_future_timestamps_until(last_ts, end_ts, *, max_periods=60):
    start = pd.Timestamp(last_ts).normalize() + pd.Timedelta(days=1)
    end = pd.Timestamp(end_ts).normalize()
    if end <= pd.Timestamp(last_ts).normalize():
        return pd.Series(dtype="datetime64[ns]")  # empty → caller uses horizon fallback
    future = pd.bdate_range(start=start, end=end, freq="B")
    if len(future) > max_periods:
        future = future[:max_periods]
        log warn
    return pd.Series(future)
```

**future 模式分支：**

```
y_ts = make_future_timestamps_until(last, params.end)
if len(y_ts) == 0:
    y_ts = make_future_timestamps(last, params.horizon)
pred_len = len(y_ts)
```

`pred_len` 传入 `predictor.predict(..., pred_len=pred_len)`，不再硬编码 `params.horizon`。

### 2. horizon 在未来模式的角色

| 条件 | 预测长度 |
|------|----------|
| future 且 end > last_kline | end 内交易日数（ capped ） |
| future 且 end ≤ last_kline | horizon（与现行为同） |
| backtest | 不变 |

UI 文案：「未来模式下，若结束日晚于最新 K 线，预测延伸至该日；否则按 horizon 天数预测。」

### 3. Web UI

- 未来模式：结束日期 label → `预测至日期`
- 辅助说明：`历史 K 线最多到最新交易日；预测区间可延伸至所选日期`
- （可选 Phase 1）静态说明即可；Phase 2 可接 API 预检 last_kline

### 4. 验证用例

- last=2026-07-03 (Fri), end=2026-07-10 → y_ts 末条为 2026-07-10
- last=2026-07-03, end=2026-07-03 → fallback horizon=5
- backtest 不受影响

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| pred_len 很大导致推理慢 | max_periods=60 + UI 提示 |
| end 填过去日期 | fallback horizon + 日志 |
| 与 CLI 文档「horizon=预测天数」冲突 | README 补充 future+end 优先级 |

## Migration Plan

1. 实现 `make_future_timestamps_until` + predict 分支
2. 单测
3. 更新 ParamForm 标签与 hint
4. 手动：future + end=7/10 验证 pred_end 与图表

## Open Questions

1. max_periods 默认 60 是否足够？（先 60，与 window 量级相当）
