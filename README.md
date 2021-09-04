# vaillant-netatmo-api

[![GitHub version](https://badge.fury.io/gh/MislavMandaric%2Fvaillant-netatmo-api.svg)](https://badge.fury.io/gh/MislavMandaric%2Fvaillant-netatmo-api)
[![PyPI version](https://badge.fury.io/py/vaillant-netatmo-api.svg)](https://badge.fury.io/py/vaillant-netatmo-api)
![Tests](https://github.com/MislavMandaric/vaillant-netatmo-api/actions/workflows/tests.yml/badge.svg)


## General

Python 3 library for managing Vaillant thermostats using the Netatmo API. It provides one-to-one mapping with Vaillant's Netatmo API and offeres similar functionality as the official Vaillant vSMART/eRELAX app.

## Installation

Library can be simply installed using pip.

```bash
pip install vaillant-netatmo-api
```

Library requires Python 3 and has [authlib](https://github.com/lepture/authlib) and [httpx](https://github.com/encode/httpx) dependencies.

> NOTE: Both authlib and httpx are prerelease software. The versions outlined in the `requirements.txt` should be working properly, but if there are some breaking changes, please check their Github issue tracker for known issues.

## Usage

### Getting the token from the OAuth API

All Netatmo APIs are protected and require a bearer token to authenticate. To get this token, Netatmo offers an OAuth API.

Since Vaillant uses Resource Owner Password Credentials Grant, there is only one method in the `AuthClient` API:

* `async_get_token`: getting a bearer token

```python
from vaillant_netatmo_api import serialize_token, auth_client

CLIENT_ID = ""
CLIENT_SECRET = ""
SCOPE = ""

with auth_client(CLIENT_ID, CLIENT_SECRET, SCOPE) as client:
    token = await client.async_get_token(
        username,
        password,
        user_prefix,
        app_version,
    )

    token_string = serialize_token(token)
    write_to_storage(token_string)
```

### Accessing the Thermostat API

There are three APIs available for the `ThermostatClient`, all of which require the bearer token for authentication:

* `async_get_thermostats_data`: getting all the devices associated with the user account
* `async_set_system_mode`: changing system mode for a device and module (ie. summer, winter or frostguard)
* `async_set_minor_mode`: changing minor mode for a device and module (ie. manual mode, away mode or hot water boost mode)

```python
from vaillant_netatmo_api import deserialize_token, thermostat_client, SystemMode

CLIENT_ID = ""
CLIENT_SECRET = ""

token_string = read_from_storage()
token = deserialize_token(token_string)

def update_token(token, access_token, refresh_token):
    token_string = serialize_token(token)
    write_to_storage(token_string)

with thermostat_client(CLIENT_ID, CLIENT_SECRET, token, update_token) as client:
    devices = await client.async_get_thermostats_data()

    d_id = devices[0].id
    m_id = devices[0].modules[0].id

    await client.async_set_system_mode(d_id, m_id, SystemMode.WINTER)
```

### Using clients as singletons

Even though library offers context manager for using `AuthClient` and `ThermostatClient`, this should only be done during development or in very infrequent usage scenarios.

Both of the clients use `httpx.AsyncClient` as the underlying HTTP communication library, which implements connection pooling and connection reuse. This means doing multiple concurent requests should be done by using the same instance of the `AuthClient` or `ThermostatClient`, which is not possible by using the context manager API since this API will return new instance of the client every time `auth_client` or `thermostat_client` method is called.

To achieve optimal usage, which will utilize connection pooling and connection reuse, both `AuthClient` and `ThermostatClient` should be used either as singletons in the application, or with some other context management mechanism, with the context wider than one block of code or one inbound request.

Here is an example for usage in Home Assistant.

```python
# When setting up integration with all the devices of one account, instantiate and store the client in a configuration memory store
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = ThermostatClient(
        entry.data[CONF_CLIENT_ID],
        entry.data[CONF_CLIENT_SECRET],
        token,
        async_token_updater,
    )

    hass.data[DOMAIN][entry.entry_id] = client
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True

# When unloading the integration of this same account, read the client and close it manually
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        client: ThermostatClient = hass.data[DOMAIN].pop(entry.entry_id)
        await client.async_close()

    return unload_ok
```

Similar hooks which represent some kind of application context should be used when integrating this library into a differnt application (Flask, Django or similar).

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