from typing import Any, Optional, List, Tuple, Mapping, NoReturn
from pathlib import Path

import httpx

__version__ = 0, 0, 1, 'dev0'


# monkey patch to fix httpx URL parsing
def is_relative_url(self):
    return not (self._uri_reference.scheme or self._uri_reference.host)


def is_absolute_url(self):
    return not self.is_relative_url


httpx.URL.is_relative_url = property(is_relative_url)
httpx.URL.is_absolute_url = property(is_absolute_url)


from httpx._utils import URLPattern
from httpx import (
    AsyncBaseTransport,
    BaseTransport,
    # TransportError,
    ByteStream,
    Client as _Client,
)


class FileTransport(AsyncBaseTransport, BaseTransport):
    '''A transport for file URIs.
    '''

    def handle_request(
        self,
        method:     bytes,
        url:        Tuple[bytes, bytes, Optional[int], bytes],
        headers:    List[Tuple[bytes, ...]],
        stream:     ByteStream,
        extensions: Mapping[str, Any],
    ) -> None:
        status = None
        scheme, host, port, path = url

        if host and host != 'localhost':
            raise NotImplementedError('Only local paths are allowed')
            status = 501  # Not Implemented

        if method in {b'PUT', b'DELETE'}:
            status = 501  # Not Implemented

        elif method not in {b'GET', b'HEAD'}:
            # raise TransportError(f'Invalid request method: {method}')
            status = 405  # Method Not Allowed

        if not status:
            parts = path.split(b'/')

            # check if it's a Windows absolute path
            if parts[1].endswith((b':', b'|')):
                parts[1] = parts[1][:-1] + b':'
                parts.pop(0)

            ospath = Path(b'/'.join(parts).decode())

            try:
                content = ospath.read_bytes()
                status = 200  # OK
            except FileNotFoundError:
                status = 404  # Not Found
            except PermissionError:
                status = 403  # Forbidden
            else:
                stream = ByteStream(content)
                headers.append((b'Content-Length', str(len(content)).encode()))

        extensions = {}
        return status, headers, stream, extensions

    async def handle_async_request(self, **kwargs) -> NoReturn:
        raise NotImplementedError


class Client(_Client):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.mount('file://', FileTransport())

    def mount(self, protocol: str, transport: BaseTransport) -> None:
        self._mounts.update({URLPattern(protocol): transport})


__all__ = ['FileTransport', 'Client']
