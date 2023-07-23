from pathlib import Path

import aiofiles
import httpx

__version__ = 0, 0, 3


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
    AsyncClient as _AsyncClient, Request, Response
)


class FileTransport(BaseTransport):
    """Transport for file URIs."""

    def handle_request(
            self,
            request: Request) -> None:
        status = None
        headers = request.headers
        method = request.method
        scheme, host, port, path = request.url.scheme, request.url.host, request.url.port, request.url.path

        if host and host != 'localhost':
            raise NotImplementedError('Only local paths are allowed')

        if method in ['PUT', 'DELETE']:
            status = 501  # Not Implemented

        elif method not in ['GET', 'HEAD']:
            # raise TransportError(f'Invalid request method: {method}')
            status = 405  # Method Not Allowed

        if not status:
            parts = path.split('/')

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
        extensions = {}
        return Response(status_code=status, headers=headers, stream=stream, extensions=extensions)


class AsyncFileTransport(AsyncBaseTransport):

    async def handle_async_request(
            self,
            request: Request) -> None:
        status = None
        headers = request.headers
        method = request.method
        scheme, host, port, path = request.url.scheme, request.url.host, request.url.port, request.url.path

        if host and host != 'localhost':
            raise NotImplementedError('Only local paths are allowed')

        if method in ['PUT', 'DELETE']:
            status = 501  # Not Implemented

        elif method not in ['GET', 'HEAD']:
            # raise TransportError(f'Invalid request method: {method}')
            status = 405  # Method Not Allowed

        if not status:
            parts = path.split('/')

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
        extensions = {}
        return Response(status_code=status, headers=headers, stream=stream, extensions=extensions)


class Client(_Client):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.mount('file://', FileTransport())

    def mount(self, protocol: str, transport: BaseTransport) -> None:
        self._mounts.update({URLPattern(protocol): transport})


class AsyncClient(_AsyncClient):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.mount('file://', AsyncFileTransport())

    def mount(self, protocol: str, transport: AsyncBaseTransport) -> None:
        self._mounts.update({URLPattern(protocol): transport})


__all__ = ['FileTransport', 'AsyncFileTransport', 'AsyncClient', 'Client']
