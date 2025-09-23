import pytest
from unittest.mock import patch
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
    assert health_data["status"] in ["healthy", "degraded"]
    assert "environment" in health_data
    assert "version" in health_data
    assert "debug" in health_data
    assert "is_lambda" in health_data
    # database_status is optional (only present if MongoDB URL is configured)


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

    # Verify database_status field if present
    if "database_status" in health_data:
        assert health_data["database_status"] in ["connected", "disconnected", "error", None]


def test_health_endpoint_with_database_connected(client):
    """Test health endpoint with database connected"""
    with patch("app.config.settings.db_config.mongodb_url", "mongodb://test"), \
         patch("app.core.database.check_database_health", return_value=True):

        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()
        health_data = data["data"]

        assert health_data["status"] == "healthy"
        assert health_data["database_status"] == "connected"


def test_health_endpoint_with_database_disconnected(client):
    """Test health endpoint with database disconnected"""
    with patch("app.config.settings.db_config.mongodb_url", "mongodb://test"), \
         patch("app.core.database.check_database_health", return_value=False):

        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()
        health_data = data["data"]

        assert health_data["status"] == "degraded"
        assert health_data["database_status"] == "disconnected"


def test_health_endpoint_with_database_error(client):
    """Test health endpoint with database error"""
    with patch("app.config.settings.db_config.mongodb_url", "mongodb://test"), \
         patch("app.core.database.check_database_health", side_effect=Exception("Connection error")):

        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()
        health_data = data["data"]

        assert health_data["status"] == "degraded"
        assert health_data["database_status"] == "error"


def test_health_endpoint_without_database_url(client):
    """Test health endpoint without MongoDB URL configured"""
    with patch("app.config.settings.db_config.mongodb_url", None):

        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()
        health_data = data["data"]

        assert health_data["status"] == "healthy"
        assert "database_status" not in health_data or health_data["database_status"] is None


@pytest.mark.asyncio
async def test_health_endpoint_async_database_check():
    """Test health endpoint with async database health check"""
    from app.core.database import check_database_health

    # Test database health check function directly
    with patch("app.core.database.client", None):
        result = await check_database_health()
        assert result is False

    # Test with mock client that raises exception
    mock_client = patch("app.core.database.client")
    with mock_client as client_mock:
        client_mock.admin.command.side_effect = Exception("Connection failed")
        result = await check_database_health()
        assert result is False