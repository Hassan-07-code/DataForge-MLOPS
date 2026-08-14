from typing import List, Dict, Any, Optional

from pydantic import BaseModel


class PredictionRequest(BaseModel):
    """
    Single prediction request.
    """
    model_name: str

    dataset_name: str

    features: Dict[str, Any]


class PredictionResponse(BaseModel):
    """
    Prediction response.
    """

    prediction: Any

    probability: Optional[List[float]] = None

    model_name: str

    version: str

    stage: str


class BatchPredictionRequest(BaseModel):
    """
    Batch prediction.
    """
    dataset_name: str

    model_name: str

    rows: List[Dict[str, Any]]


class BatchPredictionResponse(BaseModel):

    predictions: List[Any]

    total_rows: int

    model_name: str

    version: str


class HealthResponse(BaseModel):

    status: str

    model_loaded: bool

    model_name: str

    version: str

    uptime: str


class RegistryResponse(BaseModel):

    dataset: str

    model: str

    latest_version: str

    staging: Optional[str]

    production: Optional[str]


class ErrorResponse(BaseModel):

    detail: str