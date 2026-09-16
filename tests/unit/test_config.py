import importlib
import os
import sys

import pytest


def import_config_with_env(
    monkeypatch,
    **values
):
    tracked_keys = {
        "ENVIRONMENT",
        "DATABASE_URL",
        "TEST_DATABASE_URL",
        "SECRET_KEY",
        "ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "CORS_ORIGINS",
        "LOG_DIR",
        "LOG_LEVEL",
    }

    # Bersihkan environment dari nilai .env
    for key in tracked_keys:
        monkeypatch.delenv(
            key,
            raising=False
        )

    # Cegah config.py membaca .env
    monkeypatch.setattr(
        "dotenv.load_dotenv",
        lambda *args, **kwargs: None
    )

    # Default values khusus untuk unit test
    defaults = {
        "ENVIRONMENT": "development",
        "DATABASE_URL": (
            "postgresql+psycopg://test:test@localhost:5433/test_db"
        ),
        "TEST_DATABASE_URL": (
            "postgresql+psycopg://test:test@localhost:5433/test_db"
        ),
        "SECRET_KEY": (
            "test-secret-key-for-unit-tests-only-1234567890"
        ),
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
        "CORS_ORIGINS": "",
    }

    # Set default environment
    for key, value in defaults.items():
        monkeypatch.setenv(
            key,
            value
        )

    # Override default dengan nilai dari masing-masing test.
    # Jika value=None, berarti memang ingin menguji
    # kondisi environment variable tidak ada.
    for key, value in values.items():
        if value is None:
            monkeypatch.delenv(
                key,
                raising=False
            )
        else:
            monkeypatch.setenv(
                key,
                value
            )

    # Paksa config.py di-import ulang
    sys.modules.pop(
        "config",
        None
    )

    return importlib.import_module(
        "config"
    )

# =========================================================
# ENVIRONMENT INVALID
# =========================================================

def test_config_invalid_environment(
    monkeypatch
):
    with pytest.raises(
        ValueError,
        match="ENVIRONMENT harus development atau production"
    ):
        import_config_with_env(
            monkeypatch,
            ENVIRONMENT="stagingg"
        )


# =========================================================
# DATABASE URL WAJIB
# =========================================================

def test_config_missing_database_url(
    monkeypatch
):
    with pytest.raises(
        ValueError,
        match="DATABASE_URL belum diset"
    ):
        import_config_with_env(
            monkeypatch,
            ENVIRONMENT="development",
            DATABASE_URL=None
        )


# =========================================================
# TEST DATABASE URL WAJIB
# =========================================================

def test_config_missing_test_database_url(
    monkeypatch
):
    with pytest.raises(
        ValueError,
        match="TEST_DATABASE_URL belum diset"
    ):
        import_config_with_env(
            monkeypatch,
            ENVIRONMENT="development",
            TEST_DATABASE_URL=None
        )


# =========================================================
# SECRET KEY WAJIB
# =========================================================

def test_config_missing_secret_key(
    monkeypatch
):
    with pytest.raises(
        ValueError,
        match="SECRET_KEY belum diset"
    ):
        import_config_with_env(
            monkeypatch,
            ENVIRONMENT="development",
            SECRET_KEY=None
        )


# =========================================================
# PRODUCTION SECRET TERLALU PENDEK
# =========================================================

def test_config_production_secret_too_short(
    monkeypatch
):
    with pytest.raises(
        ValueError,
        match="SECRET_KEY production tidak aman"
    ):
        import_config_with_env(
            monkeypatch,
            ENVIRONMENT="production",
            SECRET_KEY="short-secret",
            CORS_ORIGINS="https://example.com"
        )


# =========================================================
# PRODUCTION SECRET YOUR_
# =========================================================

def test_config_production_placeholder_secret(
    monkeypatch
):
    with pytest.raises(
        ValueError,
        match="SECRET_KEY production tidak aman"
    ):
        import_config_with_env(
            monkeypatch,
            ENVIRONMENT="production",
            SECRET_KEY="YOUR_SECRET_KEY_12345678901234567890",
            CORS_ORIGINS="https://example.com"
        )


# =========================================================
# PRODUCTION SECRET DOCKER DEVELOPMENT
# =========================================================

def test_config_production_docker_secret(
    monkeypatch
):
    with pytest.raises(
        ValueError,
        match="SECRET_KEY production tidak aman"
    ):
        import_config_with_env(
            monkeypatch,
            ENVIRONMENT="production",
            SECRET_KEY=(
                "docker-development-"
                "secret-key-change-this-later-123456789"
            ),
            CORS_ORIGINS="https://example.com"
        )


# =========================================================
# PRODUCTION CORS WAJIB
# =========================================================

def test_config_production_missing_cors(
    monkeypatch
):
    with pytest.raises(
        ValueError,
        match="CORS_ORIGINS wajib diset pada production"
    ):
        import_config_with_env(
            monkeypatch,
            ENVIRONMENT="production",
            SECRET_KEY=(
                "A9fK7mQ2xR8vN4pL6sT1yW3zE5cH7jU9"
            ),
            CORS_ORIGINS=""
        )


# =========================================================
# PRODUCTION CONFIG VALID
# =========================================================

def test_config_production_valid(
    monkeypatch
):
    config = import_config_with_env(
        monkeypatch,
        ENVIRONMENT="production",
        SECRET_KEY=(
            "A9fK7mQ2xR8vN4pL6sT1yW3zE5cH7jU9"
        ),
        CORS_ORIGINS="https://frontend.example.com"
    )

    assert config.ENVIRONMENT == "production"

    assert config.CORS_ORIGINS == [
        "https://frontend.example.com"
    ]

def test_production_requires_cors_origins(monkeypatch):
    import importlib

    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: None)

    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://test:test@localhost:5432/test"
    )
    monkeypatch.setenv(
        "TEST_DATABASE_URL",
        "postgresql://test:test@localhost:5432/test"
    )
    monkeypatch.setenv(
        "SECRET_KEY",
        "test-secret-key-that-is-at-least-32-characters-long"
    )
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    with pytest.raises(
        ValueError,
        match="CORS_ORIGINS wajib diset pada production"
    ):
        import config
        importlib.reload(config)

def test_development_uses_default_cors_origins(monkeypatch):
    import importlib

    monkeypatch.setattr(
        "dotenv.load_dotenv",
        lambda *args, **kwargs: None
    )

    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://test:test@localhost:5432/test"
    )
    monkeypatch.setenv(
        "TEST_DATABASE_URL",
        "postgresql://test:test@localhost:5432/test"
    )
    monkeypatch.setenv(
        "SECRET_KEY",
        "test-secret-key-that-is-at-least-32-characters-long"
    )
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    import config
    config = importlib.reload(config)

    assert config.CORS_ORIGINS_RAW == (
        "http://localhost:3000,"
        "http://localhost:5173"
    )

    assert config.CORS_ORIGINS == [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
