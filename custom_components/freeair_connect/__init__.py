import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (ATTR_CONFIGURATION_URL, ATTR_HW_VERSION,
                                 ATTR_IDENTIFIERS, ATTR_MANUFACTURER,
                                 ATTR_MODEL, ATTR_NAME, ATTR_SW_VERSION)
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

from .const import CONF_PASSWORD, CONF_SERIAL_NO, DOMAIN, UPDATE_SENSORS_SIGNAL
from .FreeAir import Connect
from aiohttp import web
from datetime import datetime
import base64

_LOGGER = logging.getLogger(__name__)


PLATFORMS = ["sensor", "binary_sensor", "number", "select"]

BLUHOME_CONNECT_PORT = 80

class BluHomeConnectServer:
    def __init__(self, hass: HomeAssistant):
        self._hass = hass

    async def blu_home_index(self, request):
        s_value = request.rel_url.query['s']
        b_value = request.rel_url.query['b']
        _LOGGER.info(f"Received index request with s = {s_value}, b = {b_value}")
        shell = self._select_shell(s_value)
        if not shell:
            _LOGGER.warn(f"Could not find shell for serial number {s_value}")
            return web.Response()
        timestamp = datetime.now()
        encrypted_data = base64.b64decode(b_value, altchars="-_")
        version = self._extract_version(s_value)
        data = shell.parse(encrypted_data, timestamp, version, version)
        _LOGGER.info(f"Interpreted data for serial number {shell.serial_no}: temp_supply = {data.temp_supply}, temp_outdoor = {data.temp_outdoor}, temp_extract = {data.temp_extract}, temp_exhaust = {data.temp_exhaust}, humidity_outdoor_rel = {data.humidity_outdoor_rel}, humidity_extract_rel = {data.humidity_extract_rel}, co2_extract = {data.co2_extract}, comfort_level = {data.comfort_level}, operation_mode = {data.operation_mode}, air_flow = {data.air_flow}, filter_hours = {data.filter_hours}")
        return web.Response()

    async def blu_home_control(self, request):
        s_value = request.rel_url.query['s']
        shell = self._select_shell(s_value)
        comfort_level = 5
        operation_mode = 1
        if shell:
            comfort_level = shell.comfort_level() or comfort_level
            operation_mode = shell.operation_mode() or operation_mode
        else:
            _LOGGER.warn(f"Could not find shell for serial number {s_value}")
        response = f"heart__beat11{comfort_level}{operation_mode}\n"
        _LOGGER.info(f"Received control request with s = {s_value}, b = {request.rel_url.query['b']}, response was {response}")
        return web.Response(text = response)

    def _extract_version(self, s):
        # s = '1x1x57225y2x22x0'
        parts = s.split('y')
        return parts[1]

    def _select_shell(self, s):
        # s = '1x1x57225y2x22x0'
        parts = s.split('y')
        serial_parts = parts[0].split('x')
        serial_no = serial_parts[2]
        shells = self._hass.data.setdefault(DOMAIN, {})
        return shells[serial_no]

    async def start_server(self):
        app = web.Application()
        app.add_routes([web.get('/apps/data/blucontrol/', self.blu_home_index)])
        app.add_routes([web.get('/apps/data/blucontrol/control/', self.blu_home_control)])
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        http_site = web.TCPSite(runner, port=BLUHOME_CONNECT_PORT)
        try:
            await http_site.start()
            _LOGGER.info("Started HTTP webserver on port %s", BLUHOME_CONNECT_PORT)
        except OSError as error:
            _LOGGER.error("Failed to create HTTP server at port %d: %s", BLUHOME_CONNECT_PORT, error)


async def async_setup(hass, config):
    blu_home = BluHomeConnectServer(hass)
    await blu_home.start_server()

    async def async_fetch_data(service: ServiceCall) -> None:
        shells = hass.data.setdefault(DOMAIN, {})

        for shell in shells.values():
            shell._fetch_callback()

    # Register new Service fetch_data
    hass.services.async_register(
        DOMAIN, "fetch_data", async_fetch_data, schema=vol.Schema({})
    )
    return True


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

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

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
#        dispatcher_send(self._hass, UPDATE_SENSORS_SIGNAL)

    def parse(self, encrypted_data, timestamp, version, version_fa100):
        data = self._fac.parse(encrypted_data, timestamp, version, version_fa100)
        dispatcher_send(self._hass, UPDATE_SENSORS_SIGNAL)
        return data

    async def set_comfort_level(self, value):
        l = lambda: self._fac.set_comfort_level(value)
        await self._hass.async_add_executor_job(l)

    async def set_operation_mode(self, value):
        l = lambda: self._fac.set_operation_mode(value)
        await self._hass.async_add_executor_job(l)

    def operation_mode(self):
        return self._fac._operation_mode

    def comfort_level(self):
        return self._fac._comfort_level

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
            ATTR_CONFIGURATION_URL: f"https://freeair-connect.de/?serialnumber={self.serial_no}",
        }
