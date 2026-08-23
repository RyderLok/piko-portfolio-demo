"""Generate reproducible synthetic WAV clips for the public demo library."""
from __future__ import annotations

import math
from pathlib import Path
from typing import List

import numpy as np

import config
from sounds_store import _load_local_index, _save_local_index

SR = 16000
DEMO_SOURCE = "demo-synthetic"

SPECS = (
    ("demo-birds", "Demo · Birds", "chirp"),
    ("demo-wind", "Demo · Wind & leaves", "noise"),
    ("demo-water", "Demo · Water", "flow"),
    ("demo-impact", "Demo · Material impact", "click"),
    ("demo-insects", "Demo · Insects", "pulse"),
)


def _pcm16_wav(path: Path, y: np.ndarray, sr: int = SR) -> None:
    import wave

    y = np.clip(np.asarray(y, dtype=np.float32), -1.0, 1.0)
    pcm = (y * 32767.0).astype(np.int16)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def _synth(kind: str, seconds: float = 2.2) -> np.ndarray:
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    rng = np.random.default_rng(abs(hash(kind)) % (2**32))
    if kind == "chirp":
        y = np.zeros(n, dtype=np.float32)
        for k, start in enumerate((0.15, 0.55, 0.95, 1.4, 1.8)):
            i0 = int(start * SR)
            dur = int(0.09 * SR)
            i1 = min(n, i0 + dur)
            tt = np.arange(i1 - i0) / SR
            f0, f1 = 2200 + k * 180, 4800 + k * 120
            denom = 2 * max(float(tt[-1]) if tt.size else 1e-4, 1e-4)
            phase = 2 * math.pi * (f0 * tt + (f1 - f0) * tt * tt / denom)
            env = np.hanning(i1 - i0).astype(np.float32)
            y[i0:i1] += 0.35 * env * np.sin(phase).astype(np.float32)
        return y
    if kind == "noise":
        noise = rng.normal(0, 1, n).astype(np.float32)
        for _ in range(4):
            noise = (noise + np.roll(noise, 1)) * 0.5
        return 0.18 * noise * (0.7 + 0.3 * np.sin(2 * math.pi * 0.4 * t))
    if kind == "flow":
        y = 0.22 * np.sin(2 * math.pi * 110 * t)
        y += 0.12 * np.sin(2 * math.pi * 73 * t + 0.4)
        y += 0.08 * rng.normal(0, 1, n).astype(np.float32)
        return y * (0.6 + 0.4 * np.sin(2 * math.pi * 0.35 * t))
    if kind == "click":
        y = np.zeros(n, dtype=np.float32)
        for start in (0.2, 0.9, 1.55):
            i0 = int(start * SR)
            tail = np.exp(-np.arange(int(0.25 * SR)) / (0.04 * SR)).astype(np.float32)
            burst = rng.normal(0, 1, tail.size).astype(np.float32)
            i1 = min(n, i0 + tail.size)
            y[i0:i1] += 0.7 * tail[: i1 - i0] * burst[: i1 - i0]
        return y
    carrier = np.sin(2 * math.pi * 3400 * t).astype(np.float32)
    gate = (np.sin(2 * math.pi * 8 * t) > 0).astype(np.float32)
    return 0.22 * carrier * gate


def seed_demo_sounds() -> List[str]:
    """Write five synthetic clips into the local sounds store if missing."""
    rows = _load_local_index()
    by_id = {str(r.get("id")): r for r in rows}
    added: List[str] = []
    for sound_id, name, kind in SPECS:
        rel = f"{sound_id}.wav"
        path = config.LOCAL_SOUNDS_DIR / rel
        if sound_id not in by_id or not path.is_file():
            _pcm16_wav(path, _synth(kind))
            row = {
                "id": sound_id,
                "created_at": "2026-01-01T00:00:00+00:00",
                "name": name,
                "duration_ms": 2200,
                "sample_rate": SR,
                "upload_status": "uploaded",
                "storage_path": rel,
                "source": DEMO_SOURCE,
                "analysis": None,
                "brush": None,
                "demo": True,
            }
            rows = [r for r in rows if str(r.get("id")) != sound_id]
            rows.insert(0, row)
            added.append(sound_id)
    if added:
        _save_local_index(rows)
    return added
