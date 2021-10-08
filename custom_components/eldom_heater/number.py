"""Switch platform for eldom_heater."""
from homeassistant.components.number import NumberEntity

from .const import DEFAULT_NAME, DOMAIN, ICON, NUMBER
from .entity import EldomEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup number platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([EldomNumber(coordinator, entry)])


class EldomNumber(EldomEntity, NumberEntity):
    """eldom_heater num,ber class."""

    async def async_set_value(self, value: float) -> None:
        """Update the current value."""
        data = self.coordinator.data
        data["TSet"] = int(value)
        data["Req"] = "SetParams"
        await self.coordinator.api.async_set_parameter(data)
        await self.coordinator.async_request_refresh()

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{DEFAULT_NAME}_{NUMBER}"

    @property
    def icon(self):
        """Return the icon of this switch."""
        return ICON

    @property
    def step(self):
        """Set stepsize"""
        return 1

    @property
    def min_value(self) -> float:
        return 15

    @property
    def max_value(self) -> float:
        return 25

    @property
    def value(self):
        """Get the value of the setpoint."""
        tSet = self.coordinator.data["TSet"]
        tSet = f"{tSet[0:2]}.{tSet[2:3]}"
        return tSet
