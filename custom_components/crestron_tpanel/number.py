"""Number platform for Crestron Touch Panel brightness."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CrestronPanelCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Crestron panel brightness from a config entry."""
    coordinator: CrestronPanelCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([CrestronPanelBrightness(coordinator, entry)])


class CrestronPanelBrightness(CoordinatorEntity[CrestronPanelCoordinator], NumberEntity):
    """Representation of Crestron panel brightness control."""

    _attr_has_entity_name = True
    _attr_name = "Brightness"
    _attr_icon = "mdi:brightness-6"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator: CrestronPanelCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the brightness control."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.data[CONF_NAME]}_brightness"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data[CONF_NAME],
            "manufacturer": "Crestron",
            "model": "TSW-1070",
        }

    @property
    def native_value(self) -> float:
        """Return the current brightness."""
        return self.coordinator.data.get("brightness", 100)

    async def async_set_native_value(self, value: float) -> None:
        """Set the brightness."""
        await self.coordinator.async_set_brightness(int(value))
