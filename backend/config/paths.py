from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

ARTIFACTS_DIR = BASE_DIR / "artifacts"

MODELS_DIR = ARTIFACTS_DIR / "models"
REPORT_DIR = ARTIFACTS_DIR / "reports"
PLOT_DIR = ARTIFACTS_DIR / "plots"
METADATA_DIR = ARTIFACTS_DIR / "metadata"

DATASET_DIR = BASE_DIR / "datasets"

LOGS_DIR = BASE_DIR / "logs"