"""Sensor platform for eldom_heater."""
from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import ICON_SETPOINT
from .entity import EldomEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([EldomTemperatureSensor(coordinator, entry)])


class EldomTemperatureSensor(EldomEntity):
    """eldom_heater Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_temperature"

    @property
    def state(self):
        """Return the state of the sensor."""
        temp = self.coordinator.data["T"]
        temp = f"{temp[0:2]}.{temp[2:3]}"
        return temp

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON_SETPOINT

    @property
    def device_class(self):
        """Return de device class of the sensor."""
        return "temperature"

    @property
    def state_class(self):
        """Return state"""
        return "measurement"

    @property
    def native_unit_of_measurement(self):
        return "°C"

    @property
    def extra_state_attributes(self):
        """Return extra attributes"""
        return self.coordinator.data
