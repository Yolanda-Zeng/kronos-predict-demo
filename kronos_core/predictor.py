from __future__ import annotations

from typing import Any, Optional


_predictor_cache: dict[tuple, Any] = {}


def load_kronos_predictor(model_path, tokenizer_path, max_context, device):
    from model import Kronos, KronosPredictor, KronosTokenizer

    print(f"[INFO] 正在加载 tokenizer: {tokenizer_path}")
    tokenizer = KronosTokenizer.from_pretrained(tokenizer_path)

    print(f"[INFO] 正在加载模型: {model_path}")
    model = Kronos.from_pretrained(model_path)

    return KronosPredictor(model, tokenizer, device=device, max_context=max_context)


def get_shared_predictor(model_path: str, tokenizer_path: str, max_context: int, device: str):
    key = (model_path, tokenizer_path, max_context, device)
    if key not in _predictor_cache:
        _predictor_cache[key] = load_kronos_predictor(model_path, tokenizer_path, max_context, device)
    return _predictor_cache[key]


def is_model_loaded() -> bool:
    return len(_predictor_cache) > 0


def clear_predictor_cache() -> None:
    _predictor_cache.clear()
