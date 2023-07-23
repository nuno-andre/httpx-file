from typing import Optional, Tuple
from pathlib import Path

import aiofiles
import httpx

__version__ = 0, 2, 0


# monkey patch to fix httpx URL parsing
def is_relative_url(self):
    return not (self._uri_reference.scheme or self._uri_reference.host)


def is_absolute_url(self):
    return not self.is_relative_url


httpx.URL.is_relative_url = property(is_relative_url)  # type: ignore
httpx.URL.is_absolute_url = property(is_absolute_url)  # type: ignore

from httpx._utils import URLPattern
from httpx import (
    AsyncBaseTransport,
    BaseTransport,
    ByteStream,
    Client as _Client,
    AsyncClient as _AsyncClient,
    Request,
    Response,
)


class FileTransport(AsyncBaseTransport, BaseTransport):
    '''Transport for file URIs.
    '''

    def _handle(self, request: Request) -> Tuple[Optional[int], httpx.Headers]:

        if request.url.host and request.url.host != 'localhost':
            raise NotImplementedError('Only local paths are allowed')

        if request.method in {'PUT', 'DELETE'}:
            status = 501  # Not Implemented

        elif request.method not in {'GET', 'HEAD'}:
            # raise TransportError(f'Invalid request method: {method}')
            status = 405  # Method Not Allowed

        else:
            status = None

        return status, request.headers

    def handle_request(self, request: Request) -> Response:
        status, headers = self._handle(request)
        stream = None

        if not status:
            parts = request.url.path.split('/')

            # check if it's a Windows absolute path
            if parts[1].endswith((':', '|')):
                parts[1] = parts[1][:-1] + ':'
                parts.pop(0)

            ospath = Path('/'.join(parts))

            try:
                content = ospath.read_bytes()
                status = 200  # OK
            except FileNotFoundError:
                status = 404  # Not Found
            except PermissionError:
                status = 403  # Forbidden
            else:
                stream = ByteStream(content)
                headers['Content-Length'] = str(len(content))

        return Response(
            status_code=status,
            headers=headers,
            stream=stream,
            extensions=dict(),
        )

    async def handle_async_request(self, request: Request) -> Response:
        status, headers = self._handle(request)
        stream = None

        if not status:
            parts = request.url.path.split('/')

            # check if it's a Windows absolute path
            if parts[1].endswith((':', '|')):
                parts[1] = parts[1][:-1] + ':'
                parts.pop(0)

            ospath = Path('/'.join(parts))

            try:
                async with aiofiles.open(ospath, mode='rb') as f:
                    content = await f.read()
                status = 200  # OK
            except FileNotFoundError:
                status = 404  # Not Found
            except PermissionError:
                status = 403  # Forbidden
            else:
                stream = ByteStream(content)
                headers['Content-Length'] = str(len(content))

        return Response(
            status_code=status,
            headers=headers,
            stream=stream,
            extensions=dict(),
        )


class Client(_Client):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.mount('file://', FileTransport())

    def mount(self, protocol: str, transport: BaseTransport) -> None:
        self._mounts.update({URLPattern(protocol): transport})


class AsyncClient(_AsyncClient):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.mount('file://', FileTransport())

    def mount(self, protocol: str, transport: AsyncBaseTransport) -> None:
        self._mounts.update({URLPattern(protocol): transport})


__all__ = ['FileTransport', 'AsyncClient', 'Client']
