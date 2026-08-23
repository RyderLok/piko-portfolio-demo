"""Honest local stand-in for Qwen semantic labels when DEMO_MODE=true.

Does not call SiliconFlow or any network API. Uses the five-class
acoustic heuristic already in this repo so brush routing still works.
"""
from __future__ import annotations

import io
from typing import Any, Dict, Optional, Tuple

import numpy as np

from natural_sound_archetypes import ARCHETYPES, classify_natural_archetype

DEMO_PROVIDER = "demo-mock"
DEMO_MODEL = "piko-demo-acoustic-classifier"


def _decode_wav_mono(wav_bytes: bytes) -> Tuple[np.ndarray, int]:
    try:
        import soundfile as sf

        y, sr = sf.read(io.BytesIO(wav_bytes), dtype="float32", always_2d=False)
        if getattr(y, "ndim", 1) > 1:
            y = np.mean(y, axis=1)
        return np.asarray(y, dtype=np.float32), int(sr)
    except Exception:
        pass
    import wave

    with wave.open(io.BytesIO(wav_bytes), "rb") as w:
        sr = int(w.getframerate() or 16000)
        nch = int(w.getnchannels() or 1)
        sw = int(w.getsampwidth() or 2)
        n = int(w.getnframes() or 0)
        raw = w.readframes(n)
    if sw == 2:
        samples = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    else:
        samples = np.frombuffer(raw, dtype=np.uint8).astype(np.float32)
        samples = (samples - 128.0) / 128.0
    if nch > 1:
        samples = samples.reshape(-1, nch).mean(axis=1)
    return samples, sr


def analyze_semantic_demo(
    wav_bytes: bytes,
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
    if not wav_bytes:
        return None, {"code": "empty_audio", "message": "Demo mock: empty audio"}

    y, sr = _decode_wav_mono(wav_bytes)
    if y.size < 64:
        return None, {"code": "too_short", "message": "Demo mock: audio too short"}

    rms = float(np.sqrt(np.mean(y ** 2)))
    peak = float(np.max(np.abs(y)) + 1e-9)
    features = {
        "energy": min(1.0, rms / 0.25),
        "silenceRatio": float(np.mean(np.abs(y) < 0.02)),
        "dynamicRange": min(1.0, peak / (rms + 1e-6) / 20.0),
        "treble": 0.5,
        "bass": 0.4,
        "mid": 0.4,
        "pitch": 0.4,
        "continuity": 0.5,
        "spectralFlatness": 0.4,
        "roughness": 0.35,
        "zcr": 0.3,
        "onsetDensity": 0.4,
        "onsetRegularity": 0.4,
        "tempo": 0.4,
        "crestFactor": min(1.0, peak / (rms + 1e-6) / 12.0),
    }
    result = classify_natural_archetype(y, sr, features)
    arch = result.get("archetype") or {}
    aid = str(arch.get("id") or "water")
    meta = ARCHETYPES.get(aid) or ARCHETYPES["water"]
    conf = float(arch.get("confidence") or 0.55)
    return {
        "archetype": aid,
        "archetypeLabelZh": meta.get("labelZh") or aid,
        "soundLabel": meta.get("labelEn") or aid,
        "description": (
            "Demo simulated category (local acoustic heuristic, not Qwen). "
            + str(meta.get("waveform") or "")
        ),
        "possibleSources": [meta.get("labelEn") or aid, "synthetic demo clip"],
        "audibleEvents": [str(meta.get("spectrogram") or "demo texture")],
        "confidence": round(max(0.35, min(0.82, conf)), 3),
        "model": DEMO_MODEL,
        "provider": DEMO_PROVIDER,
    }, None
