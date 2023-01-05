import logging

from homeassistant.components.sensor import (SensorDeviceClass, SensorEntity,
                                             SensorStateClass)
from homeassistant.const import (CONCENTRATION_PARTS_PER_MILLION, PERCENTAGE,
                                 REVOLUTIONS_PER_MINUTE,
                                 SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
                                 UnitOfPressure, UnitOfTemperature, UnitOfTime,
                                 UnitOfVolumeFlowRate)
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory

from .const import CONF_SERIAL_NO, DOMAIN, UPDATE_SENSORS_SIGNAL

_LOGGER = logging.getLogger(__name__)


class SensorSpec:
    def __init__(
        self, id, uom=None, device_class=None, state_class=None, entity_category=None
    ):
        self._id = id
        self._uom = uom
        self._device_class = device_class
        self._state_class = state_class
        self._entity_category = entity_category

    @property
    def id(self):
        return self._id

    @property
    def uom(self):
        return self._uom

    @property
    def device_class(self):
        return self._device_class

    @property
    def state_class(self):
        return self._state_class

    @property
    def entity_category(self):
        return self._entity_category


ENTITY_LIST = [
    SensorSpec(
        id="humidity_outdoor_rel",
        uom=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorSpec(
        id="humidity_extract_rel",
        uom=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorSpec(
        id="temp_supply",
        uom=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorSpec(
        id="temp_outdoor",
        uom=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorSpec(
        id="temp_exhaust",
        uom=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorSpec(
        id="temp_extract",
        uom=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorSpec(
        id="temp_virt_sup_exit",
        uom=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorSpec(
        id="co2_extract",
        uom=CONCENTRATION_PARTS_PER_MILLION,
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorSpec(
        id="air_pressure",
        uom=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorSpec(id="comfort_level"),
    SensorSpec(
        id="fan_speed",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorSpec(
        id="fan_speed_supply",
        uom=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorSpec(
        id="filter_status_supply",
    ),
    SensorSpec(
        id="fan_speed_extract",
        uom=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorSpec(
        id="filter_status_extract",
    ),
    #    SensorSpec(
    #        id="error_file_nbr",
    #        entity_category=EntityCategory.DIAGNOSTIC,
    #    ),
    #    SensorSpec(
    #        id="error_line_nbr",
    #        entity_category=EntityCategory.DIAGNOSTIC,
    #    ),
    #    SensorSpec(
    #        id="error_code",
    #        entity_category=EntityCategory.DIAGNOSTIC,
    #    ),
    SensorSpec(
        id="air_flow_avg",
        uom=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorSpec(
        id="air_flow",
        uom=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorSpec(
        id="filter_hours",
        uom=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorSpec(
        id="operating_hours",
        uom=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorSpec(
        id="rssi",
        uom=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
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
        entities.append(FreeAirSensorEntity(hass, unique_id, shell, spec))

    entities.append(ErrorStateSensorEntity(hass, unique_id, shell))
    entities.append(TestSensorEntity(hass, unique_id, shell))

    async_add_entities(entities)


class FreeAirSensorEntity(SensorEntity):
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
        self._attr_state_class = spec.state_class
        self._attr_entity_category = spec.entity_category
        self._attr_has_entity_name = True
        self._attr_should_poll = False

        self._attr_native_unit_of_measurement = spec.uom

        if self._shell.data is not None:
            self._update_sensor()

        async_dispatcher_connect(hass, UPDATE_SENSORS_SIGNAL, self._update_sensor)

    @callback
    def _update_sensor(self):
        """Update the value and the extra-state-attributes of the entity."""
        fad = self._shell.data

        attributes = {"timestamp": getattr(fad, "timestamp", None)}
        self._attr_extra_state_attributes = attributes

        self._attr_native_value = getattr(fad, self._spec.id, None)

        if self.hass is not None:
            self.async_write_ha_state()


class ErrorStateSensorEntity(SensorEntity):
    """Home Assistant sensor containing FreeAir data."""

    def __init__(self, hass, unique_id, shell):
        self._hass = hass
        self._shell = shell
        self._id = "error_state"

        # entity attributes
        self._attr_device_info = shell.device_info
        self._attr_unique_id = f"{unique_id}_{self._id}"
        self._attr_name = self._id
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
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
        attributes.update(self._shell.error_text)
        self._attr_extra_state_attributes = attributes

        self._attr_native_value = getattr(fad, self._id, None)

        if self.hass is not None:
            self.async_write_ha_state()


class TestSensorEntity(SensorEntity):
    """Home Assistant sensor containing FreeAir data."""

    def __init__(self, hass, unique_id, shell):
        self._hass = hass
        self._shell = shell
        self._id = "test"

        # entity attributes
        self._attr_device_info = shell.device_info
        self._attr_unique_id = f"{unique_id}_{self._id}"
        self._attr_name = self._id

        # self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_has_entity_name = True
        self._attr_should_poll = False
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_options = [
            "good",
            "moderate",
            "unhealthy",
            "unhealthy_sensitive",
            "very_unhealthy",
            "hazardous",
        ]

        if self._shell.data is not None:
            self._update_sensor()

        async_dispatcher_connect(hass, UPDATE_SENSORS_SIGNAL, self._update_sensor)

    @callback
    def _update_sensor(self):
        """Update the value and the extra-state-attributes of the entity."""
        fad = self._shell.data

        attributes = {"timestamp": getattr(fad, "timestamp", None)}
        self._attr_extra_state_attributes = attributes

        self._attr_native_value = "moderate"

        if self.hass is not None:
            self.async_write_ha_state()
