export interface ParamHelpEntry {
  label: string;
  summary: string;
  range?: string;
  impact?: string;
  debugTip?: string;
}

export interface PlaybookSection {
  title: string;
  steps: string[];
}

export interface TunePreset {
  id: "quick" | "standard" | "thorough";
  name: string;
  description: string;
  grid_window: string;
  grid_temp: string;
  grid_top_p: string;
  grid_sample_count: string;
  tune_stride: number;
  tune_max_windows: number;
}

export interface MetricHelpEntry {
  key: "mae" | "rmse" | "mape";
  abbrev: string;
  fullName: string;
  summary: string;
  interpretation: string;
  tip: string;
  recommended?: boolean;
}

export interface TuneWorkloadEstimate {
  comboCount: number;
  evalWindows: number;
  minutesLow: number;
  minutesHigh: number;
  label: string;
}

export const tuneParamHelp: Record<string, ParamHelpEntry> = {
  grid_window: {
    label: "窗口 grid_window",
    summary: "历史 K 线窗口长度候选，逗号分隔，会逐一测试。",
    range: "常见：64,128,256,384",
    impact: "对结果影响最大，建议优先调此参数。",
    debugTip: "若 MAPE 对 window 不敏感，可缩小候选范围节省耗时。",
  },
  grid_temp: {
    label: "温度 grid_temp",
    summary: "采样温度候选，越高随机性越强。",
    range: "常见：1.0,0.9,0.7",
    impact: "在确定最优 window 后再调，通常 0.7–1.0。",
    debugTip: "温度过高可能导致预测曲线抖动，可尝试降低 temperature。",
  },
  grid_top_p: {
    label: "Top-p grid_top_p",
    summary: "核采样截断概率，控制采样多样性。",
    range: "常见：0.95,0.9,0.8",
    impact: "与 temperature 配合，影响预测平滑度。",
    debugTip: "若预测过于保守，可略提高 top_p。",
  },
  grid_sample_count: {
    label: "采样次数 grid_sample_count",
    summary: "每个窗口的 Monte Carlo 采样次数，取平均作为预测。",
    range: "常见：1,5,10",
    impact: ">1 更稳定但更慢，通常 5 是性价比平衡点。",
    debugTip: "sample_count=1 波动大时，优先加到 5 再比较 MAPE。",
  },
  tune_stride: {
    label: "步长 tune_stride",
    summary: "滚动回测每隔多少天评估一次。",
    range: "3–10，越小越准但越慢",
    impact: "直接控制每组参数的评估窗口数量。",
    debugTip: "试跑时可设 10，正式调参用 5 或 3。",
  },
  tune_max_windows: {
    label: "最大窗口数 tune_max_windows",
    summary: "每组参数最多评估多少个滚动窗口，用于控制总耗时。",
    range: "试跑 30，标准 120，精细 200",
    impact: "与 stride 共同决定每组参数的实际评估量。",
    debugTip: "结果不稳定时增大 max_windows，而非盲目扩大 grid。",
  },
};

export const predictParamHelp: Record<string, ParamHelpEntry> = {
  window: {
    label: "窗口 window",
    summary: "模型看多少根历史 K 线再做预测。",
    range: "64–384，建议用调参结果",
    impact: "影响最大的超参数，不同股票最优值差异大。",
    debugTip: "先用调参 Tab 找最优 window，再固定其他参数。",
  },
  horizon: {
    label: "预测天数 horizon",
    summary: "向前预测多少个交易日。",
    range: "通常 1–10",
    impact: "越大越难，误差通常随 horizon 增大。",
    debugTip: "回测模式会扣留最后 horizon 天与真实值对比。",
  },
  seed: {
    label: "随机种子 seed",
    summary: "固定随机性，便于复现同一预测结果。",
    range: "任意整数",
    impact: "调参时建议固定 seed，对比才有意义。",
    debugTip: "对比不同参数时保持 seed 不变。",
  },
  temperature: {
    label: "温度 temperature",
    summary: "采样温度，越高预测越随机。",
    range: "0.5–1.2",
    impact: "影响预测曲线形态与稳定性。",
    debugTip: "正式预测建议使用调参得到的最优值。",
  },
  top_p: {
    label: "Top-p top_p",
    summary: "核采样概率截断，与 temperature 配合。",
    range: "0.8–0.99",
    impact: "过低可能使预测过于平滑。",
    debugTip: "与 grid 调参结果保持一致。",
  },
  sample_count: {
    label: "采样次数 sample_count",
    summary: "多次采样取平均，降低单次随机波动。",
    range: "1, 5, 10",
    impact: ">1 更稳定，推理更慢。",
    debugTip: "展示用可设 1，正式评估建议 ≥5。",
  },
  device: {
    label: "设备 device",
    summary: "推理设备：cpu / cuda / mps。",
    range: "Mac 可用 mps，NVIDIA 用 cuda",
    impact: "仅影响速度，不影响数值结果（同 seed）。",
    debugTip: "GPU 不可用时回退 cpu。",
  },
};

