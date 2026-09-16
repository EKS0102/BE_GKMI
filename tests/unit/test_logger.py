import importlib

import pytest


def test_invalid_log_level(monkeypatch):
    monkeypatch.setattr(
        "dotenv.load_dotenv",
        lambda *args, **kwargs: None
    )

    monkeypatch.setenv("LOG_LEVEL", "INVALID")

    with pytest.raises(
        ValueError,
        match="LOG_LEVEL harus salah satu dari:"
    ):
        import logger
        importlib.reload(logger)