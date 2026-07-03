from __future__ import annotations

import threading
import traceback
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class JobStatus(str, Enum):
    QUEUED = "queued"
    LOADING_MODEL = "loading_model"
    FETCHING_DATA = "fetching_data"
    PREDICTING = "predicting"
    DONE = "done"
    FAILED = "failed"


@dataclass
class JobRecord:
    job_id: str
    job_type: str
    status: JobStatus = JobStatus.QUEUED
    message: str = "任务已排队"
    progress: float = 0.0
    error: Optional[str] = None
    result: Optional[dict[str, Any]] = None
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._lock = threading.Lock()

    def create(self, job_type: str) -> JobRecord:
        job_id = uuid.uuid4().hex
        record = JobRecord(job_id=job_id, job_type=job_type)
        with self._lock:
            self._jobs[job_id] = record
        return record

    def get(self, job_id: str) -> Optional[JobRecord]:
        with self._lock:
            return self._jobs.get(job_id)

    def update(
        self,
        job_id: str,
        *,
        status: Optional[JobStatus] = None,
        message: Optional[str] = None,
        progress: Optional[float] = None,
        error: Optional[str] = None,
        result: Optional[dict[str, Any]] = None,
    ) -> None:
        record = self.get(job_id)
        if not record:
            return
        with record.lock:
            if status is not None:
                record.status = status
            if message is not None:
                record.message = message
            if progress is not None:
                record.progress = progress
            if error is not None:
                record.error = error
            if result is not None:
                record.result = result

    def to_response(self, record: JobRecord) -> dict[str, Any]:
        with record.lock:
            payload = {
                "job_id": record.job_id,
                "status": record.status.value,
                "message": record.message,
                "progress": record.progress,
                "error": record.error,
                "result": record.result,
            }
        return payload


def run_job_in_background(store: JobStore, record: JobRecord, worker: Callable[[Callable], Any]) -> None:
    def progress_callback(message: str, progress: Optional[float] = None) -> None:
        status = JobStatus.PREDICTING
        lower = message.lower()
        if "行情" in message or "fetch" in lower:
            status = JobStatus.FETCHING_DATA
        elif "模型" in message or "load" in lower:
            status = JobStatus.LOADING_MODEL
        elif "完成" in message or progress == 1.0:
            status = JobStatus.PREDICTING

        store.update(
            record.job_id,
            status=status,
            message=message,
            progress=progress if progress is not None else record.progress,
        )

    def _run() -> None:
        store.update(record.job_id, status=JobStatus.QUEUED, message="任务开始执行", progress=0.01)
        try:
            result = worker(progress_callback)
            store.update(
                record.job_id,
                status=JobStatus.DONE,
                message="完成",
                progress=1.0,
                result=result,
            )
        except Exception as exc:
            store.update(
                record.job_id,
                status=JobStatus.FAILED,
                message="任务失败",
                error=str(exc),
                progress=1.0,
            )
            traceback.print_exc()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
