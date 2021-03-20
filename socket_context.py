import asyncio
import platform
import socket
from contextlib import asynccontextmanager

from exceptions import UnavailableOS


def set_keepalive_linux(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)


def set_keepalive_osx(sock, interval_sec=3, max_fails=5):
    TCP_KEEPALIVE = 0x10
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, TCP_KEEPALIVE, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)


@asynccontextmanager
async def open_connection(host, port):
    sock = socket.create_connection((host, port))

    os_name = platform.system()

    if os_name == 'Linux':
        set_keepalive_linux(sock, 1, 1, 1)
    elif os_name == 'Darwin':
        set_keepalive_osx(sock, 1, 1)
    else:
        raise UnavailableOS('Script works only on Linux/MacOS')
    
    reader, writer = await asyncio.open_connection(sock=sock)
    
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()
