import logging

from homeassistant.components.number import NumberEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import CONF_SERIAL_NO, DOMAIN, UPDATE_SENSORS_SIGNAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up platform for a new integration.

    Called by the HA framework after async_setup_platforms has been called
    during initialization of a new integration.
    """
    shell = hass.data[DOMAIN][config_entry.data[CONF_SERIAL_NO]]
    unique_id = config_entry.unique_id

    entities = []

    entities.append(ComfortLevelNumberEntity(hass, unique_id, shell))

    async_add_entities(entities)


class ComfortLevelNumberEntity(NumberEntity):
    """Home Assistant sensor containing FreeAir data."""

    def __init__(self, hass, unique_id, shell):
        self._hass = hass
        self._shell = shell
        self._id = "comfort_level"

        # entity attributes
        self._attr_device_info = shell.device_info
        self._attr_unique_id = f"{unique_id}_{self._id}"
        self._attr_name = self._id
        self._attr_native_min_value = 1
        self._attr_native_max_value = 5
        self._attr_native_step = 1

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
        self._attr_native_value = getattr(fad, self._id, None)

        if self.hass is not None:
            self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        await self._shell.set_comfort_level(int(value))
        self._update_sensor()
