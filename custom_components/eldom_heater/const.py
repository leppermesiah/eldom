"""Constants for eldom_heater."""
# Base component constants
from homeassistant.components.climate import DEFAULT_MAX_TEMP
from homeassistant.components.climate import DEFAULT_MIN_TEMP
from homeassistant.const import CONF_PASSWORD
from homeassistant.const import CONF_USERNAME


NAME = "eldom"
DOMAIN = "eldom"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"

ISSUE_URL = "https://github.com/pve84/eldom/issues"

# Icons
ICON = "mdi:radiator"
ICON_SETPOINT = "hass:thermometer"

# Platforms
CLIMATE = "climate"
SENSOR = "sensor"
PLATFORMS = [CLIMATE, SENSOR]


# Configuration and options
CONF_ACCESS_TOKEN = "token"
CONF_UNIQUE_ID = "uuid"
CONF_FRIENDLY_NAME = "name"
CONF_DEVICE_ID = "device_id"


# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
