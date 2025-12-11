import base64
import binascii
import logging
import urllib.parse
from datetime import datetime

import requests
from py3rijndael import RijndaelCbc, ZeroPadding

_LOGGER = logging.getLogger(__name__)


class _BitSlice:
    def __init__(self, bytepos, bitoffset, length):
        self._bytepos = bytepos
        self._bitoffset = bitoffset
        self._length = length  # in bits

    def get_bit_string(self, bitstr):
        bits = "{:0{}b}".format(bitstr[self._bytepos], 8)
        offset = 8 - self._bitoffset - self._length
        return bits[offset : offset + self._length]


_OperationModeMap = {
    0: "comfort",
    1: "comfort",
    2: "sleep",
    3: "turbo",
    4: "turbo_cool",
    5: "service",
    6: "test",
    7: "manufacturer",
}

_ControlAutoMap = {
    0: "min_ventilation",
    1: "humidity_reduction_rel",
    2: "humidity_reduction_abs",
    3: "active_cooling",
    4: "co2_reduction",
    5: "water_insertion",
    6: "outdoor_temp_lt_22_degc",
    7: "humidity_input",
}


class Data:
    def __init__(self, rawdata, timestamp, version, version_fa100):
        self._data = rawdata
        self._timestamp = timestamp
        self._version = version
        self._version_fa100 = version_fa100
        self._assumed_states = {}

    def set_comfort_level(self, value):
        self._assumed_states["comfort_level"] = value

    @property
    def is_comfort_level_assumed(self):
        return "comfort_level" in self._assumed_states

    def set_operation_mode(self, value):
        self._assumed_states["operation_mode"] = value

    @property
    def is_operation_mode_assumed(self):
        return "operation_mode" in self._assumed_states

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def version(self):
        return self._version.replace("x", ".")

    @property
    def version_fa100(self):
        return self._version_fa100.replace("x", ".")

    @property
    def humidity_outdoor_rel(self):
        return self._data[0]

    @property
    def humidity_extract_rel(self):
        return self._data[1]

    @property
    def s1(self):
        return self._data[41]

    @property
    def s2(self):
        return self._data[42]

    @property
    def s3(self):
        return self._data[43]

    @property
    def s4(self):
        return self._data[44]

    @property
    def s5(self):
        return self._data[45]

    @property
    def s6(self):
        return self._data[46]

    @property
    def temp_supply(self):
        val = self._extract([_BitSlice(29, 0, 4), _BitSlice(2, 0, 7)])
        return self._as_signed(val, 11) / 8

    @property
    def temp_outdoor(self):
        val = self._extract([_BitSlice(32, 0, 4), _BitSlice(3, 0, 7)])
        return self._as_signed(val, 11) / 8

    @property
    def temp_exhaust(self):
        val = self._extract([_BitSlice(31, 0, 4), _BitSlice(4, 0, 7)])
        return self._as_signed(val, 11) / 8

    @property
    def temp_extract(self):
        val = self._extract([_BitSlice(30, 0, 4), _BitSlice(5, 0, 7)])
        return self._as_signed(val, 11) / 8

    @property
    def temp_virt_sup_exit(self):
        val = self._extract([_BitSlice(33, 0, 4), _BitSlice(6, 0, 7)])
        return self._as_signed(val, 11) / 8

    @property
    def co2_extract(self):
        return self._extract([_BitSlice(36, 5, 1), _BitSlice(13, 0, 7)]) * 16

    @property
    def air_pressure(self):
        return self._extract([_BitSlice(39, 0, 5), _BitSlice(34, 0, 4)]) + 700

    @property
    def comfort_level(self):
        return self._assumed_states.get(
            "comfort_level", self._extract([_BitSlice(29, 4, 3)]) + 1
        )

    @property
    def operation_mode(self):  # = "State"
        return self._assumed_states.get(
            "operation_mode", self._extract([_BitSlice(30, 4, 3)])
        )

    @property
    def operation_mode_str(self):
        return _OperationModeMap.get(self.operation_mode)

    @property
    def humidity_reduction_mode(self):
        return bool(self._extract([_BitSlice(37, 5, 1)]))

    @property
    def fan_lim_2nd_room(self):
        return bool(self._extract([_BitSlice(35, 6, 1)]))

    @property
    def b_2nd_room_only_20(self):
        return bool(self._extract([_BitSlice(35, 5, 1)]))

    @property
    def summer_cooling(self):
        return bool(self._extract([_BitSlice(37, 6, 1)]))

    @property
    def error_state(self):
        return self._extract([_BitSlice(24, 0, 5)])

    @property
    def fan_speed(self):
        return self._extract([_BitSlice(38, 0, 4)])

    @property
    def fan_speed_supply(self):  # TODO: is this supply?
        return self._extract([_BitSlice(37, 0, 5), _BitSlice(9, 0, 7)])

    @property
    def fan_speed_extract(self):
        return self._extract([_BitSlice(36, 0, 5), _BitSlice(7, 0, 7)])

    @property
    def air_flow_avg(self):
        return self._extract([_BitSlice(35, 0, 5)])

    @property
    def air_flow(self):
        return self.fan_speed * 10 if self.fan_speed > 2 else self.air_flow_avg

    @property
    def filter_supply_full(self):
        return bool(self._extract([_BitSlice(34, 5, 1)]))

    @property
    def filter_extract_full(self):
        return bool(self._extract([_BitSlice(34, 6, 1)]))

    @property
    def vent_pos_extract(self):
        return self._extract([_BitSlice(26, 0, 5)])

    @property
    def vent_pos_bath(self):
        return self._extract([_BitSlice(27, 0, 5)])

    @property
    def vent_pos_supply(self):
        return self._extract([_BitSlice(25, 0, 5)])

    @property
    def vent_pos_bypass(self):
        return self._extract([_BitSlice(28, 0, 5)])

    @property
    def control_auto(self):
        return self._extract([_BitSlice(31, 4, 3)])

    @property
    def control_auto_str(self):
        return _ControlAutoMap.get(self.control_auto)

    @property
    def dip_switch(self):
        return self._extract([_BitSlice(36, 6, 1), _BitSlice(8, 0, 7)])

    @property
    def defrost_exhaust(self):
        return self._extract([_BitSlice(24, 5, 2)])

    @property
    def control_set_supply_vent(self):
        return self._extract([_BitSlice(25, 5, 2)])

    @property
    def control_set_ext_vent(self):
        return self._extract([_BitSlice(26, 5, 2)])

    @property
    def control_set_2nd_vent(self):
        return self._extract([_BitSlice(27, 5, 2)])

    @property
    def control_set_bypass_vent(self):
        return self._extract([_BitSlice(28, 5, 2)])

    @property
    def error_file_nbr(self):
        return self._extract([_BitSlice(23, 0, 6)])

    @property
    def error_line_nbr(self):
        return self._extract(
            [_BitSlice(39, 5, 2), _BitSlice(10, 0, 7), _BitSlice(11, 0, 7)]
        )

    @property
    def error_code(self):
        return self._extract([_BitSlice(40, 6, 1), _BitSlice(12, 0, 7)])

    @property
    def filter_hours(self):
        return self._extract(
            [_BitSlice(40, 4, 2), _BitSlice(17, 0, 7), _BitSlice(16, 0, 7)]
        )

    @property
    def operating_hours(self):
        return self._extract(
            [_BitSlice(40, 0, 4), _BitSlice(15, 0, 7), _BitSlice(14, 0, 7)]
        )

    @property
    def board_version(self):
        return self._data[22]

    @property
    def deicing(self):
        return bool(self._extract([_BitSlice(23, 6, 1)]))

    @property
    def fsc(self):
        return self._extract([_BitSlice(38, 4, 1), _BitSlice(18, 0, 7)])

    @property
    def fec(self):
        return self._extract([_BitSlice(38, 5, 1), _BitSlice(19, 0, 7)])

    @property
    def csu(self):
        return self._extract([_BitSlice(38, 6, 1), _BitSlice(20, 0, 7)])

    @property
    def cfa(self):
        return self._extract([_BitSlice(34, 4, 1), _BitSlice(21, 0, 7)])

    @property
    def rssi(self):
        val = self._extract([_BitSlice(47, 0, 8)])
        return self._as_signed(val, 8)

    @property
    def filter_status_supply(self):
        filter_rpms = [
            [20, 870, 1510],
            [30, 1e3, 1640],
            [40, 1230, 1870],
            [50, 1460, 2100],
            [60, 1690, 2410],
            [70, 1910, 2630],
            [85, 2230, 2950],
            [100, 2540, 3260],
            [0, 0, 0],
        ]
        return self._filter_status(self.fan_speed_supply, filter_rpms)

    @property
    def filter_status_extract(self):
        filter_rpms = [
            [20, 920, 1560],
            [30, 1040, 1680],
            [40, 1260, 1900],
            [50, 1480, 2200],
            [60, 1700, 2420],
            [70, 1910, 2710],
            [85, 2210, 2930],
            [100, 2480, 3200],
            [0, 0, 0],
        ]
        return self._filter_status(self.fan_speed_extract, filter_rpms)

    @property
    def energy_savings(self):
        if self.temp_extract - self.temp_outdoor < 2:
            return 0

        return round(
            (self.air_flow * (self.temp_supply - self.temp_outdoor)) / 3 + 0.5, 1
        )

    @property
    def heat_recovery(self):
        if self.air_flow == 0:
            return 100

        if self.temp_extract - self.temp_outdoor < 2:
            return 100

        return round(
            100
            * (
                1
                - (self.temp_extract - self.temp_supply)
                / (self.temp_extract - self.temp_outdoor)
            )
            + 0.5,
            1,
        )

    def _as_signed(self, value, potenz):
        maxUn = 2**potenz
        if value >= maxUn / 2:
            value = value - maxUn
        return value

    def _extract(self, bitslicelist):
        result = ""
        for s in bitslicelist:
            result += s.get_bit_string(self._data)
        return int(result, 2)

    def _filter_status(self, fan_rpm, filter_rpms):
        fan_speed = self.fan_speed * 10
        for e in filter_rpms:
            if e[0] < fan_speed:
                continue
            diff = e[2] - e[1]
            if fan_rpm < e[1] - diff / 2:
                return 0
            if fan_rpm < e[1] + diff * 0.4:
                return 1
            if fan_rpm < e[1] + diff * 0.7:
                return 2
            if fan_rpm < e[1] + diff * 0.95:
                return 3
            return 4
        return None


