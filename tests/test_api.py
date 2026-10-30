import pytest
from fastapi.testclient import TestClient
from src.app.main import app


@pytest.fixture(scope="module")
def client():
    """Test client fixture running within FastAPI lifespan context."""
    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# TEST 1: API CONTRACT
# ---------------------------------------------------------------------------
def test_api_contract_health(client):
    """
    PROTECTS AGAINST: Broken health check contract or unresponsive service.
    Verifies that GET /health responds with HTTP 200, valid JSON, and declares
    healthy status with model_loaded == True.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True


def test_api_contract_predict(client):
    """
    PROTECTS AGAINST: Breaking changes to prediction response format.
    Ensures POST /predict returns HTTP 200 with required schema fields:
    integer prediction, string class_name, and probability dictionary.
    """
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "class_name" in data
    assert "probabilities" in data
    assert isinstance(data["prediction"], int)
    assert isinstance(data["class_name"], str)
    assert isinstance(data["probabilities"], dict)

    # Probabilities should approximately sum to 1.0
    total_prob = sum(data["probabilities"].values())
    assert 0.99 <= total_prob <= 1.01


# ---------------------------------------------------------------------------
# TEST 2: INPUT SCHEMA VALIDATION
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "invalid_payload, expected_loc",
    [
        # Missing required field
        ({"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4}, "petal_width"),
        # Empty body
        ({}, "sepal_length"),
        # Invalid data type (string instead of float)
        (
            {
                "sepal_length": "invalid_string",
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2,
            },
            "sepal_length",
        ),
    ],
)
def test_input_schema_validation(client, invalid_payload, expected_loc):
    """
    PROTECTS AGAINST: Malformed requests, missing attributes, or invalid data types
    reaching the machine learning pipeline and causing unhandled server 500 crashes.
    FastAPI and Pydantic must reject these with HTTP 422 Unprocessable Entity.
    """
    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422, f"Failed for payload: {invalid_payload}"
    error_details = response.json().get("detail", [])
    locations = [str(err.get("loc", [])) for err in error_details]
    assert any(expected_loc in loc for loc in locations)


# ---------------------------------------------------------------------------
# TEST 3: EDGE CASES (NEGATIVE & OUT-OF-BOUNDS NUMBERS)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "edge_case_payload",
    [
        # Non-positive values (sepal length <= 0)
        {"sepal_length": -1.0, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
        {"sepal_length": 0.0, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
        # Unrealistic extreme biological values (> 20 cm)
        {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 999.0, "petal_width": 0.2},
    ],
)
def test_edge_cases_boundary_constraints(client, edge_case_payload):
    """
    PROTECTS AGAINST: Nonsensical or adversarial biological measurements (zero,
    negative values, or extreme out-of-distribution values) being fed to the model.
    Pydantic boundary checks (gt=0.0, le=20.0) catch these and return HTTP 422.
    """
    response = client.post("/predict", json=edge_case_payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TEST 4 & 5: DETERMINISTIC PREDICTIONS
# ---------------------------------------------------------------------------
def test_deterministic_prediction_setosa(client):
    """
    PROTECTS AGAINST: Silent model regressions, weight corruption, or incorrect feature
    scaling. Given canonical Setosa measurements, the model must deterministically
    classify it as Setosa (index 0) with high confidence (> 0.85).
    """
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == 0
    assert data["class_name"] == "setosa"
    assert data["probabilities"]["setosa"] >= 0.85


def test_deterministic_prediction_virginica(client):
    """
    PROTECTS AGAINST: Inverted or swapped model classes or decision boundary shifts.
    Given canonical Virginica measurements, the model must deterministically classify
    it as Virginica (index 2) with high confidence (> 0.80).
    """
    payload = {
        "sepal_length": 6.7,
        "sepal_width": 3.0,
        "petal_length": 5.2,
        "petal_width": 2.3,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == 2
    assert data["class_name"] == "virginica"
    assert data["probabilities"]["virginica"] >= 0.80
