import asyncio
from unittest.mock import Mock

from fastapi import Request
from fastapi.responses import JSONResponse

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