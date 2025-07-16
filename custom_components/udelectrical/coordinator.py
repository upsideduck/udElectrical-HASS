"""Coordinator for the udelectrical integration."""

from __future__ import annotations

import asyncio
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
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        try:
            corrutine_month = self.api._async_request(
                "GET",
                f"/api/statistics/by-month/?start_month={current_month}&end_month={current_month}",
            )
            corrutine_days = self.api._async_request(
                "GET",
                f"/api/statistics/by-day/?start_date={yesterday}&end_date={today}",
            )
            corrutine_updated = self.api._async_request(
                "GET",
                f"/api/consumption/latest",
            )
            res_month, res_days, res_latest = await asyncio.gather(
                corrutine_month, corrutine_days, corrutine_updated
            )
            output = {}
            if (
                isinstance(res_month, list)
                and res_month
                and isinstance(res_month[0], dict)
            ):
                output = {
                    **res_month[0],
                    "today": None,
                    "yesterday": None,
                    "last_updated": res_latest if res_latest else None,
                }
                if (
                    isinstance(res_days, list)
                    and len(res_days) >= 2
                    and isinstance(res_days[0], dict)
                    and isinstance(res_days[1], dict)
                ):
                    output["today"] = res_days[1]
                    output["yesterday"] = res_days[0]
                return output

            return None
        except CannotConnect as err:
            raise UpdateFailed(f"API communication error: {err}") from err
