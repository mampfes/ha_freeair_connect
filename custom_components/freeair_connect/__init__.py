import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (ATTR_CONFIGURATION_URL, ATTR_HW_VERSION,
                                 ATTR_IDENTIFIERS, ATTR_MANUFACTURER,
                                 ATTR_MODEL, ATTR_NAME, ATTR_SW_VERSION)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

from .const import CONF_PASSWORD, CONF_SERIAL_NO, DOMAIN, UPDATE_SENSORS_SIGNAL
from .FreeAir import Connect

_LOGGER = logging.getLogger(__name__)


PLATFORMS = ["sensor", "binary_sensor", "number", "select"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up component from a config entry, config_entry contains data from config entry database."""
    shells = hass.data.setdefault(DOMAIN, {})

    # store shell object
    serial_no = entry.data[CONF_SERIAL_NO]

    shell = FreeAirConnectShell(
        hass, serial_no=serial_no, password=entry.data[CONF_PASSWORD]
    )
    shells[serial_no] = shell

    await hass.async_add_executor_job(shell._fac.fetch)

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        shells = hass.data[DOMAIN]

        del shells[entry.data[CONF_SERIAL_NO]]

        if len(shells) == 0:
            # also remove shells if not used by any entry any more
            del hass.data[DOMAIN]

    return unload_ok


class FreeAirConnectShell:
    """Shell object for FreeAir Connect. Stored in hass.data."""

    def __init__(self, hass: HomeAssistant, serial_no: str, password: str):
        """Initialize the instance."""
        self._hass = hass
        self._serial_no = serial_no
        self._fac = Connect(serial_no=serial_no, password=password)

        self._fetch_callback_listener = async_track_time_interval(
            self._hass, self._fetch_callback, timedelta(minutes=10)
        )

    @callback
    def _fetch_callback(self, *_):
        self._hass.add_job(self._fetch)

    def _fetch(self):
        self._fac.fetch()
        dispatcher_send(self._hass, UPDATE_SENSORS_SIGNAL)

    async def set_comfort_level(self, value):
        l = lambda: self._fac.set_comfort_level(value)
        await self._hass.async_add_executor_job(l)

    async def set_operation_mode(self, value):
        l = lambda: self._fac.set_operation_mode(value)
        await self._hass.async_add_executor_job(l)

    @property
    def serial_no(self):
        return self._serial_no

    @property
    def data(self):
        return self._fac.data

    @property
    def error_text(self):
        return self._fac.error_text

    @property
    def device_info(self):
        return {
            ATTR_IDENTIFIERS: {(DOMAIN, self.serial_no)},
            ATTR_NAME: f"freeAir {self.serial_no}",
            ATTR_MANUFACTURER: "bluMartin",
            ATTR_MODEL: "freeAir",
            # "entry_type": DeviceEntryType.SERVICE,
            ATTR_SW_VERSION: getattr(self.data, "version", None),
            ATTR_HW_VERSION: getattr(self.data, "board_version", None),
            ATTR_CONFIGURATION_URL: f"https://freeair-connect.de/tabs.php?sn={self.serial_no}",
        }
