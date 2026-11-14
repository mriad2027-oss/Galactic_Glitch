"""
Unit and integration tests for TerraTwin FastAPI backend
"""
from fastapi.testclient import TestClient
from backend.api.app import app

client = TestClient(app)

def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert "TerraTwin" in data["service"]
    print("[OK] /api/v1/health passed")

def test_planets():
    r = client.get("/api/v1/planets")
    assert r.status_code == 200
    data = r.json()
    assert len(data["planets"]) == 3
    print("[OK] /api/v1/planets passed")

def test_datasets():
    r = client.get("/api/v1/planets/moon/datasets")
    assert r.status_code == 200
    data = r.json()
    assert "datasets" in data
    print(f"[OK] /api/v1/planets/moon/datasets passed ({len(data['datasets'])} datasets)")

def test_layers():
    r = client.get("/api/v1/planets/moon/layers")
    assert r.status_code == 200
    data = r.json()
    assert len(data["layers"]) >= 4
    print("[OK] /api/v1/planets/moon/layers passed")

def test_search_analogs_moon():
    req = {
        "planet": "moon",
        "lat": -85.5,
        "lon": 0.0,
        "features": ["Elevation", "Slope", "Roughness", "Temperature", "Mineralogy"]
    }
    r = client.post("/api/v1/analogs/search", json=req)
    assert r.status_code == 200
    data = r.json()
    assert data["demo"] is False
    assert len(data["results"]) > 0
    top = data["results"][0]
    assert top["rank"] == 1
    assert "score" in top
    assert len(top["vals"]) == 5
    print(f"[OK] /api/v1/analogs/search for Moon passed: Top candidate {top['name']} (score {top['score']})")

def test_search_analogs_mars():
    req = {
        "planet": "mars",
        "lat": 18.38,
        "lon": 77.58,
        "features": ["Elevation", "Slope", "Roughness", "Temperature"]
    }
    r = client.post("/api/v1/analogs/search", json=req)
    assert r.status_code == 200
    data = r.json()
    assert data["demo"] is False
    assert len(data["results"]) > 0
    top = data["results"][0]
    print(f"[OK] /api/v1/analogs/search for Mars passed: Top candidate {top['name']} (score {top['score']})")

def test_region_workflow():
    reg_req = {
        "planet": "mars",
        "name": "Jezero Crater Exploration Site",
        "lat": 18.38,
        "lon": 77.58
    }
    r = client.post("/api/v1/regions", json=reg_req)
    assert r.status_code == 200
    reg = r.json()
    reg_id = reg["id"]
    assert "Elevation" in reg["extracted_features"]

    r2 = client.get(f"/api/v1/regions/{reg_id}")
    assert r2.status_code == 200
    assert r2.json()["id"] == reg_id
    print("[OK] /api/v1/regions workflow passed")

if __name__ == "__main__":
    test_health()
    test_planets()
    test_datasets()
    test_layers()
    test_search_analogs_moon()
    test_search_analogs_mars()
    test_region_workflow()
    print("\n[ALL BACKEND API TESTS PASSED SUCCESSFULLY!]")
