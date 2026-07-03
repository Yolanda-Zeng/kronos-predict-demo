## Why

Web 预测工作台已跑通，但**调参 Tab 仍是「裸字段名 + 逗号分隔值」**，用户很难理解每个 grid 参数的含义、合理取值范围，以及出问题时该怎么排查；**预测 Tab 的 MAE/RMSE/MAPE 卡片也只显示数字、没有释义**。README 里虽有调参最佳实践和指标解读，却与界面脱节。现在正是把「文档里的经验」嵌进 UI 的时机，降低调参门槛、让用户看得懂预测结果。

## What Changes

- 调参 Tab 增加**参数说明面板**：每个 grid 字段附带中文释义、推荐范围、对结果/耗时的影响。
- 增加**调参调试指南**：折叠式「怎么调 / 怎么读结果 / 常见坑」 playbook（对齐 README 最佳实践）。
- 增加**预设方案**：快速试跑 / 标准 / 精细三档，一键填充 grid 与 stride 参数。
- 启动调参前展示**组合数与预估耗时**提示，避免误触大规模网格。
- 结果区增强：按 MAPE 排序说明、最优行高亮、中文列头。
- **预测指标释义**：Predict Tab 的 MAE / RMSE / MAPE 卡片增加中文全称、一句话说明、参考解读（对齐 README）；Tune 结果表列头附带同样释义。
- **Phase 2（同 change 内可选）**：预测 Tab 高级参数复用同一套说明组件；调参结果 CSV 下载。

## Capabilities

### New Capabilities

- `tune-param-guidance`: 调参参数释义、调试 playbook、预设方案、组合数/耗时提示、结果解读增强。
- `metric-glossary`: MAE / RMSE / MAPE 指标释义，用于 Predict 指标卡片与 Tune 结果表。

### Modified Capabilities

- `prediction-web-ui`: 扩展 Tune Tab 与 Predict Tab 的参数引导行为；指标卡片展示释义。

## Impact

- **前端**：`TunePage.tsx`、`MetricCards.tsx`、新增 `paramHelp.ts`（含 `metricHelp`）/ `ParamHelpField.tsx` / `MetricHelpCard.tsx` / `TuneGuidePanel.tsx`，可选扩展 `ParamForm.tsx`。
- **后端**：无必须变更（组合数可在前端纯计算）；Phase 2 调参 CSV 下载可复用现有 `/api/files/download`。
- **文档**：README 调参章节可与 UI 文案保持同源（从 `paramHelp.ts` 或共享 markdown 引用）。

## 项目还可完善的方向（本 change 外，供 roadmap 参考）

| 优先级 | 方向 | 理由 |
|--------|------|------|
| 高 | 预测/调参 **Job 取消** | 长跑任务无法中断，体验差 |
| 高 | 历史 Tab **完整图表回放** | 目前历史记录缺少 history/actual 完整曲线 |
| 中 | **GPU 设备**状态与切换提示 | 用户不知是否在 CPU 上慢速推理 |
| 中 | 多股票 **批量预测** | 单票操作效率低 |
| 低 | Docker 一键包齐 Kronos 依赖 | 降低环境踩坑 |
| 低 | 调参/预测 **结果对比** | 两次 run 并排看 MAPE 变化 |

本 change 聚焦「调参可理解、可调试」与「预测指标可读」；上表高优先级项建议作为后续独立 change。
