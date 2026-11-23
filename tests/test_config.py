import json

from gcs.config.loader import load_config


def test_missing_file_gives_defaults(tmp_path):
    cfg = load_config(str(tmp_path / "nope.json"))
    assert cfg["input"]["sample_rate_hz"] == 50


def test_file_overrides_defaults(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"input": {"sample_rate_hz": 100}}))
    cfg = load_config(str(p))
    assert cfg["input"]["sample_rate_hz"] == 100
    assert cfg["input"]["deadzone"] == 0.1  # untouched default kept
