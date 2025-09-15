import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_app_startup():
    """Test that the app can start up successfully."""
    assert app is not None
