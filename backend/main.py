from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
KRONOS_DIR = ROOT / "Kronos"
if str(KRONOS_DIR) not in sys.path:
    sys.path.insert(0, str(KRONOS_DIR))

from backend.jobs import JobStore, run_job_in_background
from backend.schemas import HealthResponse, JobCreateResponse, JobStatusResponse, PredictRequest, TuneRequest
from kronos_core.chart import configure_matplotlib_fonts
from kronos_core.history import list_predictions
from kronos_core.params import PredictParams, TuneParams
from kronos_core.predict import execute_predict
from kronos_core.predictor import is_model_loaded
from kronos_core.tune import execute_tune

configure_matplotlib_fonts()

app = FastAPI(title="Kronos Prediction API", version="1.0.0")
job_store = JobStore()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _predict_params(req: PredictRequest) -> PredictParams:
    return PredictParams(**req.model_dump())


def _tune_params(req: TuneRequest) -> TuneParams:
    return TuneParams(**req.model_dump())


def _predict_result_payload(result) -> dict:
    return {
        "instrument": result.instrument,
        "mode": result.mode,
        "csv_path": result.csv_path,
        "chart_path": result.chart_path,
        "metrics": result.metrics,
        "predictions": result.predictions,
        "chart": result.chart,
        "pred_start": result.pred_start,
        "pred_end": result.pred_end,
    }


@app.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", model_loaded=is_model_loaded())


@app.post("/api/jobs/predict", response_model=JobCreateResponse, status_code=202)
def create_predict_job(req: PredictRequest):
    record = job_store.create("predict")
    params = _predict_params(req)

    def worker(progress):
        result = execute_predict(params, use_shared_predictor=True, on_progress=progress)
        return _predict_result_payload(result)

    run_job_in_background(job_store, record, worker)
    return JobCreateResponse(job_id=record.job_id, status=record.status.value)


@app.post("/api/jobs/tune", response_model=JobCreateResponse, status_code=202)
def create_tune_job(req: TuneRequest):
    record = job_store.create("tune")
    params = _tune_params(req)

    def worker(progress):
        result = execute_tune(params, use_shared_predictor=True, on_progress=progress)
        return {
            "csv_path": result.csv_path,
            "results": result.results,
            "best": result.best,
        }

    run_job_in_background(job_store, record, worker)
    return JobCreateResponse(job_id=record.job_id, status=record.status.value)


@app.get("/api/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str):
    record = job_store.get(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(**job_store.to_response(record))


@app.get("/api/predictions")
def get_predictions(output_dir: str = "predictions"):
    return {"items": list_predictions(output_dir)}


def _resolve_safe_path(path: str) -> Path:
    abs_path = Path(path).resolve()
    predictions_root = (ROOT / "predictions").resolve()
    if predictions_root not in abs_path.parents and abs_path != predictions_root:
        raise HTTPException(status_code=403, detail="Access denied")
    if not abs_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return abs_path


@app.get("/api/files/download")
def download_file(path: str):
    file_path = _resolve_safe_path(path)
    media = "text/csv" if file_path.suffix == ".csv" else "application/octet-stream"
    return FileResponse(file_path, media_type=media, filename=file_path.name)


FRONTEND_DIST = ROOT / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
