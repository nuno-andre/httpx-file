from pathlib import Path
from httpx_file import Client, FileTransport
from httpx import Client as HttpxClient

THIS = Path(__file__)


def test_client():
    client = Client()

    assert client.get(THIS.as_uri()).content == THIS.read_bytes()


def test_adapter():
    mounts = {'file://': FileTransport()}
    client = HttpxClient(mounts=mounts)

    assert client.get(THIS.as_uri()).content == THIS.read_bytes()
