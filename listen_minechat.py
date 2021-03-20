import asyncio
import datetime
from pathlib import Path

import aiofiles

from socket_context import open_connection


async def get_message(reader: asyncio.StreamReader) -> str:
    data = await reader.readline()
    time_now = datetime.datetime.now()
    formated_time = time_now.strftime('%e.%m.%Y %H:%M:%S')
    return f"[{formated_time}] {data.decode()}"


async def listen_tcp_connection(
    host: str,
    port: int,
    message_queue: asyncio.Queue,
    file_queue: asyncio.Queue,
    watchdog_queue: asyncio.Queue
) -> None:
    async with open_connection(host, port) as connection:
        reader, writer = connection
        while True:
            message = await get_message(reader)
            message_queue.put_nowait(message.strip())
            file_queue.put_nowait(message)
            watchdog_queue.put_nowait('New message in chat')


async def save_messages(filepath, message_queue: asyncio.Queue, file_queue: asyncio.Queue) -> None:
    Path(filepath).touch(exist_ok=True)

    async with aiofiles.open(filepath, mode='r+') as file:
        content = await file.read()
        message_queue.put_nowait(content.strip())

        while True:
            message = await file_queue.get()
            await file.write(message)
