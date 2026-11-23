"""Logging: console + rotating file."""
import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(level="INFO", file="logs/gcs.log", max_bytes=1_000_000, backup_count=3):
    os.makedirs(os.path.dirname(file) or ".", exist_ok=True)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(threadName)s %(name)s: %(message)s")
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    rotating = RotatingFileHandler(file, maxBytes=max_bytes, backupCount=backup_count)
    rotating.setFormatter(fmt)
    root.addHandler(console)
    root.addHandler(rotating)
