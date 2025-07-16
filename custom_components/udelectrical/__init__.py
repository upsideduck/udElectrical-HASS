"""The udelectrical integration."""

from __future__ import annotations

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
)
from homeassistant.const import CONF_API_KEY, CONF_HOST, Platform
from homeassistant.core import HomeAssistant

from .api import CannotConnect, UdelectricalApi
from .const import CONF_SSL

_PLATFORMS: list[Platform] = [Platform.SENSOR]

type UdelectricalConfigEntry = ConfigEntry[UdelectricalApi]


async def async_setup_entry(
    hass: HomeAssistant, entry: UdelectricalConfigEntry
) -> bool:
    """Set up udelectrical from a config entry."""
    api = UdelectricalApi(
        hass=hass,
        host=entry.data[CONF_HOST],
        api_key=entry.data[CONF_API_KEY],
        ssl=entry.data.get(
            CONF_SSL, True
        ),  # Default to True for backwards compatibility
    )

    try:
        if not await api.authenticate():
            raise ConfigEntryAuthFailed("Invalid API key")
    except CannotConnect as err:
        raise ConfigEntryNotReady from err

    entry.runtime_data = api

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: UdelectricalConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
