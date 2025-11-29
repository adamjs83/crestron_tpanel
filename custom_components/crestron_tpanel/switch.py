"""Switch platform for Crestron Touch Panel."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
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
    """Set up Crestron panel switch from a config entry."""
    coordinator: CrestronPanelCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([CrestronPanelPowerSwitch(coordinator, entry)])


class CrestronPanelPowerSwitch(CoordinatorEntity[CrestronPanelCoordinator], SwitchEntity):
    """Representation of a Crestron panel power switch."""

    _attr_has_entity_name = True
    _attr_name = "Power"
    _attr_icon = "mdi:tablet"

    def __init__(
        self,
        coordinator: CrestronPanelCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.data[CONF_NAME]}_power"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data[CONF_NAME],
            "manufacturer": "Crestron",
            "model": "TSW-1070",
        }

    @property
    def is_on(self) -> bool:
        """Return true if the panel is on (not in standby)."""
        return self.coordinator.data.get("is_on", True)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the panel (exit standby)."""
        await self.coordinator.async_turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the panel (enter standby)."""
        await self.coordinator.async_turn_off()
