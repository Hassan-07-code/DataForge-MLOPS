from datetime import datetime
import time
import pandas as pd
import platform
import psutil
from fastapi import APIRouter, HTTPException, Request

from backend.api.json_error import validate_features
from backend.api.prediction_logger import PredictionLogger
from backend.api.loader import ModelLoader
from backend.api.schemas import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse
)

# --------------------------------------------------------
# Configuration
# --------------------------------------------------------

REGISTRY_DIR = "artifacts/registry"
MODELS_DIR = "artifacts/models"

loader = ModelLoader(
    registry_dir=REGISTRY_DIR,
    models_dir=MODELS_DIR
)
prediction_logger = PredictionLogger()

router = APIRouter()


# ==========================================================
# Health
# ==========================================================

@router.get(
    "/health",
    response_model=HealthResponse
)
def health():

    try:

        info = loader.cache.info()

        if info["loaded"]:

            metadata = info["metadata"]

            return HealthResponse(

                status="healthy",

                model_loaded=True,

                model_name=metadata["model"],

                version=metadata["version"],

                uptime=str(datetime.now() - loader.cache.get_loaded_time())

            )

        return HealthResponse(

            status="healthy",

            model_loaded=False,

            model_name="",

            version="",

            uptime="0"

        )

    except Exception as e:
        prediction_logger.log_error(...)

        raise HTTPException(500, str(e))


# ==========================================================
# System Metrics
# ==========================================================
@router.get("/system")
def system_metrics():
    memory = psutil.virtual_memory()

    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_mb": round(
            psutil.Process().memory_info().rss / (1024 * 1024),
            2
        ),
        "ram_gb": round(
            memory.total / (1024 ** 3),
            2
        ),
        "ram_percent": memory.percent,
        "python_version": platform.python_version(),
        "operating_system": platform.platform(),
        "timestamp": datetime.now().isoformat(),
    }


# ==========================================================
# Predict
# ==========================================================
@router.post(
    "/predict",
    response_model=PredictionResponse
)
def predict(request: PredictionRequest, http_request: Request):
    start = time.perf_counter()

    try:

        df = pd.DataFrame([request.features])

        model = loader.get_model(
            request.dataset_name,
            request.model_name
        )
        df = validate_features(model, df)

        prediction = loader.predict(

            request.dataset_name,

            request.model_name,

            df

        )

        probability = loader.predict_proba(

            request.dataset_name,

            request.model_name,

            df

        )

        metadata = loader.metadata(

            request.dataset_name,

            request.model_name

        )

        latency = (time.perf_counter() - start) * 1000

        prediction_logger.log_prediction(
            client_ip = http_request.client.host,
            endpoint="/predict",
            dataset_name=request.dataset_name,
            model_name=request.model_name,
            version=metadata["version"],
            latency_ms=latency,
            prediction_count=1
        )

        return PredictionResponse(

            prediction=prediction.tolist()[0],

            probability=(
                probability.tolist()[0]
                if probability is not None
                else None
            ),

            model_name=metadata["model"],

            version=metadata["version"],

            stage=metadata["stage"]

        )

    except Exception as e:
        prediction_logger.log_error(
            client_ip=http_request.client.host,
            endpoint  = "/predict",
            dataset_name=request.dataset_name,
            model_name = request.model_name,
            error = e
        )

        raise HTTPException(status_code=500, detail =str(e))


# ==========================================================
# Batch Prediction
# ==========================================================

@router.post(
    "/batch_predict",
    response_model=BatchPredictionResponse
)
def batch_predict(
    request: BatchPredictionRequest,
    http_request: Request
):

    start = time.perf_counter()

    try:

        df = pd.DataFrame(request.rows)

        preds = loader.predict(

            request.dataset_name,

            request.model_name,

            df

        )

        model = loader.get_model(
            request.dataset_name,
            request.model_name
        )
        df = validate_features(model, df)

        metadata = loader.metadata(

            request.dataset_name,

            request.model_name

        )

        latency = (time.perf_counter() - start) * 1000

        prediction_logger.log_prediction(

            client_ip=http_request.client.host,

            endpoint="/batch_predict",

            dataset_name=request.dataset_name,

            model_name=request.model_name,

            version=metadata["version"],

            latency_ms=latency,

            prediction_count=len(df)

        )

        return BatchPredictionResponse(

            predictions=preds.tolist(),

            total_rows=len(df),

            model_name=metadata["model"],

            version=metadata["version"]

        )

    except Exception as e:

        prediction_logger.log_error(

            client_ip=http_request.client.host,

            endpoint="/batch_predict",

            dataset_name=request.dataset_name,

            model_name=request.model_name,

            error=e

        )

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )

# ==========================================================
# Registry Information
# ==========================================================

@router.get("/metadata/{dataset}/{model}")
def models():

    return loader.registry.load_registry()


# ==========================================================
# Versions
# ==========================================================

@router.get("/versions/{dataset}/{model}")
def versions(
    dataset: str,
    model: str
):

    return loader.registry.list_versions(

        dataset,

        model

    )


# ==========================================================
# Reload
# ==========================================================

@router.post("/reload")
def reload_model(

    dataset: str,

    model: str

):

    loader.reload(

        dataset,

        model

    )

    return {

        "status": "success",

        "message": "Production model reloaded."

    }