_DEFAULT_HEADERS = {
    "Accept-Encoding": "gzip, deflate",
}


class Connect:
    def __init__(self, serial_no, password):
        self._serial_no = serial_no
        self._password = password
        self._fetchtime = None
        self._fad = None
        self._error_text = {}
        self._session = requests.Session()
        self._session.headers.update(_DEFAULT_HEADERS)

    @property
    def fetchtime(self):
        """Return last fetch time."""
        return self._fetchtime

    @property
    def data(self):
        return self._fad

    @property
    def error_text(self):
        return self._error_text

    def _login(self):
        self._session.post(
            "https://www.freeair-connect.de/index.php",
            data={"serialnumber": self._serial_no},
        ).raise_for_status()

        self._session.post(
            "https://www.freeair-connect.de/index.php",
            data={"serial_password": self._password},
        ).raise_for_status()

    def fetch(self):
        blob = None
        try:
            self._login()
            blob = self._fetch_data()
        except Exception as error:
            self._fad = None
            self._error_text = {}
            _LOGGER.error(f"fetch failed for SN {self._serial_no}: {error}")
            return

        if blob is None:
            _LOGGER.error(f"No data received for SN {self._serial_no}")
            return

        parts = blob.split("timestamp")
        encrypted_data = parts[0]
        timestamp = datetime.strptime(parts[1], "%Y-%m-%d %H:%M:%S")
        version = parts[2]
        version_fa100 = parts[3]

        self._fad = self._parse(encrypted_data, timestamp, version, version_fa100)
        self._fetchtime = timestamp

        if self._fad.error_state not in (0, 22):
            self._fetch_error()
        else:
            self._error_text = {}

    def _fetch_data(self):
        r = self._session.post("https://www.freeair-connect.de/getDataHexAjax.php")
        r.raise_for_status()
        return r.text

    def _fetch_error(self):
        data = {"serObject": f"err=1&serialnumber={self._serial_no}&device=1"}
        r = self._session.post(
            "https://www.freeair-connect.de/getErrorTextLong.php", data=data
        )

        if not r.ok:
            return

        err = urllib.parse.parse_qs(r.text)
        self._error_text = {
            "en": err["en"][0],
            "de": err["de"][0],
        }

    def _parse(self, encrypted_data, timestamp, version, version_fa100):
        encrypted_data = base64.b64decode(encrypted_data)

        version_numbers = version.split("x")
        major = int(version_numbers[0])
        minor = int(version_numbers[1])
        if major == 2 and (minor <= 13 or minor == 20 or minor == 21):
            iv = "000102030405060708090a0b0c0d0e0f"
            size = 16
        else:
            iv = "30313233343536373839303132333435"
            size = 32

        # prepare initialization vector
        iv = binascii.unhexlify(iv)
        
        # fill password to 16 characters with zeros
        pw = self._password.ljust(size, "0")

        rijndael = RijndaelCbc(key=pw, iv=iv, padding=ZeroPadding(16), block_size=16)
        data = rijndael.decrypt(encrypted_data)

        # extract data
        return Data(data, timestamp, version, version_fa100)

    def set_comfort_level(self, value):
        assert value >= 1 and value <= 5
        self._fad.set_comfort_level(value)
        self.set_cl_and_om(value, self._fad.operation_mode)

    def set_operation_mode(self, value):
        assert value >= 1 and value <= 4
        self._fad.set_operation_mode(value)
        self.set_cl_and_om(self._fad.comfort_level, value)

    def set_cl_and_om(self, comfort_level, operation_mode):
        if operation_mode == 0:
            operation_mode = 1
        data = {
            "RB_CL": comfort_level,
            "RB_OM": operation_mode,
            "srn_button": f"{self._serial_no}-Test",
            "lang_button": "en",
            "serial_password": "",
        }
        r = self._session.post(
            "https://www.freeair-connect.de/bf.php", data=data
        )
        r.raise_for_status()
