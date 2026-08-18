"""
Listing de tous les types de variables qui entrent et sortent de l'API.
"""

# ╔════════════════════════════════════════════════════════════╗
# ║ 🚚 IMPORTS
# ╚════════════════════════════════════════════════════════════╝
from typing import List

from pydantic import BaseModel


# ╔════════════════════════════════════════════════════════════╗
# ║ 📝 SCHEMAS
# ╚════════════════════════════════════════════════════════════╝
class ChurnInput(BaseModel):
    """
    Prediction request structure.
    """

    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float


class PredictResponse(BaseModel):
    """
    Prediction response structure.
    """

    prediction: int
    churn: bool
    label: str
    probability: float


class ModelInfo(BaseModel):
    """
    Model info structure.
    """

    model_name: str
    model_type: str
    model_length: int
    model_features: list[str]
    model_description: str
    model_recall: float
    model_precision: float
    model_accuracy: float
    model_f1: float
    model_roc_auc: float


class ChurnBatchInput(BaseModel):
    """
    Batch prediction request structure.
    """

    data: List[ChurnInput]


class User(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
