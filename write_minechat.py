import asyncio
import json
import logging

import gui
from exceptions import InvalidToken
from socket_context import open_connection
from status_context import manage_status


def clean_string(string: str) -> str:
    return string.replace('\\n', '')


async def authorise(
    token: str,
    writer: asyncio.StreamWriter,
    reader: asyncio.StreamReader
) -> dict:
    logging.info(await reader.readuntil(b'\n'))

    writer.write(f"{clean_string(token)}\n".encode())
    await writer.drain()

    recieved_data = json.loads(await reader.readuntil(b'\n'))
    logging.info(recieved_data)
    return recieved_data


async def submit_message(writer: asyncio.StreamWriter, message: str) -> None:
    writer.write(f"{clean_string(message)}\n\n".encode())
    await writer.drain()


async def write_tcp_connection(
    host: str,
    port: int,
    token: str,
    sending_queue: asyncio.Queue,
    status_queue: asyncio.Queue,
    watchdog_queue: asyncio.Queue
) -> None:
    async with manage_status(status_queue, gui.SendingConnectionStateChanged):
        async with open_connection(host, port) as connection:
            reader, writer = connection

            watchdog_queue.put_nowait('Prompt before auth')
            recieved_data = await authorise(token, writer, reader)
            watchdog_queue.put_nowait('Authorization done')
            if not recieved_data:
                raise InvalidToken('Проверьте токен, сервер его не узнал.')

            await reader.readuntil(b'\n')
            event = gui.NicknameReceived(recieved_data['nickname'])
            status_queue.put_nowait(event)
            
            while True:
                message = await sending_queue.get()
                await submit_message(writer, message)
                watchdog_queue.put_nowait('Message sent')
