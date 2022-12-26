"""Config flow for FreeAir component.

Used by UI to setup integration.
"""
import voluptuous as vol
from homeassistant import config_entries

from .const import CONF_PASSWORD, CONF_SERIAL_NO, DOMAIN


class FreeAirConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore
    """Component config flow."""

    VERSION = 1

    def __init__(self):
        self._source_name = None

    async def async_step_user(self, user_input=None):
        """Handle the start of the config flow.

        Called after integration has been selected in the 'add integration
        UI'. The user_input is set to None in this case. We will open a config
        flow form then.
        This function is also called if the form has been submitted. user_input
        contains a dict with the user entered values then.
        """
        if user_input is None:
            data_schema = vol.Schema(
                {vol.Required(CONF_SERIAL_NO): str, vol.Required(CONF_PASSWORD): str},
            )
            return self.async_show_form(step_id="user", data_schema=data_schema)

        serial_no = user_input[CONF_SERIAL_NO]

        # create config entry
        unique_id = f"{DOMAIN} {serial_no}"
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        title = f"FreeAir S/N: {serial_no}"
        return self.async_create_entry(
            title=title,
            data={CONF_SERIAL_NO: serial_no, CONF_PASSWORD: user_input[CONF_PASSWORD]},
        )
