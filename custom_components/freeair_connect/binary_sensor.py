import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import CONF_SERIAL_NO, DOMAIN, UPDATE_SENSORS_SIGNAL

_LOGGER = logging.getLogger(__name__)


class SensorSpec:
    def __init__(self, id, device_class=None):
        self._id = id
        self._device_class = device_class

    @property
    def id(self):
        return self._id

    @property
    def device_class(self):
        return self._device_class


ENTITY_LIST = [
    SensorSpec(
        id="humidity_reduction_mode",
    ),
    SensorSpec(
        id="fan_lim_2nd_room",
    ),
    SensorSpec(
        id="b_2nd_room_only_20",
    ),
    SensorSpec(
        id="summer_cooling",
    ),
    SensorSpec(
        id="filter_supply_full",
    ),
    SensorSpec(
        id="filter_extract_full",
    ),
    SensorSpec(
        id="deicing",
    ),
]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up platform for a new integration.

    Called by the HA framework after async_setup_platforms has been called
    during initialization of a new integration.
    """
    shell = hass.data[DOMAIN][config_entry.data[CONF_SERIAL_NO]]
    unique_id = config_entry.unique_id

    entities = []

    for spec in ENTITY_LIST:
        entities.append(FreeAirBinarySensorEntity(hass, unique_id, shell, spec))

    async_add_entities(entities)


class FreeAirBinarySensorEntity(BinarySensorEntity):
    """Home Assistant sensor containing FreeAir data."""

    def __init__(self, hass, unique_id, shell, spec):
        self._hass = hass
        self._shell = shell
        self._spec = spec

        # entity attributes
        self._attr_device_info = shell.device_info
        self._attr_unique_id = f"{unique_id}_{spec.id}"
        self._attr_name = spec.id
        self._attr_device_class = spec.device_class
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

        self._attr_is_on = getattr(fad, self._spec.id, None)

        if self.hass is not None:
            self.async_write_ha_state()
