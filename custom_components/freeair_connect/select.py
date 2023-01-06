import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import CONF_SERIAL_NO, DOMAIN, UPDATE_SENSORS_SIGNAL

_LOGGER = logging.getLogger(__name__)


MODES = {
    "comfort": 1,
    "sleep": 2,
    "turbo": 3,
    "turbo_cool": 4,
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up platform for a new integration.

    Called by the HA framework after async_setup_platforms has been called
    during initialization of a new integration.
    """
    shell = hass.data[DOMAIN][config_entry.data[CONF_SERIAL_NO]]
    unique_id = config_entry.unique_id

    entities = []

    entities.append(OperationModeSelectEntity(hass, unique_id, shell))

    async_add_entities(entities)


class OperationModeSelectEntity(SelectEntity):
    """Home Assistant sensor containing FreeAir data."""

    def __init__(self, hass, unique_id, shell):
        self._hass = hass
        self._shell = shell
        self._id = "operation_mode"

        # entity attributes
        self._attr_device_info = shell.device_info
        self._attr_unique_id = f"{unique_id}_{self._id}"
        self._attr_name = self._id

        self._attr_translation_key = (self._id,)
        self._attr_options = list(MODES.keys())

        self._attr_has_entity_name = True
        self._attr_should_poll = False

        if self._shell.data is not None:
            self._update_sensor()

        async_dispatcher_connect(hass, UPDATE_SENSORS_SIGNAL, self._update_sensor)

    @callback
    def _update_sensor(self):
        """Update the value and the extra-state-attributes of the entity."""
        fad = self._shell.data

        attributes = {"timestamp": getattr(fad, "timestamp", None)}
        self._attr_extra_state_attributes = attributes

        self._attr_assumed_state = getattr(fad, f"is_{self._id}_assumed", False)
        self._attr_current_option = getattr(fad, f"{self._id}_str", None)

        if self.hass is not None:
            self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self._shell.set_operation_mode(MODES.get(option, 1))
        self._update_sensor()
