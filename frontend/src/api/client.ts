import type { HistoryItem, JobStatus, PredictFormValues, TuneRow } from "../types";

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export function createPredictJob(body: PredictFormValues) {
  return request<{ job_id: string; status: string }>("/api/jobs/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export interface TuneRequestBody extends PredictFormValues {
  grid_window: string;
  grid_temp: string;
  grid_top_p: string;
  grid_sample_count: string;
  tune_stride: number;
  tune_max_windows: number;
}

export function createTuneJob(body: TuneRequestBody) {
  return request<{ job_id: string; status: string }>("/api/jobs/tune", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function getJob(jobId: string) {
  return request<JobStatus>(`/api/jobs/${jobId}`);
}

export function listPredictions() {
  return request<{ items: HistoryItem[] }>("/api/predictions");
}

export function downloadUrl(path: string) {
  return `/api/files/download?path=${encodeURIComponent(path)}`;
}

export type { TuneRow };
