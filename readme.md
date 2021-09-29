# httpx-file

Transport adapter fort __[httpx](https://github.com/encode/httpx)__ to allow
`file://` URI fetching in the local filesystem.


## Installation

<a href="https://pypi.org/project/httpx-file/"><pre>
pip install httpx-file
</pre></a>


## Usage

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
