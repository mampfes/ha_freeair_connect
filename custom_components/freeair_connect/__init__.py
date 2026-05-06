import base64
import logging
from datetime import datetime, timedelta

import voluptuous as vol
from aiohttp import web
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (ATTR_CONFIGURATION_URL, ATTR_HW_VERSION,
                                 ATTR_IDENTIFIERS, ATTR_MANUFACTURER,
                                 ATTR_MODEL, ATTR_NAME, ATTR_SW_VERSION)
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

from .const import CONF_PASSWORD, CONF_SERIAL_NO, CONF_SERVER_MODE, DOMAIN, UPDATE_SENSORS_SIGNAL
from .FreeAir import Connect

_LOGGER = logging.getLogger(__name__)


PLATFORMS = ["sensor", "binary_sensor", "number", "select"]

BLUHOME_CONNECT_PORT = 80


class BluHomeConnectServer:
    def __init__(self, hass: HomeAssistant):
        self._hass = hass

    async def blu_home_index(self, request):
        s_value = request.rel_url.query["s"]
        b_value = request.rel_url.query["b"]
        shell = self._select_shell(s_value)
        if not shell:
            _LOGGER.warning("Could not find shell for serial number derived from %s", s_value)
            return web.Response()
        timestamp = datetime.now()
        # Device uses ';' as base64 padding instead of '='
        encrypted_data = base64.b64decode(b_value.replace(";", "="), altchars="-_")
        version = self._extract_version(s_value)
        shell.parse(encrypted_data, timestamp, version, version)
        return web.Response()

    async def blu_home_control(self, request):
        s_value = request.rel_url.query["s"]
        shell = self._select_shell(s_value)
        comfort_level = 5
        operation_mode = 1
        if shell:
            comfort_level = shell.comfort_level() or comfort_level
            operation_mode = shell.operation_mode() or operation_mode
        else:
            _LOGGER.warning("Could not find shell for serial number derived from %s", s_value)
        response = f"heart__beat11{comfort_level}{operation_mode}\n"
        return web.Response(text=response)

    def _extract_version(self, s):
        return s.split("y")[1]

    def _select_shell(self, s):
        parts = s.split("y")
        serial_no = parts[0].split("x")[2]
        return self._hass.data.setdefault(DOMAIN, {}).get(serial_no)

    async def start_server(self):
        app = web.Application()
        app.add_routes([web.get("/apps/data/blucontrol/", self.blu_home_index)])
        app.add_routes([web.get("/apps/data/blucontrol/control/", self.blu_home_control)])
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        site = web.TCPSite(runner, port=BLUHOME_CONNECT_PORT)
        try:
            await site.start()
            self._hass.data[f"{DOMAIN}_server_runner"] = runner
            _LOGGER.info("Started HTTP server on port %s", BLUHOME_CONNECT_PORT)
        except OSError as error:
            _LOGGER.error("Failed to start HTTP server on port %d: %s", BLUHOME_CONNECT_PORT, error)


async def async_setup(hass, config):
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

    serial_no = entry.data[CONF_SERIAL_NO]
    server_mode = entry.options.get(CONF_SERVER_MODE, entry.data.get(CONF_SERVER_MODE, False))

    shell = FreeAirConnectShell(
        hass, serial_no=serial_no, password=entry.data[CONF_PASSWORD], server_mode=server_mode
    )
    shells[serial_no] = shell

    if server_mode:
        if not hass.data.get(f"{DOMAIN}_server_started"):
            server = BluHomeConnectServer(hass)
            await server.start_server()
            hass.data[f"{DOMAIN}_server_started"] = True
    else:
        await hass.async_add_executor_job(shell._fac.fetch)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        shells = hass.data[DOMAIN]
        del shells[entry.data[CONF_SERIAL_NO]]

        # Stop server if no remaining shells need it
        if not any(s._server_mode for s in shells.values()):
            runner = hass.data.pop(f"{DOMAIN}_server_runner", None)
            if runner:
                await runner.cleanup()
                _LOGGER.info("Stopped HTTP server")
            hass.data.pop(f"{DOMAIN}_server_started", None)

        if len(shells) == 0:
            del hass.data[DOMAIN]

    return unload_ok


class FreeAirConnectShell:
    """Shell object for FreeAir Connect. Stored in hass.data."""

    def __init__(self, hass: HomeAssistant, serial_no: str, password: str, server_mode: bool = False):
        """Initialize the instance."""
        self._hass = hass
        self._serial_no = serial_no
        self._server_mode = server_mode
        self._fac = Connect(serial_no=serial_no, password=password, server_mode=server_mode)

        if not server_mode:
            self._fetch_callback_listener = async_track_time_interval(
                self._hass, self._fetch_callback, timedelta(minutes=10)
            )

    @callback
    def _fetch_callback(self, *_):
        self._hass.add_job(self._fetch)

    def _fetch(self):
        self._fac.fetch()
        dispatcher_send(self._hass, UPDATE_SENSORS_SIGNAL)

    def parse(self, encrypted_bytes, timestamp, version, version_fa100):
        data = self._fac.parse(encrypted_bytes, timestamp, version, version_fa100)
        dispatcher_send(self._hass, UPDATE_SENSORS_SIGNAL)
        return data

    def comfort_level(self):
        return self._fac._comfort_level

    def operation_mode(self):
        return self._fac._operation_mode

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
            ATTR_CONFIGURATION_URL: f"https://freeair-connect.de/?serialnumber={self.serial_no}",
        }
