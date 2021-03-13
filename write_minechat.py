import asyncio
import logging
import json
import socket

from socket_context import open_connection
from exceptions import InvalidToken
import gui


def clean_string(string: str):
    return string.replace('\\n', '')


async def register(username, writer, reader):
    writer.write(f"{clean_string(username)}\n\n".encode())
    await writer.drain()

    logging.info(await reader.readuntil(b'\n'))
    recieved_data = json.loads(await reader.readuntil(b'\n'))
    logging.info(recieved_data)

    return recieved_data


async def authorise(token, writer, reader):
    logging.info(await reader.readuntil(b'\n'))

    writer.write(f"{clean_string(token)}\n".encode())
    await writer.drain()

    recieved_data = json.loads(await reader.readuntil(b'\n'))
    logging.info(recieved_data)
    return recieved_data


async def submit_message(writer, message):
    writer.write(f"{clean_string(message)}\n\n".encode())
    await writer.drain()


async def write_tcp_connection(
    host: str,
    port: int,
    token: str,
    sending_queue: asyncio.Queue,
    status_queue: asyncio.Queue
) -> None:
    while True:
        try:
            async with open_connection(host, port) as connection:
                status_queue.put_nowait(gui.SendingConnectionStateChanged.ESTABLISHED)
                reader, writer = connection

                recieved_data = await authorise(token, writer, reader)
                if not recieved_data:
                    raise InvalidToken('Проверьте токен, сервер его не узнал.')

                await reader.readuntil(b'\n')
                event = gui.NicknameReceived(recieved_data['nickname'])
                status_queue.put_nowait(event)
                
                while True:
                    message = await sending_queue.get()
                    await submit_message(writer, message)
        except (TimeoutError, socket.gaierror):
            status_queue.put_nowait(gui.SendingConnectionStateChanged.INITIATED)
            await asyncio.sleep(10)
