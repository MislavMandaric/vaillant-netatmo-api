"""Module containing a BaseClient for the Netatmo API."""

from __future__ import annotations

from httpx import AsyncClient, Auth
from tenacity import retry, retry_if_exception_type, stop_after_attempt, stop_after_delay, wait_random_exponential

from .errors import RetryableException, client_error_handler
from .time import now

_API_HOST = "https://api.netatmo.com/"


class BaseClient:
    """
    Base client for making HTTP requests to the Netatmo API.

    Uses the constructor provided AsyncClient and Auth from httpx to make authenticated requests. The provided AsyncClient should be used as a singleton for making all requests to allow efficient connection pool management.
    """

    def __init__(
        self,
        client: AsyncClient,
        auth: Auth,
    ) -> None:
        """
        Create new base client instance.

        Uses the provided parameters when making API calls towards the Netatmo API.
        """

        self._client = client
        self._auth = auth

    @retry(
        retry=retry_if_exception_type(RetryableException),
        stop=(stop_after_delay(300) | stop_after_attempt(10)),
        wait=wait_random_exponential(multiplier=1, max=30),
        reraise=True,
    )
    async def _post(self, path: str, data: dict) -> dict:
        """
        Makes post request using the underlying httpx AsyncClient, with the defaut timeout of 15s.
        
        In case of retryable exceptions, requests are retryed for up to 10 times or 5 minutes.
        """

        with client_error_handler():
            resp = await self._client.post(
                f"{_API_HOST}{path}",
                headers={"Cache-Control": "no-cache"},
                params={"ts": round(now().timestamp())},
                data=data,
                auth=self._auth,
                timeout=15.0,
            )

            resp.raise_for_status()
            return resp.json()