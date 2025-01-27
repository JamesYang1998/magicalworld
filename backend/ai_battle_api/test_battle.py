import pytest
import httpx
import json
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.services import AIServiceError

client = TestClient(app)

def test_create_battle():
    """Test creating a new battle"""
    response = client.post(
        "/api/battles",
        json={"topic": "Who is the better AI assistant?", "rounds": 3}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "in_progress"
    assert len(data["messages"]) == 1  # Initial system message
    assert data["messages"][0]["role"] == "system"

def test_get_nonexistent_battle():
    """Test getting a battle that doesn't exist"""
    response = client.get("/api/battles/nonexistent-id")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_battle_round_progression():
    """Test battle round progression"""
    # Create a battle first
    create_response = client.post(
        "/api/battles",
        json={"topic": "Test battle topic", "rounds": 1}
    )
    assert create_response.status_code == 200
    battle_id = create_response.json()["id"]
    
    # Process a round
    round_response = client.post(f"/api/battles/{battle_id}/round")
    assert round_response.status_code == 503  # Should fail without API keys
    assert "API key not configured" in round_response.json()["detail"]

def test_healthcheck():
    """Test health check endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
