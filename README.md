# vaillant-netatmo-api

[![GitHub version](https://badge.fury.io/gh/MislavMandaric%2Fvaillant-netatmo-api.svg)](https://badge.fury.io/gh/MislavMandaric%2Fvaillant-netatmo-api)
[![PyPI version](https://badge.fury.io/py/vaillant-netatmo-api.svg)](https://badge.fury.io/py/vaillant-netatmo-api)
![Tests](https://github.com/MislavMandaric/vaillant-netatmo-api/actions/workflows/tests.yml/badge.svg)


## General

Python 3 library for managing Vaillant thermostats using the Netatmo API. It provides one-to-one mapping with Vaillant's Netatmo API and offeres similar functionality as the official Vaillant vSMART/eRELAX app.

> NOTE: This library is still in a prerelease status and will be until v1.0.0. There might be breaking changes to the public API in any of the v0.x.y versions.

## Installation

Library can be simply installed using pip.

```bash
pip install vaillant-netatmo-api
```

Library requires Python 3 and has [tenacity](https://github.com/jd/tenacity) and [httpx](https://github.com/encode/httpx) dependencies.

> NOTE: httpx is currently a prerelease software. The version outlined in the `requirements.txt` should be working properly, but if there are some breaking changes, please check their Github issue tracker for known issues.

## Usage

### Getting the token from the OAuth API

All Netatmo APIs are protected and require a bearer token to authenticate. To get this token, Netatmo offers an OAuth API.

Since Vaillant uses Resource Owner Password Credentials Grant, there is only one method in the `AuthClient` API:

* `async_token`: getting a bearer token and storing it in the token store

```python
from vaillant_netatmo_api import auth_client

CLIENT_ID = ""
CLIENT_SECRET = ""

def handle_token_update(token):
    token_string = token.serialize()
    write_to_storage(token_string)

async with auth_client(CLIENT_ID, CLIENT_SECRET, handle_token_update) as client:
    await client.async_token(
        username,
        password,
        user_prefix,
        app_version,
    )
```

### Accessing the Thermostat API

There are three APIs available for the `ThermostatClient`, all of which require the bearer token for authentication:

* `async_get_thermostats_data`: getting all the devices associated with the user account
* `async_set_system_mode`: changing system mode for a device and module (ie. summer, winter or frostguard)
* `async_set_minor_mode`: changing minor mode for a device and module (ie. manual mode, away mode or hot water boost mode)
* `async_sync_schedule`: updating schedule data for a device and module
* `async_switch_schedule`: changing active schedule for a device and module

```python
from vaillant_netatmo_api import thermostat_client, SystemMode, Token

CLIENT_ID = ""
CLIENT_SECRET = ""

token_string = read_from_storage()
token = Token.deserialize(token_string)

def handle_token_update(token):
    token_string = token.serialize()
    write_to_storage(token_string)

async with thermostat_client(CLIENT_ID, CLIENT_SECRET, token, handle_token_update) as client:
    devices = await client.async_get_thermostats_data()

    d_id = devices[0].id
    m_id = devices[0].modules[0].id

    await client.async_set_system_mode(d_id, m_id, SystemMode.WINTER)
```

### Using clients as singletons

Even though library offers context manager for using `AuthClient` and `ThermostatClient`, this should only be done during development or in very infrequent usage scenarios.

Both of the clients use `httpx.AsyncClient` as the underlying HTTP communication library, which implements connection pooling and connection reuse. This means doing multiple concurent requests should be done by using the same instance of the `AuthClient` or `ThermostatClient`, which is not possible by using the context manager API since this API will return new instance of the client every time `auth_client` or `thermostat_client` method is called.

To achieve optimal usage, which will utilize connection pooling and connection reuse, both `AuthClient` and `ThermostatClient` should be used by instantiating the clients and providing `httpx.AsyncClient` instance in a constructor. This provided client should be used as singleton, or with some other context management mechanism, with the context wider than one block of code or one inbound request.

Here is an example for usage in Home Assistant.

```python
# When setting up integration with all the devices of one account, instantiate and store the client in a configuration memory store
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = get_async_client(hass)
    token_store = TokenStore(
        entry.data[CONF_CLIENT_ID],
        entry.data[CONF_CLIENT_SECRET],
        token,
        handle_token_update,
    )

    hass.data[DOMAIN][entry.entry_id] = ThermostatClient(client, token_store)
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True

# When unloading the integration of this same account, read the client and close it manually
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
```

Similar hooks which represent some kind of application context should be used when integrating this library into a different application (Flask, Django or similar).

## Acknowledgements

This library would not exist if it weren't for previous implementations by the following projects:

* https://github.com/philippelt/netatmo-api-python
* https://github.com/jabesq/netatmo-api-python
* https://github.com/samueldumont/netatmo-api-python
* https://github.com/jabesq/pyatmo
* https://github.com/pjmaenh/pyvaillant

They laid out the foundation by exploring and documenting the APIs.

## Disclaimers

This library is not associated with Vaillant or Netatmo in any way. If either Vaillant or Netatmo decide to change anything with the API, or block the usage outside of their first party apps, this library will stop working.
