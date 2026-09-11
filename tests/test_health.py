from unittest.mock import patch

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
    
# =========================================================
# HEALTH TANPA TOKEN
# =========================================================

def test_health_does_not_require_authentication(client):
    response = client.get("/health")

    assert response.status_code == 200


# =========================================================
# READINESS TANPA TOKEN
# =========================================================

def test_readiness_does_not_require_authentication(client):
    response = client.get("/health/ready")

    assert response.status_code == 200


# =========================================================
# SECURITY HEADERS PADA HEALTH
# =========================================================

def test_health_has_security_headers(client):
    response = client.get("/health")

    assert response.headers[
        "X-Content-Type-Options"
    ] == "nosniff"

    assert response.headers[
        "X-Frame-Options"
    ] == "DENY"

    assert response.headers[
        "Referrer-Policy"
    ] == "strict-origin-when-cross-origin"
    
# =========================================================
# READINESS - DATABASE GAGAL
# =========================================================

def test_readiness_check_database_failure(client):
    with patch(
        "main.engine.connect",
        side_effect=Exception("database unavailable")
    ):
        response = client.get(
            "/health/ready"
        )

    assert response.status_code == 503

    assert response.json() == {
        "status": "not_ready"
    }