"""Constants for the component."""

# Component domain, used to store component data in hass data.
DOMAIN = "freeair_connect"

CONF_SERIAL_NO = "serial_no"
CONF_PASSWORD = "password"

UPDATE_SENSORS_SIGNAL = f"{DOMAIN}_update_sensors_signal"


CONTROL_AUTO_TEXT = {
    0: "Minimum Ventilation",
    1: "Humidity Reduction(rel)",
    2: "Humidity Reduction(abs)",
    3: "Active Cooling",
    4: "CO2 Reduction",
    5: "Water Insertion",
    6: "Outdoor Temp < -22",
    7: "Humidity Input",
}

STATE_TEXT = {
    0: "Comfort",
    1: "Comfort",
    2: "Sleep",
    3: "Turbo",
    4: "Turbocool",
    5: "Service",
    6: "Test",
    7: "Manufacturer",
}
