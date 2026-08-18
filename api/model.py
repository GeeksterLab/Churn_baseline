"""
- POST /predict         → prediction for 1 customer
- POST /predict-batch   → prediction for several customers
- POST /upload          → CSV upload
- GET  /model-info      → model load information
"""

# ╔════════════════════════════════════════════════════════════╗
# ║ 🚚 IMPORTS
# ╚════════════════════════════════════════════════════════════╝

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends

from core.settings import settings
import pandas as pd

# ╔════════════════════════════════════════════════════════════╗
# ║ 🌐 API
# ╚════════════════════════════════════════════════════════════╝
import joblib
from fastapi import APIRouter

model_predict = APIRouter()
model_predict_batch = APIRouter()
model_upload = APIRouter()
model_info = APIRouter()

# ╔════════════════════════════════════════════════════════════╗
# ║ 🛣️ ROUTERS
# ╚════════════════════════════════════════════════════════════╝
from api.schemas import (
    ChurnInput,
    PredictResponse,
    ModelInfo,
    ChurnBatchInput,
)
from api.utils import get_model, get_current_user
import csv
from io import StringIO
from sklearn.linear_model import LogisticRegression


# ── PREDICT ──────────────────────────────────────────────────
@model_predict.post("/predict", response_model=PredictResponse, tags=["Predict"])
def predict_churn(
    data: ChurnInput,
    baseline=Depends(get_model),
    current_user: str = Depends(get_current_user),
) -> PredictResponse:

    # ═════════════════════ Transform the data ═════════════════════
    df = pd.json_normalize(data.model_dump())

    # ═════════════════════ Send the data ═════════════════════
    prediction = baseline["model"].predict(df)[0]
    probability = baseline["model"].predict_proba(df)[0][1]

    return PredictResponse(
        prediction=prediction,
        churn=prediction,
        label="Churn" if prediction == 1 else "No Churn",
        probability=round(probability, 2),
    )


# ── PREDICT BATCH ──────────────────────────────────────────────────
@model_predict_batch.post("/predict-batch", tags=["PredictBatch"])
async def predict_batch(
    data: ChurnBatchInput,
    baseline=Depends(get_model),
    current_user: str = Depends(get_current_user),
) -> list[PredictResponse]:

    results = []

    for client in data.data:
        df = pd.json_normalize(client.model_dump())

        prediction = baseline["model"].predict(df)[0]
        probability = baseline["model"].predict_proba(df)[0][1]

        # PredictResponse for each client and append to results
        results.append(
            PredictResponse(
                prediction=prediction,
                churn=prediction,
                label="Churn" if prediction == 1 else "No Churn",
                probability=round(probability, 2),
            )
        )

    return results


# ── UPLOAD ──────────────────────────────────────────────────
@model_upload.post("/upload-csv", tags=["Upload"])
async def upload_csv(file: UploadFile = File(...)):
    data = []

    # Read file as bytes and decode bytes info text stream
    file_bytes = await file.read()
    buffer = StringIO(file_bytes.decode("utf-8"))

    # Process CSV
    csvReader = csv.DictReader(buffer)
    for row in csvReader:
        data.append(row)

    # Close buffer and file
    buffer.close()
    await file.close()

    # Return JSON
    return data


# ── MORE INFO ──────────────────────────────────────────────────
@model_info.get("/model-info", response_model=ModelInfo, tags=["ModelInfo"])
async def model_information(
    baseline=Depends(get_model),
    current_user: str = Depends(get_current_user),
) -> ModelInfo:

    # Is our model exists?
    if not settings.BASELINE_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Baseline model file not found.",
        )

    else:
        return ModelInfo(
            model_name=settings.BASELINE_PATH.name,
            model_type=baseline["type"],
            model_length=baseline["length"],
            model_features=baseline["features"],
            model_description="Baseline model for churn prediction",
            model_recall=round(baseline["metrics"]["recall"], 2),
            model_precision=round(baseline["metrics"]["precision"], 2),
            model_accuracy=round(baseline["metrics"]["accuracy"], 2),
            model_f1=round(baseline["metrics"]["f1"], 2),
            model_roc_auc=round(baseline["metrics"]["roc_auc"], 2),
        )
