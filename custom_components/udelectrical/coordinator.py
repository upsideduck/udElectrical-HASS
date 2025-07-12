"""Coordinator for the udelectrical integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

from .api import UdelectricalApi, CannotConnect
from .const import DOMAIN
from datetime import datetime

_LOGGER = logging.getLogger(__name__)


from typing import Any


class UdelectricalCoordinator(DataUpdateCoordinator[dict[str, Any] | None]):
    """Coordinator for udelectrical data updates."""

    def __init__(
        self, hass: HomeAssistant, api: UdelectricalApi, entry: ConfigEntry
    ) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=20),
            config_entry=entry,
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any] | None:
        """Fetch data from the udelectrical API."""
        current_month = datetime.now().strftime("%Y-%m")
        try:
            res = await self.api._async_request(
                "GET",
                f"/api/statistics/by-month/?start_month={current_month}&end_month={current_month}",
            )
            if isinstance(res, list) and res and isinstance(res[0], dict):
                return res[0]
            return None
        except CannotConnect as err:
            raise UpdateFailed(f"API communication error: {err}") from err
