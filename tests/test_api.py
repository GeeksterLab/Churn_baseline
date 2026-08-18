"""
GET /health → return 200
POST /login → return a token
POST /predict → without token return 401
POST /predict → with allowed token return a prediction

"""

# ╔════════════════════════════════════════════════════════════╗
# ║ 🚚 IMPORTS
# ╚════════════════════════════════════════════════════════════╝
import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


# TestClient + lifespan = need manager context
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": "Predict Churn",
    }


def test_login(client):
    # Login to get the token
    response = client.post(
        "/login", data={"username": "admin", "password": "tutochurn"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_error_predict(client):
    response = client.post("/predict")
    assert response.status_code == 401


def test_predict(client):
    # Login to get the token
    login = client.post("/login", data={"username": "admin", "password": "tutochurn"})
    token = login.json()["access_token"]

    # Predict with a token + body
    response = client.post(
        "/predict",
        json={
            "gender": "Male",
            "SeniorCitizen": 1,
            "Partner": "No",
            "Dependents": "Yes",
            "tenure": 1,
            "PhoneService": "No",
            "MultipleLines": "No phone service",
            "InternetService": "DSL",
            "OnlineSecurity": "No",
            "OnlineBackup": "No",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "Yes",
            "StreamingMovies": "No",
            "Contract": "Month-to-month",
            "PaperlessBilling": "No",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 18.54,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "prediction" in response.json()
    assert "churn" in response.json()
    assert "label" in response.json()
    assert "probability" in response.json()
