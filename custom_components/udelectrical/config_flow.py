"""Config flow for UDElectrical integration."""

from __future__ import annotations
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST

from .api import UdelectricalApi, CannotConnect, InvalidAuth
from .const import DOMAIN

CONF_API_KEY = "api_key"


class UDElectricalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for UDElectrical."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            api_key = user_input[CONF_API_KEY]
            try:
                api = UdelectricalApi(self.hass, host, api_key)
                authenticated = await api.authenticate()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            else:
                if not authenticated:
                    errors["base"] = "invalid_auth"
                else:
                    await self.async_set_unique_id(f"udelectrical_{host}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=host,
                        data={CONF_HOST: host, CONF_API_KEY: api_key},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle re-authentication with updated credentials."""
        errors = {}
        host = self.context.get("host") or self.context.get("unique_id")
        if user_input is not None and host:
            api_key = user_input[CONF_API_KEY]
            try:
                api = UdelectricalApi(self.hass, str(host), api_key)
                authenticated = await api.authenticate()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            else:
                if not authenticated:
                    errors["base"] = "invalid_auth"
                else:
                    # Find the config entry to update
                    entry = next(
                        (
                            e
                            for e in self._async_current_entries()
                            if e.unique_id == f"udelectrical_{host}"
                        ),
                        None,
                    )
                    if entry is not None:
                        return self.async_update_reload_and_abort(
                            entry,
                            data_updates={CONF_API_KEY: api_key},
                        )
                    errors["base"] = "unknown"
        return self.async_show_form(
            step_id="reauth",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )
