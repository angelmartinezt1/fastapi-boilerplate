import pytest
from fastapi.testclient import TestClient
from app.main import create_app


@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    return TestClient(app)


def test_health_endpoint_success(client):
    """Test health endpoint returns successful response"""
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    # Verify standard response structure
    assert "metadata" in data
    assert "data" in data

    # Verify metadata
    metadata = data["metadata"]
    assert metadata["success"] is True
    assert metadata["message"] == "Health check completed successfully"
    assert "timestamp" in metadata

    # Verify health data
    health_data = data["data"]
    assert health_data["status"] == "healthy"
    assert "environment" in health_data
    assert "version" in health_data
    assert "debug" in health_data
    assert "is_lambda" in health_data


def test_health_endpoint_response_model(client):
    """Test health endpoint response matches expected model"""
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    health_data = data["data"]

    # Verify all required fields are present
    required_fields = ["status", "environment", "version", "debug", "is_lambda"]
    for field in required_fields:
        assert field in health_data

    # Verify field types
    assert isinstance(health_data["status"], str)
    assert isinstance(health_data["environment"], str)
    assert isinstance(health_data["version"], str)
    assert isinstance(health_data["debug"], bool)
    assert isinstance(health_data["is_lambda"], bool)