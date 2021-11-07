#!/usr/bin/env python3

import asyncio
import os

from httpx import AsyncClient
from dotenv import load_dotenv

from src.vaillant_netatmo_api import AuthClient, ThermostatClient, TokenStore, SetpointMode

load_dotenv()

client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
username = os.environ['USERNAME']
password = os.environ['PASSWORD']
user_prefix = os.environ['USER_PREFIX']
app_version = os.environ['APP_VERSION']

async def main():
    async with AsyncClient() as client:
        token_store = TokenStore(
            client_id,
            client_secret,
            None,
            handle_token_update
        )
        await async_get_token(client, token_store)
        await async_call_api(client, token_store)

def handle_token_update(token):
    ...

async def async_get_token(client, token_store):
    client = AuthClient(client, token_store)

    await client.async_token(
        username,
        password,
        user_prefix,
        app_version
    )

async def async_call_api(client, token_store):
    client = ThermostatClient(client, token_store)

    devices = await client.async_get_thermostats_data()

    d_id = devices[0].id
    m_id = devices[0].modules[0].id

    await client.async_set_minor_mode(d_id, m_id, SetpointMode.MANUAL, False)

if __name__ == "__main__":
    asyncio.run(main())