export interface PredictFormValues {
  data_source: "qlib" | "akshare" | "hkshare" | "usstock";
  provider_uri?: string;
  instrument: string;
  start: string;
  end: string;
  future: boolean;
  adjust: "" | "qfq" | "hfq";
  model_path: string;
  tokenizer_path: string;
  window: number;
  horizon: number;
  seed: number;
  temperature: number;
  top_p: number;
  sample_count: number;
  device: string;
}

export interface ChartSeries {
  timestamps: string[];
  close: number[];
}

export interface ChartData {
  history: ChartSeries;
  predicted: ChartSeries;
  actual?: ChartSeries | null;
  bridge: { timestamp: string; close: number };
}

export interface Metrics {
  mae: number;
  rmse: number;
  mape: number;
}

export interface PredictResult {
  instrument: string;
  mode: string;
  csv_path: string;
  chart_path: string;
  metrics?: Metrics | null;
  predictions: Record<string, unknown>[];
  chart: ChartData;
  pred_start: string;
  pred_end: string;
}

export interface JobStatus {
  job_id: string;
  status: string;
  message?: string;
  progress?: number;
  error?: string;
  result?: PredictResult | TuneJobResult;
}

export interface TuneJobResult {
  csv_path: string;
  results: TuneRow[];
  best: TuneRow;
}

export interface TuneRow {
  window: number;
  T: number;
  top_p: number;
  sample_count: number;
  mae: number;
  rmse: number;
  mape: number;
  n_eval_windows: number;
}

export interface HistoryItem {
  id: string;
  instrument: string;
  pred_start: string;
  pred_end: string;
  window: number;
  horizon: number;
  run_timestamp: string;
  csv_path: string;
  png_path?: string | null;
  metrics?: Metrics | null;
  mode?: string;
  chart_complete?: boolean;
  chart?: ChartData | Partial<ChartData> | null;
}

export const defaultPredictForm: PredictFormValues = {
  data_source: "akshare",
  provider_uri: "./qlib_data",
  instrument: "600519",
  start: "2024-01-01",
  end: "2025-06-01",
  future: false,
  adjust: "qfq",
  model_path: "./model",
  tokenizer_path: "./tokenizer",
  window: 64,
  horizon: 5,
  seed: 40,
  temperature: 1.0,
  top_p: 0.9,
  sample_count: 1,
  device: "cpu",
};

export const dataSourceHints: Record<PredictFormValues["data_source"], string> = {
  qlib: "本地 qlib 数据，需填写 provider_uri，数据截止约 2020 年。",
  akshare: "A 股东方财富接口，请关闭系统代理（Clash 等）以避免连接失败。",
  hkshare: "港股东方财富接口，同样需要直连国内网络。",
  usstock: "美股 yfinance 接口，需要 VPN 访问 Yahoo Finance。",
};
