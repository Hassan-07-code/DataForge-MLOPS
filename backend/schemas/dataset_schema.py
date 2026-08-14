"""
===========================================================
DataForge AI Platform
Dataset Upload Schemas
===========================================================

Purpose:
    Pydantic models for Dataset Management APIs.

Author:
    Hassan
===========================================================
"""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


# ===========================================================
# Dataset Summary
# ===========================================================

class DatasetSummary(BaseModel):
    """Dataset statistics."""

    filename: str = Field(..., description="Uploaded dataset filename")
    rows: int = Field(..., ge=0)
    columns: int = Field(..., ge=0)
    size_mb: float = Field(..., ge=0)
    missing_values: int = Field(..., ge=0)
    numerical_columns: int = Field(..., ge=0)
    categorical_columns: int = Field(..., ge=0)


# ===========================================================
# Dataset Preview
# ===========================================================

class DatasetPreview(BaseModel):
    """Preview of uploaded dataset."""

    columns: List[str] = Field(
        default_factory=list,
        description="Dataset column names"
    )

    records: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Preview rows"
    )


# ===========================================================
# Upload Response
# ===========================================================

class DatasetUploadResponse(BaseModel):
    """Complete upload response."""

    success: bool = True

    message: str = "Dataset uploaded successfully."

    summary: DatasetSummary

    preview: DatasetPreview


# ===========================================================
# Error Response
# ===========================================================

class DatasetErrorResponse(BaseModel):
    """API error response."""

    success: bool = False

    message: str

    details: str | None = None                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             