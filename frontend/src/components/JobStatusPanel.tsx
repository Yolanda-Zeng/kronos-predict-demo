interface Props {
  status?: string;
  message?: string;
  progress?: number;
  error?: string;
}

function statusBadgeClass(status?: string): string {
  switch (status) {
    case "queued":
      return "badge-queued";
    case "running":
      return "badge-running";
    case "done":
      return "badge-done";
    case "failed":
      return "badge-failed";
    default:
      return "badge-queued";
  }
}

function statusLabel(status?: string): string {
  switch (status) {
    case "queued":
      return "排队中";
    case "running":
      return "运行中";
    case "done":
      return "已完成";
    case "failed":
      return "失败";
    default:
      return status ?? "未知";
  }
}

export default function JobStatusPanel({ status, message, progress, error }: Props) {
  if (!status) return null;

  return (
    <div className={`card ${error ? "border-danger/30" : "border-accent/20"}`}>
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium">任务状态</p>
          <p className="text-xs text-muted">{message ?? statusLabel(status)}</p>
        </div>
        <span className={statusBadgeClass(status)}>{statusLabel(status)}</span>
      </div>
      {typeof progress === "number" && status !== "done" && status !== "failed" && (
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs text-muted">
            <span>进度</span>
            <span className="numeric">{Math.round(progress * 100)}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-elevated">
            <div
              className="h-full rounded-full bg-gradient-to-r from-accent to-accent-hover transition-all duration-300"
              style={{ width: `${Math.round(progress * 100)}%` }}
            />
          </div>
        </div>
      )}
      {error && (
        <p className="mt-3 rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p>
      )}
    </div>
  );
}
