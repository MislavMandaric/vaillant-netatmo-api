#!/usr/bin/env python3

import asyncio
from datetime import datetime, timedelta
import os

from dotenv import load_dotenv
from src.vaillant_netatmo_api import AuthClient, ThermostatClient, SetpointMode

load_dotenv()

client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
username = os.environ['USERNAME']
password = os.environ['PASSWORD']
user_prefix = os.environ['USER_PREFIX']
app_version = os.environ['APP_VERSION']

async def main():
    token = await async_get_token()
    await async_call_api(token)

async def async_get_token():
    client = AuthClient(
        client_id,
        client_secret,
        "read_thermostat write_thermostat"
    )

    try:
        return await client.async_get_token(
            username,
            password,
            user_prefix,
            app_version
            )
    except Exception as e:
        print(e)
    finally:
        await client.async_close()

async def async_call_api(token):
    client = ThermostatClient(
        client_id,
        client_secret,
        token,
        update_token
    )

    try:
        devices = await client.async_get_thermostats_data()

        d_id = devices[0].id
        m_id = devices[0].modules[0].id

        await client.async_set_minor_mode(d_id, m_id, SetpointMode.MANUAL, False)
    except Exception as e:
        print(e.response.text)
    finally:
        await client.async_close()

async def update_token(token):
    return

if __name__ == "__main__":
    asyncio.run(main())