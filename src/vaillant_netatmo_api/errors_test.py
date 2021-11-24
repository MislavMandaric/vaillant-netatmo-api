import httpx
import pytest

from datetime import timedelta

from vaillant_netatmo_api.errors import ApiException, NetworkException, RequestBackoffException, RequestClientException, RequestException, RequestServerException, RequestUnauthorizedException, client_error_handler, NetworkTimeoutException


@pytest.mark.asyncio
class TestErrors:
    async def test_client_error_handler__timeout_exception__raises_network_timeout_exception(self):
        request = httpx.Request("POST", "https://api.netatmo.com/")

        with pytest.raises(NetworkTimeoutException):
            with client_error_handler():
                raise httpx.TimeoutException("test", request=request)

    async def test_client_error_handler__network_error__raises_network_exception(self):
        request = httpx.Request("POST", "https://api.netatmo.com/")

        with pytest.raises(NetworkException):
            with client_error_handler():
                raise httpx.NetworkError("test", request=request)

    async def test_client_error_handler__http_status_error_401__raises_request_unauthorized_exception(self):
        request = httpx.Request("POST", "https://api.netatmo.com/")

        response = httpx.Response(401, request=request)
        response.elapsed = timedelta()

        with pytest.raises(RequestUnauthorizedException):
            with client_error_handler():
                raise httpx.HTTPStatusError("test", request=request, response=response)

    async def test_client_error_handler__http_status_error_403__raises_request_unauthorized_exception(self):
        request = httpx.Request("POST", "https://api.netatmo.com/")

        response = httpx.Response(403, request=request)
        response.elapsed = timedelta()

        with pytest.raises(RequestUnauthorizedException):
            with client_error_handler():
                raise httpx.HTTPStatusError("test", request=request, response=response)

    async def test_client_error_handler__http_status_error_429__raises_request_backoff_exception(self):
        request = httpx.Request("POST", "https://api.netatmo.com/")

        response = httpx.Response(429, request=request)
        response.elapsed = timedelta()

        with pytest.raises(RequestBackoffException):
            with client_error_handler():
                raise httpx.HTTPStatusError("test", request=request, response=response)

    async def test_client_error_handler__http_status_error_400__raises_request_client_exception(self):
        request = httpx.Request("POST", "https://api.netatmo.com/")

        response = httpx.Response(400, request=request)
        response.elapsed = timedelta()

        with pytest.raises(RequestClientException):
            with client_error_handler():
                raise httpx.HTTPStatusError("test", request=request, response=response)

    async def test_client_error_handler__http_status_error_500__raises_request_server_exception(self):
        request = httpx.Request("POST", "https://api.netatmo.com/")

        response = httpx.Response(500, request=request)
        response.elapsed = timedelta()

        with pytest.raises(RequestServerException):
            with client_error_handler():
                raise httpx.HTTPStatusError("test", request=request, response=response)

    async def test_client_error_handler__http_status_error_600__raises_request_exception(self):
        request = httpx.Request("POST", "https://api.netatmo.com/")

        response = httpx.Response(600, request=request)
        response.elapsed = timedelta()

        with pytest.raises(RequestException):
            with client_error_handler():
                raise httpx.HTTPStatusError("test", request=request, response=response)


@pytest.mark.asyncio
class TestApiException:
    async def test_init__with_access_token_and_password_content__sanitizes_request_content(self):
        request = httpx.Request("POST", "https://api.netatmo.com/", content="a=b&access_token=nesto&c=d&password=drugo")

        response = httpx.Response(500, request=request, content="response")
        response.elapsed = timedelta()

        with pytest.raises(ApiException) as ex:
            raise ApiException("test", request=request, response=response)
        
        assert ex.value.request["body"] == b"a=b&access_token=<FILTERED>&c=d&password=<FILTERED>&"