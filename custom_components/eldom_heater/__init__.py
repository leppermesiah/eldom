"""
Custom integration to integrate eldom with Home Assistant.

For more details about this integration, please refer to
https://github.com/pve84/eldom
"""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from .api import EldomApiClient
from .const import CONF_ACCESS_TOKEN
from .const import CONF_DEVICE_ID
from .const import CONF_PASSWORD
from .const import CONF_UNIQUE_ID
from .const import CONF_USERNAME
from .const import DOMAIN
from .const import PLATFORMS
from .const import STARTUP_MESSAGE

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    token = entry.data.get(CONF_ACCESS_TOKEN)
    uuid = entry.data.get(CONF_UNIQUE_ID)
    deviceId = entry.data.get(CONF_DEVICE_ID)

    session = async_get_clientsession(hass)
    client = EldomApiClient(session=session, token=token, uuid=uuid, deviceId=deviceId)

    coordinator = EldomDataUpdateCoordinator(hass, client=client)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

    entry.add_update_listener(async_reload_entry)
    return True


class EldomDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: EldomApiClient,
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Get Status"""
        try:
            status = await self.api.async_get_status()
            parameters = await self.api.async_get_parameters()
            response = {
                "T": status["T"],
                "Operation": status["Operation"],
                "TSet": parameters["TSet"],
                "ID": parameters["ID"],
                "Lock": parameters["Lock"],
                "Rate1": parameters["Rate1"],
                "Rate2": parameters["Rate2"],
                "Antifrost": parameters["Antifrost"],
                "AutoTimeSet": parameters["AutoTimeSet"],
                "SystemSettings": parameters["SystemSettings"],
                "CRC": "00000000",
                "CID": "1",
            }
            return response
        except Exception as exception:
            raise UpdateFailed() from exception


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
