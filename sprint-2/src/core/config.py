import sys
import logging
from pathlib import Path

def get_base_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent

def get_data_path() -> Path:
    base = get_base_path()
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / "data"
    return base / "data"

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )