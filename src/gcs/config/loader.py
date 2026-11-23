"""Load the JSON config file, merging over defaults."""
import copy
import json
import logging

log = logging.getLogger(__name__)

DEFAULTS = {
    "input": {"sample_rate_hz": 50, "deadzone": 0.1, "default_profile": "default"},
    "profiles_file": "config/profiles.json",
    "logging": {"level": "INFO", "file": "logs/gcs.log", "max_bytes": 1000000, "backup_count": 3},
}


def _merge(base, override):
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge(base[key], value)
        else:
            base[key] = value
    return base


def load_config(path="config/config.json"):
    cfg = copy.deepcopy(DEFAULTS)
    try:
        with open(path, encoding="utf-8") as f:
            _merge(cfg, json.load(f))
    except FileNotFoundError:
        log.warning("Config %s not found, using defaults", path)
    return cfg
