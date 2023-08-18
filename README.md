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

## Refresh Service

If you want to trigger a manual refresh of all device data, you can call the service:

`freeair_connect.fetch_data`
