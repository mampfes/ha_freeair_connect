import base64
import binascii
import logging
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
    0: "Comfort",
    1: "Comfort",
    2: "Sleep",
    3: "Turbo",
    4: "Turbocool",
    5: "Service",
    6: "Test",
    7: "Manufacturer",
}

_ControlAutoMap = {
    0: "Minimum Ventilation",
    1: "Humidity Reduction (rel)",
    2: "Humidity Reduction (abs)",
    3: "Active Cooling",
    4: "CO2 Reduction",
    5: "Water Insertion",
    6: "Outdoor Temp < -22",
    7: "Humidity Input",
    # fehlt: defrosting
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
        return self._version

    @property
    def version_fa100(self):
        return self._version_fa100

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
        return self._extract([_BitSlice(37, 5, 1)])

    @property
    def fan_lim_2nd_room(self):
        return self._extract([_BitSlice(35, 6, 1)])

    @property
    def b_2nd_room_only_20(self):
        return self._extract([_BitSlice(35, 5, 1)])

    @property
    def summer_cooling(self):
        return self._extract([_BitSlice(37, 6, 1)])

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
    def filter_supply_full(self):
        return self._extract([_BitSlice(34, 5, 1)])

    @property
    def filter_extract_full(self):
        return self._extract([_BitSlice(34, 6, 1)])

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
        return self._extract([_BitSlice(23, 6, 1)])

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

    # fehlt:
    # PRG . Programm . mve
    # RA [m2] . Room Area .
    # 2A [m3/h] . 2nd Room Adapter . 100
    # ADY [kg/m3] Air Densty . 1132
    # EFN . 0
    # ELN . 0
    # ECO . 0
    # SWV . Software Version . 2.07
    # SNR . Serial Number . 20643-EGKueche

    # Program
    # mve . Minimum Ventilation . On
    # hrr . Humidity reducation (rel) . Off
    # hra . Humidity reducation (abs) . Off
    # col . Active Cooling . Off
    # co2 . CO2 Reduction . Off

    # Reduction (Mini)
    # dfr . Defrosting . Off
    # hin . Humidity Input . Off
    # otb . Outdoor Temperatur < -22C . Off
    # win . Water Insertin . Off

    # Questions:
    # TSC . Supply Temp (cal.) . 19.9  ==> temp_virt_sup_exit???
    # TPE, TBY, TBA, TPS (alle 3) ==> control_set_*
    # ZKL, AKL (beide 27) ==> fsc, fec
    # LKA (68) ==> csu
    # LKF (13) ==> cfa

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


class Connect:
    def __init__(self, serial_no, password):
        self._serial_no = serial_no
        self._password = password
        self._fetchtime = None
        self._fad = None

    @property
    def fetchtime(self):
        """Return last fetch time."""
        return self._fetchtime

    @property
    def data(self):
        return self._fad

    def fetch(self):
        try:
            blob = self._fetch_web()
        except Exception as error:
            self._fad = None
            _LOGGER.error(f"fetch failed for SN {self._serial_no}: {error}")

        # split blob
        parts = blob.split("timestamp")
        encrypted_data = parts[0]
        timestamp = datetime.strptime(parts[1], "%Y-%m-%d %H:%M:%S")
        version = parts[2]
        version_fa100 = parts[3]

        self._fad = self._parse(encrypted_data, timestamp, version, version_fa100)

    def _fetch_web(self):
        data = {"serObject": f"serialnumber={self._serial_no}"}
        r = requests.post(
            "https://www.freeair-connect.de/getDataHexAjax.php", data=data
        )
        r.raise_for_status()
        return r.text

    def _parse(self, encrypted_data, timestamp, version, version_fa100):
        # encrypted_data = "PgiFboacxLklQ3gz8APQ87wwROYqCWCKViRZR0XCZo72CrWG3Cn91Dr+it7SfJwD"
        # encrypted_data = urllib.parse.unquote(encrypted_data) # this is probably not needed!
        encrypted_data = base64.b64decode(encrypted_data)

        # prepare initialization vector
        iv = "000102030405060708090a0b0c0d0e0f"
        iv = binascii.unhexlify(iv)

        # fill password to 16 characters with zeros
        pw = self._password.ljust(16, "0")

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
            "serObject": f"CL={comfort_level}&OM={operation_mode}&serialnumber={self._serial_no}&device=1"
        }
        r = requests.post(
            "https://www.freeair-connect.de/buttonUserAjax.php", data=data
        )
        r.raise_for_status()
