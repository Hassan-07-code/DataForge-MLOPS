"""
============================================================
DataForge AI Platform
Dataset API
============================================================

Purpose:
    Dataset upload and preview endpoints.
============================================================
"""

from fastapi import APIRouter
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status

from backend.schemas.dataset_schema import (
    DatasetUploadResponse,
)

from backend.services.dataset_service import (
    dataset_service,
)


# ==========================================================
# Router
# ==========================================================

router = APIRouter(

    prefix="/dataset",

    tags=["Dataset"]

)


# ==========================================================
# Upload Dataset
# ==========================================================

@router.post(

    "/upload",

    response_model=DatasetUploadResponse,

    status_code=status.HTTP_200_OK,

    summary="Upload Dataset"

)

async def upload_dataset(

    file: UploadFile = File(...)

) -> DatasetUploadResponse:
    """
    Upload a CSV or Excel dataset.

    Returns:

        • Dataset summary

        • Dataset preview

        • File statistics
    """

    try:

        response = await dataset_service.process_dataset(

            file

        )

        return response

    except ValueError as error:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail=str(error)

        )

    except Exception as error:

        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"Dataset processing failed: {error}"

        )


# ==========================================================
# Health Check
# ==========================================================

@router.get(

    "/health",

    summary="Dataset Service Health"

)

async def dataset_health():
    """
    Dataset service status.
    """

    return {

        "success": True,

        "service": "Dataset API",

        "status": "Running"

    }