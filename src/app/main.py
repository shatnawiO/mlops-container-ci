import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Optional

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

# Model artifact container
DEFAULT_MODEL_PATH = os.getenv("MODEL_PATH", "models/model.joblib")


class IrisFeatures(BaseModel):
    sepal_length: float = Field(
        ..., gt=0.0, le=20.0, description="Sepal length in cm (must be > 0 and <= 20)"
    )
    sepal_width: float = Field(
        ..., gt=0.0, le=20.0, description="Sepal width in cm (must be > 0 and <= 20)"
    )
    petal_length: float = Field(
        ..., gt=0.0, le=20.0, description="Petal length in cm (must be > 0 and <= 20)"
    )
    petal_width: float = Field(
        ..., gt=0.0, le=20.0, description="Petal width in cm (must be > 0 and <= 20)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2,
            }
        }
    }


class PredictionResponse(BaseModel):
    prediction: int
    class_name: str
    probabilities: Dict[str, float]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_type: Optional[str] = None


def load_model_from_disk(path: str = DEFAULT_MODEL_PATH) -> Optional[dict]:
    """Load model artifact from disk if available."""
    model_file = Path(path)
    if model_file.exists():
        return joblib.load(model_file)
    return None


model_artifact: Optional[dict] = load_model_from_disk(DEFAULT_MODEL_PATH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to ensure model is loaded on startup."""
    global model_artifact
    if model_artifact is None:
        model_artifact = load_model_from_disk(DEFAULT_MODEL_PATH)
    if model_artifact is None:
        from src.train.train import train_and_save

        model_artifact = train_and_save(DEFAULT_MODEL_PATH)
    yield


app = FastAPI(
    title="AI381 MLOps - Machine Learning Inference Service",
    description="Containerized inference API for AI381 MLOps Lab 2",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False)
def root():
    return {
        "message": "AI381 MLOps Model API is running.",
        "health": "/health",
        "docs": "/docs",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
)
def health():
    """Healthcheck endpoint returning service health and model status."""
    is_loaded = model_artifact is not None and "pipeline" in model_artifact
    model_type = model_artifact.get("model_type") if is_loaded else None
    return HealthResponse(
        status="healthy" if is_loaded else "degraded",
        model_loaded=is_loaded,
        model_type=model_type,
    )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict iris flower variety",
)
def predict(features: IrisFeatures):
    """Predict flower class based on physical measurements with pydantic schema validation."""
    if model_artifact is None or "pipeline" not in model_artifact:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded or unavailable.",
        )

    pipeline = model_artifact["pipeline"]
    target_names = model_artifact.get(
        "target_names", ["setosa", "versicolor", "virginica"]
    )

    input_vector = np.array(
        [
            [
                features.sepal_length,
                features.sepal_width,
                features.petal_length,
                features.petal_width,
            ]
        ]
    )

    pred = int(pipeline.predict(input_vector)[0])
    probs = pipeline.predict_proba(input_vector)[0]

    prob_dict = {
        name: round(float(p), 4) for name, p in zip(target_names, probs)
    }

    return PredictionResponse(
        prediction=pred,
        class_name=target_names[pred],
        probabilities=prob_dict,
    )
