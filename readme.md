# httpx-file

Transport adapter fort __[httpx](https://github.com/encode/httpx)__ to allow
`file://` URI fetching in the local filesystem.


## Installation

<a href="https://pypi.org/project/httpx-file/"><pre>
pip install httpx-file
</pre></a>


## Usage (synchronous approach)

_httpx-file_ subclasses `httpx.Client`, so you can just replace `httpx.Client`
with `httpx_file.Client` to get the same behavior with added `file://` protocol
support.

```python
from httpx_file import Client

client = Client()
client.get('file:///etc/fstab)
```

Or you can also mount `FileTransport` in a `httpx.Client` instance.

```python
from httpx_file import FileTransport
from httpx import Client

client = Client(mounts={'file://': FileTransport()})
client.get('file:///etc/fstab)
```

## Usage (asynchronous approach)

It is also possible to use _httpx-file_ possibilities asynchronous way. 
To do this, you can just replace 'httpx.AsyncClient' with 'httpx_file.AsyncClient'.

```python
from httpx_file import AsyncClient

# Taken from tests/test_transport.py

from pathlib import Path

THIS = Path(__file__)

async def test_async_client():
    async_client = AsyncClient()
    async_response = await async_client.get(THIS.as_uri())

    assert async_response.content == THIS.read_bytes()
```