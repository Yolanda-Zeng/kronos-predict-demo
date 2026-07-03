from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Optional


@dataclass
class PredictParams:
    data_source: str = "qlib"
    provider_uri: Optional[str] = None
    instrument: str = ""
    start: str = ""
    end: str = ""
    future: bool = False
    adjust: str = "qfq"
    model_path: str = ""
    tokenizer_path: str = ""
    window: int = 64
    horizon: int = 5
    seed: int = 40
    temperature: float = 1.0
    top_p: float = 0.9
    sample_count: int = 1
    output_dir: str = "predictions"
    out: Optional[str] = None
    chart_out: Optional[str] = None
    max_context: int = 512
    device: str = "cpu"

    @classmethod
    def from_namespace(cls, args: Any) -> "PredictParams":
        data = {f.name: getattr(args, f.name) for f in fields(cls)}
        return cls(**data)


@dataclass
class TuneParams(PredictParams):
    grid_window: str = "64,128,256"
    grid_temp: str = "1.0,0.9"
    grid_top_p: str = "0.95,0.9"
    grid_sample_count: str = "1,5"
    tune_stride: int = 5
    tune_max_windows: int = 120
    tune_out: Optional[str] = None

    @classmethod
    def from_namespace(cls, args: Any) -> "TuneParams":
        data = {f.name: getattr(args, f.name) for f in fields(cls)}
        return cls(**data)
