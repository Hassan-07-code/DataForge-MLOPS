import os

# App
APP_NAME = "DataForge"
VERSION = "2.0.0-dev"

# ML
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5

# Upload
MAX_UPLOAD_SIZE_MB = 200

# Training
N_JOBS = -1

# Logging
LOG_LEVEL = "INFO"

# =====================================================
# API
# =====================================================
API_HOST = "127.0.0.1"
API_TIMEOUT = 30
API_PORT = 8000
API_URL = f"http://{API_HOST}:{API_PORT}"

# =====================================================
# WATCHER
# =====================================================
WATCH_INTERVAL = 5

# ==========================
# Paths
# ==========================

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")

MODELS_DIR = os.path.join(ARTIFACTS_DIR, "models")

REPORTS_DIR = os.path.join(ARTIFACTS_DIR, "reports")

PLOTS_DIR = os.path.join(ARTIFACTS_DIR, "plots")

REGISTRY_DIR = os.path.join(ARTIFACTS_DIR, "registry")

MLFLOW_DIR = os.path.join(ARTIFACTS_DIR, "mlflow")

LOGS_DIR = os.path.join(ARTIFACTS_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# ==========================
# MLflow
# ==========================

MLFLOW_TRACKING_URI = "sqlite:///" + os.path.join(BASE_DIR, "mlflow.db").replace("\\", "/")

MLFLOW_EXPERIMENT_NAME = "DataForge"

MLFLOW_REGISTER_MODEL = False

# =====================================================
# Create Directories
# =====================================================

for directory in [
    ARTIFACTS_DIR,
    MODELS_DIR,
    REGISTRY_DIR,
    LOGS_DIR,
    REPORTS_DIR,
    PLOTS_DIR
]:
    os.makedirs(directory, exist_ok=True)