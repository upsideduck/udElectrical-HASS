"""Sensor platform for UDElectrical integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    RestoreEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import UdelectricalCoordinator

SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="unit_price",
        name="Average Units Price",
        icon="mdi:flash",
        native_unit_of_measurement="SEK/kWh",
        suggested_display_precision=3,
    ),
    SensorEntityDescription(
        key="actual_price",
        name="Average Actual Price",
        icon="mdi:flash",
        native_unit_of_measurement="SEK/kWh",
        suggested_display_precision=3,
    ),
    SensorEntityDescription(
        key="consumption",
        name="Consumption",
        icon="mdi:flash",
        native_unit_of_measurement="kWh",
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="saved",
        name="Saved",
        icon="mdi:cash-plus",
        native_unit_of_measurement="SEK",
        suggested_display_precision=2,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up UDElectrical sensors from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    if entry.entry_id not in hass.data[DOMAIN]:
        api = entry.runtime_data
        coordinator = UdelectricalCoordinator(hass, api, entry)
        await coordinator.async_config_entry_first_refresh()
        hass.data[DOMAIN][entry.entry_id] = coordinator
    else:
        coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        UDElectricalSensor(entry, coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class UDElectricalSensor(
    CoordinatorEntity[UdelectricalCoordinator], RestoreEntity, SensorEntity
):
    """Representation of a UDElectrical sensor entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        coordinator: UdelectricalCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the UDElectrical sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
        }
        self._restored_value = None
        self._attr_native_value = None

    async def async_added_to_hass(self) -> None:
        """Restore state on startup."""
        await super().async_added_to_hass()

        # First try to get current value from coordinator
        if self.coordinator.data and isinstance(self.coordinator.data, dict):
            self._attr_native_value = self.coordinator.data.get(
                self.entity_description.key
            )

        # If no current value, try to restore last state
        if self._attr_native_value is None:
            last_state = await self.async_get_last_state()
            if last_state is not None and last_state.state not in (
                None,
                "unknown",
                "unavailable",
            ):
                try:
                    self._attr_native_value = float(last_state.state)
                except (ValueError, TypeError):
                    self._attr_native_value = last_state.state

        self.async_write_ha_state()

    def _convert_to_float(self, value: str | float | None) -> float | None:
        """Convert a value to float, returning None if conversion fails."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        # Always try coordinator data first
        if self.coordinator.data and isinstance(self.coordinator.data, dict):
            if self.entity_description.key == "saved":
                # Calculate the difference between unit_price and actual_price
                unit_price = self._convert_to_float(
                    self.coordinator.data.get("unit_price")
                )
                actual_price = self._convert_to_float(
                    self.coordinator.data.get("actual_price")
                )
                consumption = self._convert_to_float(
                    self.coordinator.data.get("consumption")
                )
                if (
                    unit_price is not None
                    and actual_price is not None
                    and consumption is not None
                ):
                    self._attr_native_value = (
                        unit_price * consumption - actual_price * consumption
                    )
                    return self._attr_native_value
            else:
                value = self._convert_to_float(
                    self.coordinator.data.get(self.entity_description.key)
                )
                if value is not None:
                    self._attr_native_value = value
                    return self._attr_native_value

        # Fall back to stored value if available
        if isinstance(self._attr_native_value, (int, float)):
            return float(self._attr_native_value)
        return None
