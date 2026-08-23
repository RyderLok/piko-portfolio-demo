"""Demo mode must not require cloud credentials."""
import io
import wave

import numpy as np

import config
from demo_assets import _synth, seed_demo_sounds
from demo_semantic import analyze_semantic_demo


def test_demo_mode_default_true():
    assert config.DEMO_MODE is True


def test_supabase_disabled_in_demo():
    assert config.supabase_configured() is False


def test_local_semantic_returns_five_class_label():
    y = _synth("chirp")
    pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(pcm.tobytes())
    semantic, err = analyze_semantic_demo(buf.getvalue())
    assert err is None
    assert semantic["provider"] == "demo-mock"
    assert semantic["archetype"] in {
        "birds",
        "wind_leaves",
        "water",
        "material_impact",
        "insects_amphibians",
    }


def test_seed_demo_sounds_writes_wavs(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "LOCAL_SOUNDS_DIR", tmp_path)
    monkeypatch.setattr(config, "LOCAL_SOUNDS_INDEX", tmp_path / "index.json")
    added = seed_demo_sounds()
    assert added
    assert (tmp_path / "demo-birds.wav").is_file()
