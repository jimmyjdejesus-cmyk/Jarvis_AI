# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from __future__ import annotations

import platform
from pathlib import Path
from typing import Optional

try:
    import onnxruntime as ort
except Exception:  # pragma: no cover - optional dependency
    ort = None

from .base import GenerationRequest, GenerationResponse, LLMBackend


class WindowsMLBackend(LLMBackend):
    """WindowsML/ONNX Runtime backed generator.

    This backend is intentionally conservative: it only reports availability when
    the runtime is Windows and an ONNX model path is provided. The model is
    assumed to output a textual response in a tensor named "response".
    """

    name = "windowsml"

    def __init__(self, model_path: Optional[Path], device_preference: str = "cpu"):
        self._model_path = model_path
        self._device_preference = device_preference
        self._session: Optional["ort.InferenceSession"] = None

    def is_available(self) -> bool:
        if ort is None:
            return False
        if platform.system().lower() != "windows":
            return False
        if not self._model_path or not self._model_path.exists():
            return False
        try:
            self._ensure_session()
            return True
        except Exception:
            return False

    def _ensure_session(self) -> "ort.InferenceSession":
        if self._session is not None:
            return self._session
        providers = ["CPUExecutionProvider"]
        if self._device_preference.lower() == "dml":
            providers.insert(0, "DmlExecutionProvider")
        self._session = ort.InferenceSession(str(self._model_path), providers=providers)  # type: ignore[arg-type]
        return self._session

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        session = self._ensure_session()
        prompt = request.context.encode("utf-8")
        inputs = {session.get_inputs()[0].name: [prompt]}
        outputs = session.run(None, inputs)
        tensor = outputs[0][0]
        if isinstance(tensor, bytes):
            content = tensor.decode("utf-8", errors="ignore")
        else:
            content = str(tensor)
        tokens = len(content.split())
        diagnostics = {"provider": ",".join(session.get_providers())}
        return GenerationResponse(content=content, tokens=tokens, backend=self.name, diagnostics=diagnostics)


__all__ = ["WindowsMLBackend"]
