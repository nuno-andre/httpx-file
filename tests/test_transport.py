from pathlib import Path

import pytest

from httpx_file import Client, AsyncClient, FileTransport

THIS = Path(__file__)


def test_client():
    client = Client()

    assert client.get(THIS.as_uri()).content == THIS.read_bytes()


def test_adapter():
    mounts = {'file://': FileTransport()}
    client = Client(mounts=mounts)

    assert client.get(THIS.as_uri()).content == THIS.read_bytes()


@pytest.mark.asyncio
async def test_async_client():
    async_client = AsyncClient()
    async_response = await async_client.get(THIS.as_uri())

    assert async_response.content == THIS.read_bytes()


@pytest.mark.asyncio
async def test_async_adapter():
    mounts = {'file://': FileTransport()}
    async_client = AsyncClient(mounts=mounts)
    async_response = await async_client.get(THIS.as_uri())

    assert async_response.content == THIS.read_bytes()
