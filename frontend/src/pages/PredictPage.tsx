import { useEffect, useRef, useState } from "react";
import { createPredictJob, getJob } from "../api/client";
import ChartPanel from "../components/ChartPanel";
import JobStatusPanel from "../components/JobStatusPanel";
import MetricCards from "../components/MetricCards";
import ParamForm from "../components/ParamForm";
import ResultPanel from "../components/ResultPanel";
import type { PredictFormValues, PredictResult } from "../types";

interface Props {
  form: PredictFormValues;
  setForm: (value: PredictFormValues) => void;
  result: PredictResult | null;
  setResult: (value: PredictResult | null) => void;
}

export default function PredictPage({ form, setForm, result, setResult }: Props) {
  const [status, setStatus] = useState<string>();
  const [message, setMessage] = useState<string>();
  const [progress, setProgress] = useState<number>();
  const [error, setError] = useState<string>();
  const [submitting, setSubmitting] = useState(false);
  const pollRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, []);

  const pollJob = (id: string) => {
    if (pollRef.current) window.clearInterval(pollRef.current);
    pollRef.current = window.setInterval(async () => {
      try {
        const job = await getJob(id);
        setStatus(job.status);
        setMessage(job.message);
        setProgress(job.progress);
        setError(job.error);

        if (job.status === "done" && job.result) {
          setResult(job.result as PredictResult);
          setSubmitting(false);
          if (pollRef.current) window.clearInterval(pollRef.current);
        }
        if (job.status === "failed") {
          setSubmitting(false);
          if (pollRef.current) window.clearInterval(pollRef.current);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
        setSubmitting(false);
        if (pollRef.current) window.clearInterval(pollRef.current);
      }
    }, 1200);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(undefined);
    setResult(null);
    try {
      const { job_id } = await createPredictJob(form);
      setStatus("queued");
      setMessage("任务已提交");
      setProgress(0);
      pollJob(job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setSubmitting(false);
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[360px,1fr]">
      <ParamForm form={form} setForm={setForm} onSubmit={handleSubmit} submitting={submitting} />
      <div className="space-y-4">
        <JobStatusPanel status={status} message={message} progress={progress} error={error} />
        <ChartPanel
          chart={result?.chart}
          instrument={result?.instrument ?? form.instrument}
          mode={result?.mode ?? (form.future ? "future" : "backtest")}
          predStart={result?.pred_start}
          predEnd={result?.pred_end}
        />
        <MetricCards metrics={result?.metrics} showBacktestNote={!!result?.metrics && !form.future} />
        {result && (
          <ResultPanel
            result={{
              ...result,
              predictions: result.predictions.length
                ? result.predictions
                : result.chart.predicted.timestamps.map((ts, idx) => ({
                    timestamps: ts,
                    close: result.chart.predicted.close[idx],
                  })),
            }}
          />
        )}
      </div>
    </div>
  );
}
