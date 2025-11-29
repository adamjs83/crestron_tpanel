"""Data coordinator for Crestron Touch Panel."""
from __future__ import annotations

import asyncio
import logging
import re
from datetime import timedelta
from typing import Any

import asyncssh

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CMD_BRIGHTNESS_GET,
    CMD_BRIGHTNESS_SET,
    CMD_STANDBY_OFF,
    CMD_STANDBY_ON,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# Regex to parse brightness response: "Current LCD brightness level: 50%"
BRIGHTNESS_REGEX = re.compile(r"(?:Current|New) LCD brightness level:\s*(\d+)%")


class CrestronPanelCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage Crestron panel data."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        username: str,
        password: str,
        name: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Crestron Panel {name}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.panel_name = name
        
        # Track state locally since we can't query standby status
        self._is_on: bool = True
        self._brightness: int = 100

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the panel."""
        try:
            brightness = await self._get_brightness()
            if brightness is not None:
                self._brightness = brightness
                # If we can read brightness, panel is likely awake
                self._is_on = True
            
            return {
                "brightness": self._brightness,
                "is_on": self._is_on,
            }
        except Exception as err:
            # If we can't connect, panel might be in standby or offline
            _LOGGER.debug("Failed to get brightness from %s: %s", self.host, err)
            return {
                "brightness": self._brightness,
                "is_on": self._is_on,
            }

    async def _run_ssh_command(self, command: str) -> str | None:
        """Run an SSH command on the panel."""
        try:
            async with asyncssh.connect(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                known_hosts=None,  # Disable host key checking
                connect_timeout=10,
            ) as conn:
                result = await conn.run(command, check=False, timeout=10)
                return result.stdout
        except asyncssh.Error as err:
            _LOGGER.error("SSH error connecting to %s: %s", self.host, err)
            raise UpdateFailed(f"SSH error: {err}") from err
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout connecting to %s", self.host)
            raise UpdateFailed(f"Connection timeout to {self.host}") from err
        except Exception as err:
            _LOGGER.error("Unexpected error connecting to %s: %s", self.host, err)
            raise UpdateFailed(f"Unexpected error: {err}") from err

    async def _get_brightness(self) -> int | None:
        """Get current brightness level."""
        output = await self._run_ssh_command(CMD_BRIGHTNESS_GET)
        if output:
            match = BRIGHTNESS_REGEX.search(output)
            if match:
                return int(match.group(1))
        return None

    async def async_set_brightness(self, brightness: int) -> bool:
        """Set brightness level (0-100)."""
        brightness = max(0, min(100, brightness))
        command = CMD_BRIGHTNESS_SET.format(brightness)
        try:
            output = await self._run_ssh_command(command)
            if output and "brightness level" in output.lower():
                self._brightness = brightness
                await self.async_request_refresh()
                return True
            return False
        except UpdateFailed:
            return False

    async def async_turn_on(self) -> bool:
        """Wake the panel from standby."""
        try:
            output = await self._run_ssh_command(CMD_STANDBY_OFF)
            if output and "exit standby" in output.lower():
                self._is_on = True
                await self.async_request_refresh()
                return True
            # Even without expected output, assume success
            self._is_on = True
            await self.async_request_refresh()
            return True
        except UpdateFailed:
            return False

    async def async_turn_off(self) -> bool:
        """Put the panel into standby."""
        try:
            output = await self._run_ssh_command(CMD_STANDBY_ON)
            if output and "entering standby" in output.lower():
                self._is_on = False
                await self.async_request_refresh()
                return True
            # Even without expected output, assume success
            self._is_on = False
            await self.async_request_refresh()
            return True
        except UpdateFailed:
            return False

    async def async_test_connection(self) -> bool:
        """Test if we can connect to the panel."""
        try:
            brightness = await self._get_brightness()
            return brightness is not None
        except Exception:
            return False
