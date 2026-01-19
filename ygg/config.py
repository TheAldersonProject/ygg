"""Project configuration."""

from pathlib import Path

CURRENT_FILE_PATH = Path(__file__).resolve()
SRC_FOLDER = CURRENT_FILE_PATH.parent
PROJECT_ROOT = SRC_FOLDER.parent.parent

DOCS_FOLDER = PROJECT_ROOT / "docs"

ASSETS_FOLDER = PROJECT_ROOT / "assets"
DATA_MODELS = ASSETS_FOLDER / "data-models"
