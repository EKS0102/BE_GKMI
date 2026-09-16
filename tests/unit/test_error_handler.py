import asyncio
from unittest.mock import MagicMock, Mock

from fastapi import Request
from fastapi.responses import JSONResponse
import pytest

from main import global_exception_handler


def test_global_exception_handler():

    request = Mock(
        spec=Request
    )

    request.method = "GET"

    request.url.path = "/test-error"

    exception = Exception(
        "database password should not leak"
    )

    response = asyncio.run(
        global_exception_handler(
            request,
            exception
        )
    )

    assert isinstance(
        response,
        JSONResponse
    )

    assert response.status_code == 500

def test_global_exception_handler_production(monkeypatch):
    import asyncio

    from fastapi import Request
    from main import global_exception_handler

    monkeypatch.setattr("main.ENVIRONMENT", "production")

    request = MagicMock(spec=Request)
    request.method = "GET"
    request.url.path = "/test"

    exc = Exception("test internal error")

    response = asyncio.run(
        global_exception_handler(request, exc)
    )

    assert response.status_code == 500
    assert response.body == b'{"message":"Internal Server Error"}'
