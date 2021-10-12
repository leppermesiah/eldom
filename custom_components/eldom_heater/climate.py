"""Support for Eldom wifi-enabled home heaters."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_WHOLE,
    TEMP_CELSIUS,
)
from .const import DOMAIN, DEFAULT_NAME, DEFAULT_MIN_TEMP, DEFAULT_MAX_TEMP, CLIMATE
from .entity import EldomEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([EldomClimate(coordinator, entry)])


class EldomClimate(EldomEntity, ClimateEntity):
    """Representation of a heater."""

    _attr_hvac_modes = [HVAC_MODE_HEAT, HVAC_MODE_OFF]
    _attr_max_temp = DEFAULT_MAX_TEMP
    _attr_min_temp = DEFAULT_MIN_TEMP
    _attr_supported_features = SUPPORT_TARGET_TEMPERATURE
    _attr_target_temperature_step = PRECISION_WHOLE
    _attr_temperature_unit = TEMP_CELSIUS

    @property
    def name(self) -> str:
        """Return the name of the device, if any."""
        return f"{DEFAULT_NAME}_{CLIMATE}"

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        operation = self.coordinator.data["Operation"]
        if operation == "16":
            return HVAC_MODE_HEAT
        return HVAC_MODE_OFF

    @property
    def icon(self) -> str:
        """Return nice icon for heater."""
        if self.hvac_mode == HVAC_MODE_HEAT:
            return "mdi:radiator"
        return "mdi:radiator-off"

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set hvac mode."""
        if hvac_mode == HVAC_MODE_HEAT:
            setpoint = self.coordinator.data["TSet"]
            setpoint = f"{setpoint[0:2]}.{setpoint[2:3]}"
            temperature = max(self.min_temp, int(float(setpoint)), self.min_temp)
            await self.coordinator.api.async_turn_on_or_off("On")
            data = self.coordinator.data
            data["TSet"] = int(temperature)
            data["Req"] = "SetParams"
            await self.coordinator.api.async_set_parameter(data)
        elif hvac_mode == HVAC_MODE_OFF:
            await self.coordinator.api.async_turn_on_or_off("Off")
        else:
            return
        await self.coordinator.async_request_refresh()

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        temperature = self.coordinator.data["T"]
        temperature = f"{temperature[0:2]}.{temperature[2:3]}"
        return int(float(temperature))

    @property
    def target_temperature(self) -> int | None:
        """Return the temperature we try to reach."""
        setpoint = self.coordinator.data["TSet"]
        setpoint = f"{setpoint[0:2]}.{setpoint[2:3]}"
        return int(float(setpoint))

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        data = self.coordinator.data
        data["TSet"] = int(temperature)
        data["Req"] = "SetParams"
        await self.coordinator.api.async_set_parameter(data)
        await self.coordinator.async_request_refresh()

    # async def async_update(self) -> None:
    #     """Get the latest data."""
    #     for room in await self._adax_data_handler.get_rooms():
    #         if room["id"] == self._heater_data["id"]:
    #             self._heater_data = room
    #             return