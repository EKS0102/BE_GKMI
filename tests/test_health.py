# =========================================================
# HEALTH CHECK
# =========================================================

def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok"
    }
    
# =========================================================
# DATABASE READINESS
# =========================================================

def test_readiness_check(client):
    response = client.get(
        "/health/ready"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ready"
    }