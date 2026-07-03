from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class PredictRequest(BaseModel):
    data_source: Literal["qlib", "akshare", "hkshare", "usstock"] = "akshare"
    provider_uri: Optional[str] = None
    instrument: str
    start: str
    end: str
    future: bool = False
    adjust: Literal["", "qfq", "hfq"] = "qfq"
    model_path: str = "./model"
    tokenizer_path: str = "./tokenizer"
    window: int = Field(default=64, ge=1)
    horizon: int = Field(default=5, ge=1)
    seed: int = 40
    temperature: float = Field(default=1.0, gt=0)
    top_p: float = Field(default=0.9, gt=0, le=1)
    sample_count: int = Field(default=1, ge=1)
    output_dir: str = "predictions"
    max_context: int = Field(default=512, ge=1)
    device: str = "cpu"

    @model_validator(mode="after")
    def validate_qlib(self):
        if self.data_source == "qlib" and not self.provider_uri:
            raise ValueError("provider_uri is required when data_source is qlib")
        return self


class TuneRequest(PredictRequest):
    grid_window: str = "64,128,256"
    grid_temp: str = "1.0,0.9"
    grid_top_p: str = "0.95,0.9"
    grid_sample_count: str = "1,5"
    tune_stride: int = Field(default=5, ge=1)
    tune_max_windows: int = Field(default=120, ge=1)


class JobCreateResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    message: Optional[str] = None
    progress: Optional[float] = None
    error: Optional[str] = None
    result: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