export const tunePlaybook: PlaybookSection[] = [
  {
    title: "推荐调参顺序",
    steps: [
      "固定 seed，用默认参数跑通一次，记录 MAPE 作为 baseline",
      "优先 grid_window：64,128,256,384",
      "在最优 window 上再调 temperature / top_p / sample_count",
      "不同股票单独调参，不要一套参数通吃",
    ],
  },
  {
    title: "怎么看 MAPE / RMSE",
    steps: [
      "MAPE 越小越好，横向对比股票或参数组合时优先看 MAPE",
      "MAPE < 1% 算相当不错",
      "RMSE 通常 ≥ MAE；两者越接近说明每天误差越均匀",
      "最优行按 RMSE 最小标记，与 CLI 排序一致",
    ],
  },
  {
    title: "常见失败排查",
    steps: [
      "数据拉取失败：A 股请关闭 Clash 等系统代理",
      "任务极慢：减小 grid 组合数或增大 tune_stride、减小 tune_max_windows",
      "MAPE 异常高：检查日期区间是否足够长、window 是否过大",
      "结果波动大：提高 sample_count 或固定 seed 后重跑",
    ],
  },
];

export const tunePresets: TunePreset[] = [
  {
    id: "quick",
    name: "快速试跑",
    description: "小 grid + 大步长，约几分钟内看趋势",
    grid_window: "64,128",
    grid_temp: "1.0",
    grid_top_p: "0.9",
    grid_sample_count: "1",
    tune_stride: 10,
    tune_max_windows: 30,
  },
  {
    id: "standard",
    name: "标准",
    description: "与 CLI 默认 grid 一致，平衡耗时与覆盖",
    grid_window: "64,128,256",
    grid_temp: "1.0,0.9",
    grid_top_p: "0.95,0.9",
    grid_sample_count: "1,5",
    tune_stride: 5,
    tune_max_windows: 120,
  },
  {
    id: "thorough",
    name: "精细",
    description: "大 grid + 小步长，适合最终定参",
    grid_window: "64,128,256,384",
    grid_temp: "1.0,0.9,0.7",
    grid_top_p: "0.95,0.9,0.8",
    grid_sample_count: "1,5,10",
    tune_stride: 3,
    tune_max_windows: 200,
  },
];

export const metricHelp: Record<"mae" | "rmse" | "mape", MetricHelpEntry> = {
  mae: {
    key: "mae",
    abbrev: "MAE",
    fullName: "平均绝对误差",
    summary: "预测收盘价平均偏离真实值多少元",
    interpretation: "绝对值，受股价大小影响",
    tip: "横向对比不同股票时参考价值有限，建议配合 MAPE 一起看。",
  },
  rmse: {
    key: "rmse",
    abbrev: "RMSE",
    fullName: "均方根误差",
    summary: "类似 MAE，但对偏差特别大的天惩罚更重",
    interpretation: "通常 ≥ MAE",
    tip: "两者越接近说明每天误差越均匀；调参最优行按 RMSE 最小排序。",
  },
  mape: {
    key: "mape",
    abbrev: "MAPE",
    fullName: "平均绝对百分比误差",
    summary: "预测平均偏离真实价格的百分比",
    interpretation: "横向对比首选",
    tip: "MAPE < 1% 算相当不错；对比不同股票或参数组合时优先看 MAPE 排序。",
    recommended: true,
  },
};

export const metricHelpList: MetricHelpEntry[] = [metricHelp.mae, metricHelp.rmse, metricHelp.mape];

function parseGridValues(raw: string): number[] {
  return raw
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)
    .map(Number)
    .filter((n) => !Number.isNaN(n));
}

export function estimateTuneWorkload(input: {
  grid_window: string;
  grid_temp: string;
  grid_top_p: string;
  grid_sample_count: string;
  tune_max_windows: number;
}): TuneWorkloadEstimate {
  const counts = [
    parseGridValues(input.grid_window).length,
    parseGridValues(input.grid_temp).length,
    parseGridValues(input.grid_top_p).length,
    parseGridValues(input.grid_sample_count).length,
  ];
  const comboCount = counts.reduce((acc, n) => acc * Math.max(n, 0), 1) || 0;
  const evalWindows = comboCount * Math.max(input.tune_max_windows, 0);
  const secondsLow = evalWindows * 1.5;
  const secondsHigh = evalWindows * 4;
  const minutesLow = Math.max(1, Math.ceil(secondsLow / 60));
  const minutesHigh = Math.max(minutesLow, Math.ceil(secondsHigh / 60));

  const label =
    comboCount === 0
      ? "请检查 grid 参数格式（逗号分隔数字）"
      : `约 ${comboCount} 组参数 × ${input.tune_max_windows} 窗口 ≈ ${evalWindows} 次评估 · 预计 ${minutesLow}–${minutesHigh} 分钟（仅供参考，CPU 环境）`;

  return { comboCount, evalWindows, minutesLow, minutesHigh, label };
}
