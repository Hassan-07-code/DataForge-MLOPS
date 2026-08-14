"""
============================================================
DataForge AI Platform
Dataset Processing Service
============================================================

Purpose:
    Centralized dataset processing service.

Responsibilities:
    • Validate uploaded files
    • Read CSV / Excel
    • Generate statistics
    • Generate preview
    • Return API response

Author:
    Hassan
============================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import UploadFile

from  backend.schemas.dataset_schema import (
    DatasetPreview,
    DatasetSummary,
    DatasetUploadResponse,
)

# ==========================================================
# Supported Extensions
# ==========================================================

SUPPORTED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
}

MAX_PREVIEW_ROWS = 100


# ==========================================================
# Dataset Service
# ==========================================================

class DatasetService:
    """
    Handles dataset upload and processing.
    """

    def __init__(self) -> None:

        self.dataframe: pd.DataFrame | None = None

        self.filename: str = ""

        self.file_size_mb: float = 0.0


    # ======================================================
    # File Validation
    # ======================================================

    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """
        Validate uploaded dataset.
        """

        if file is None:

            raise ValueError("No dataset was uploaded.")

        if not file.filename:

            raise ValueError("Filename is missing.")

        extension = Path(file.filename).suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:

            raise ValueError(
                f"Unsupported file format: {extension}"
            )


    # ======================================================
    # Load Dataset
    # ======================================================

    async def load_dataset(
        self,
        file: UploadFile,
    ) -> pd.DataFrame:
        """
        Read uploaded dataset into pandas.
        """

        self.validate_file(file)

        self.filename = file.filename

        extension = Path(file.filename).suffix.lower()

        contents = await file.read()

        self.file_size_mb = round(
            len(contents) / (1024 * 1024),
            2,
        )

        if extension == ".csv":

            dataframe = self._read_csv(contents)

        else:

            dataframe = self._read_excel(contents)

        if dataframe.empty:

            raise ValueError(
                "Uploaded dataset is empty."
            )

        self.dataframe = dataframe

        return self.dataframe

    # ======================================================
    # Read CSV
    # ======================================================

    @staticmethod
    def _read_csv(contents: bytes) -> pd.DataFrame:
        """
        Read CSV dataset.
        """

        from io import BytesIO

        return pd.read_csv(
            BytesIO(contents)
        )


    # ======================================================
    # Read Excel
    # ======================================================

    @staticmethod
    def _read_excel(contents: bytes) -> pd.DataFrame:
        """
        Read Excel dataset.
        """

        from io import BytesIO

        return pd.read_excel(
            BytesIO(contents)
        )


    # ======================================================
    # Generate Dataset Summary
    # ======================================================

    def generate_summary(self) -> DatasetSummary:
        """
        Generate dataset statistics.
        """

        if self.dataframe is None:

            raise ValueError(
                "Dataset has not been loaded."
            )

        dataframe = self.dataframe

        total_rows = len(dataframe)

        total_columns = len(dataframe.columns)

        missing_values = int(
            dataframe.isna().sum().sum()
        )

        numerical_columns = len(

            dataframe.select_dtypes(

                include="number"

            ).columns

        )

        categorical_columns = (

            total_columns - numerical_columns

        )

        return DatasetSummary(

            filename=self.filename,

            rows=total_rows,

            columns=total_columns,

            size_mb=self.file_size_mb,

            missing_values=missing_values,

            numerical_columns=numerical_columns,

            categorical_columns=categorical_columns,

        )

    # ======================================================
    # Generate Dataset Preview
    # ======================================================

    def generate_preview(self) -> DatasetPreview:
        """
        Generate preview of uploaded dataset.
        """

        if self.dataframe is None:

            raise ValueError(
                "Dataset has not been loaded."
            )

        dataframe = self.dataframe.copy()

        preview_dataframe = dataframe.head(
            MAX_PREVIEW_ROWS
        )

        preview_dataframe = preview_dataframe.fillna("")

        return DatasetPreview(

            columns=list(preview_dataframe.columns),

            records=preview_dataframe.to_dict(
                orient="records"
            ),

        )


    # ======================================================
    # Detect Column Types
    # ======================================================

    def detect_column_types(self) -> dict[str, list[str]]:
        """
        Detect numerical and categorical columns.
        """

        if self.dataframe is None:

            raise ValueError(
                "Dataset has not been loaded."
            )

        dataframe = self.dataframe

        numerical_columns = dataframe.select_dtypes(
            include="number"
        ).columns.tolist()

        categorical_columns = dataframe.select_dtypes(
            exclude="number"
        ).columns.tolist()

        return {

            "numerical": numerical_columns,

            "categorical": categorical_columns,

        }


    # ======================================================
    # Dataset Shape
    # ======================================================

    def get_shape(self) -> tuple[int, int]:
        """
        Return dataset shape.
        """

        if self.dataframe is None:

            raise ValueError(
                "Dataset has not been loaded."
            )

        return self.dataframe.shape


    # ======================================================
    # Column Names
    # ======================================================

    def get_columns(self) -> list[str]:
        """
        Return dataset column names.
        """

        if self.dataframe is None:

            raise ValueError(
                "Dataset has not been loaded."
            )

        return self.dataframe.columns.tolist()


    # ======================================================
    # Missing Values
    # ======================================================

    def get_missing_values(self) -> dict[str, int]:
        """
        Return missing values per column.
        """

        if self.dataframe is None:

            raise ValueError(
                "Dataset has not been loaded."
            )

        return (

            self.dataframe

            .isnull()

            .sum()

            .astype(int)

            .to_dict()

        )

    # ======================================================
    # Build Upload Response
    # ======================================================

    def build_response(self) -> DatasetUploadResponse:
        """
        Build complete dataset upload response.
        """

        return DatasetUploadResponse(

            success=True,

            message="Dataset uploaded successfully.",

            summary=self.generate_summary(),

            preview=self.generate_preview(),

        )


    # ======================================================
    # Process Dataset
    # ======================================================

    async def process_dataset(
        self,
        file: UploadFile,
    ) -> DatasetUploadResponse:
        """
        Complete dataset processing pipeline.
        """

        await self.load_dataset(file)

        return self.build_response()


    # ======================================================
    # Reset Service
    # ======================================================

    def reset(self) -> None:
        """
        Clear loaded dataset.
        """

        self.dataframe = None
        self.filename = ""
        self.file_size_mb = 0.0


# ==========================================================
# Service Instance
# ==========================================================

dataset_service = DatasetService()
    