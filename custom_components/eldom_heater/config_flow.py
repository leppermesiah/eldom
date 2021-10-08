"""Adds config flow for eldom."""
from homeassistant.const import CONF_DEVICE_ID, CONF_FRIENDLY_NAME
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import EldomApiClient
from .const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_ACCESS_TOKEN,
    CONF_UNIQUE_ID,
    DOMAIN,
    PLATFORMS,
)


class EldomHeaterHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for eldom."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            response = await self._get_credentials(
                user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            )
            token = response["id_token"]
            if token:

                response = await self._get_devices(token)
                user_input[CONF_ACCESS_TOKEN] = token
                user_input[CONF_UNIQUE_ID] = response[0]["uuid"]
                user_input[CONF_DEVICE_ID] = response[0]["pairTok"]
                user_input[CONF_FRIENDLY_NAME] = response[0]["name"]
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=user_input
                )
            else:
                self._errors["base"] = "auth"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return EldomOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
            ),
            errors=self._errors,
        )

    async def _get_credentials(self, username, password):
        """Return response if credentials is valid."""
        try:
            session = async_create_clientsession(self.hass)
            client = EldomApiClient(session, username=username, password=password)
            response = await client.async_get_token()
            return response
        except Exception:  # pylint: disable=broad-except
            pass
        return False

    async def _get_devices(self, token):
        """Return devices"""
        try:
            session = async_create_clientsession(self.hass)
            client = EldomApiClient(session, token=token)
            response = await client.async_get_devices()
            return response
        except Exception:  # pylint: disable=broad-except
            pass
        return False


class EldomOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options handler for eldom."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(x, default=self.options.get(x, True)): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_USERNAME), data=self.options
        )
