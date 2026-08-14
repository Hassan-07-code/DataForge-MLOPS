from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.dataset import router as dataset_router
from backend.api.routes import router, loader
from backend.api.watcher import RegistryWatcher
from backend.api.prediction_logger import PredictionLogger
from backend.config.settings import API_HOST, API_PORT


# ==========================================================
# Global Services
# ==========================================================

prediction_logger = PredictionLogger()
watcher = RegistryWatcher(loader)


# ==========================================================
# Lifespan
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    prediction_logger.log_event(
        "API Started"
    )

    watcher.start()

    print("=" * 60)
    print("DataForge Prediction API Started")
    print("=" * 60)

    yield

    watcher.stop()

    prediction_logger.log_event(
        "API Shutdown"
    )

    print("=" * 60)
    print("DataForge Prediction API Shutdown")
    print("=" * 60)


# ==========================================================
# FastAPI App
# ==========================================================

app = FastAPI(

    title="DataForge API",

    description="Enterprise Model Serving API",

    version="1.0.0",

    lifespan=lifespan

)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# Routers
# ==========================================================

app.include_router(

    router,

    prefix="/api",

    tags=["Prediction"]

)


# ==========================================================
# Root
# ==========================================================

@app.get("/")
def root():

    return {

        "application": "DataForge",

        "version": "1.0.0",

        "status": "running",

        "docs": "/docs"

    }


# ==========================================================
# API Information
# ==========================================================

@app.get("/info")
def info():

    return {

        "application": "DataForge",

        "api_version": "1.0.0",

        "host": API_HOST,

        "port": API_PORT,

        "watcher_running": watcher.running,

        "cache_loaded": loader.cache.is_loaded()

    }

#====================================================
# DataForge API Server
#====================================================
app.include_router(
    dataset_router,
    prefix="/api"
)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           


# ==========================================================
# Run
# ==========================================================

if __name__ == "__main__":

    uvicorn.run(

        "backend.api.server:app",

        host=API_HOST,

        port=API_PORT,

        reload=True

    )