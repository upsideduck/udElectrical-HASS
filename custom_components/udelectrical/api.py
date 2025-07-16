"""API client for udelectrical."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = __import__("logging").getLogger(__name__)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect to the UDElectrical API."""

    def __init__(self, message: str = "Cannot connect to the UDElectrical API") -> None:
        """Initialize CannotConnect with an optional message."""
        super().__init__(message)


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid authentication for the UDElectrical API."""

    def __init__(
        self, message: str = "Invalid authentication for the UDElectrical API"
    ) -> None:
        """Initialize InvalidAuth with an optional message."""
        super().__init__(message)


class UdelectricalApi:
    """API client for udelectrical."""

    def __init__(
        self, hass: HomeAssistant, host: str, api_key: str, ssl: bool = True
    ) -> None:
        """Initialize API client."""
        self._session = async_get_clientsession(hass)
        self._host = host
        self._api_key = api_key
        self._ssl = ssl
        self._headers = {
            "X-API-Key": api_key,
            "Accept": "application/json",
        }

    async def _async_request(
        self, method: str, url: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Make an API request."""
        try:
            async with asyncio.timeout(10):
                protocol = "https" if self._ssl else "http"
                response = await self._session.request(
                    method,
                    f"{protocol}://{self._host}{url}",
                    **kwargs,
                    headers=self._headers,
                )

                _LOGGER.debug(
                    "udelectrical API response [%s] %s: %s",
                    response.status,
                    url,
                    await response.text(),
                )
                if response.status == 401:
                    raise InvalidAuth("Invalid API key")

                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientError as err:
            raise CannotConnect from err
        except TimeoutError as err:
            raise CannotConnect("Timeout connecting to API") from err

    async def authenticate(self) -> bool:
        """Test if we can authenticate with the host."""
        try:
            await self._async_request("GET", "/api/status")
        except InvalidAuth:
            return False
        except CannotConnect:
            return False
        else:
            return True
