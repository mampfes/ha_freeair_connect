# FreeAir Connect

This component adds data from [FreeAir Connect](https://www.freeair-connect.de) to Home Assistant.

If you like this component, please give it a star on [github](https://github.com/mampfes/ha_freeair_connect).

## Installation

1. Ensure that [HACS](https://hacs.xyz) is installed.
2. Install **FreeAir Connect** integration via HACS.
3. Add **FreeAir Connect** integration to Home Assistant:

   [![badge](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=freeair_connect)

In case you would like to install manually:

1. Copy the folder `custom_components/freeair_connect` to `custom_components` in your Home Assistant `config` folder.
2. Add **FreeAir Connect** integration to Home Assistant:

    [![badge](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=freeair_connect)

## Sensors

This component provides sensors for all major values provided by a FreeAir device.

## Local Server Mode

Instead of polling the freeair-connect.de cloud, the integration can run a local HTTP server that receives data directly from the device. To use this mode:

1. Enable **"Lokalen Server aktivieren"** / **"Enable local server"** during setup, or afterwards via **Settings → Integrations → FreeAir Connect → Configure**.
2. Using the FreeAir USB app, configure the device's server address to the IP address of your Home Assistant instance.

> **Note:** The local server listens on port 80 by default. Make sure this port is not already in use on your Home Assistant host. You can change the port in the integration options, but only do so when running a reverse proxy in front of the server, since the device expects to reach the server on port 80.

## Refresh Service

If you want to trigger a manual refresh of all device data, you can call the service:

`freeair_connect.fetch_data`
