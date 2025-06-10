# backend/tests/test_api.py
from fastapi.testclient import TestClient
from backend.main import app # Adjusted import path assuming 'backend' is on PYTHONPATH or tests run from root

client = TestClient(app)

def test_read_main():
    response = client.get("/") # This will fail as there's no "/" route, but /docs or /api/realtime?region=Europe
    # Let's test a known endpoint like /docs
    response_docs = client.get("/docs")
    assert response_docs.status_code == 200

    response_api = client.get("/api/realtime?region=TestRegion")
    assert response_api.status_code == 200
    assert response_api.json()["region"] == "TestRegion"
    assert "message" in response_api.json() # Check for the dummy data message

def test_simulate_add_plant_api():
    payload = {
        "name": "Test Solar Plant API",
        "type": "solar",
        "capacity": 100,
        "start_date": "2024-01-01",
        "lat": 50.0,
        "lon": 10.0,
        "region": "TestRegionAPI"
    }
    response = client.post("/api/simulation/add", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["simulation_details"]["action"] == "add_plant"
    assert data["simulation_details"]["plant_added"]["name"] == "Test Solar Plant API"
    assert data["production"]["solar"] > 0 # Check if solar production was added/calculated
