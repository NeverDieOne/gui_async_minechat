import argparse
import asyncio
import contextlib
import json
import logging
import os
import tkinter as tk

import aiofiles
from anyio import create_task_group, run

from gui import TkAppClosed
from socket_context import open_connection
from write_minechat import clean_string


async def register(
    host: str,
    port: int,
    username: str,
) -> str:
    async with open_connection(host, port) as connection:
        reader, writer = connection

        await reader.readuntil(b'\n')
        writer.write(b'\n')
        await reader.readuntil(b'\n')

        writer.write(f"{clean_string(username)}\n\n".encode())
        await writer.drain()

        recieved_data = json.loads(await reader.readuntil(b'\n'))
        return recieved_data['account_hash']


async def register_handler(
    host: str,
    port: int,
    filename: str,
    register_queue: asyncio.Queue
) -> None:
    async with aiofiles.open(filename, mode='a') as file:
        while True:
            username = await register_queue.get()
            account_hash = await register(host, port, username)
            await file.write(f'{username}: {account_hash}')
            logging.info(f'Пользователь {username} зарегистрирован')
            await asyncio.sleep(1)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Register in Minechat')
    parser.add_argument('--host', default=os.getenv('HOST') or 'minechat.dvmn.org', help='Host to connection')
    parser.add_argument('--port', default=os.getenv('WRITE_PORT') or 5050, type=int, help='Port to connection')
    parser.add_argument('--output', default='register.txt', help='File to write register data')
    return parser.parse_args()


def process_register(input_field: tk.Entry, register_queue: asyncio.Queue) -> None:
    username = input_field.get()
    register_queue.put_nowait(username)
    input_field.delete(0, tk.END)


def create_gui(register_queue: asyncio.Queue) -> tk.Frame:
    root = tk.Tk()
    
    root.title('Регистрация')

    root_frame = tk.Frame()
    root_frame.pack(fill='both', expand=True)

    input_frame = tk.Frame(root_frame)
    input_frame.pack(side='bottom', fill=tk.X)

    input_field = tk.Entry(input_frame)
    input_field.pack(side="left", fill=tk.X, expand=True)

    input_field.bind("<Return>", lambda event: process_register(input_field, register_queue))

    send_button = tk.Button(input_frame)
    send_button["text"] = "Отправить"
    send_button["command"] = lambda: process_register(input_field, register_queue)
    send_button.pack(side="left")

    return root_frame


async def update_tk(root_frame, interval=1 / 120):
    while True:
        try:
            root_frame.update()
        except tk.TclError:
            raise TkAppClosed()
        await asyncio.sleep(interval)


async def main():
    args = get_args()
    register_queue = asyncio.Queue()
    root_frame = create_gui(register_queue)
    
    with contextlib.suppress(KeyboardInterrupt, TkAppClosed):
        async with create_task_group() as tg:
            await tg.spawn(update_tk, root_frame)
            await tg.spawn(register_handler, args.host, args.port, args.output, register_queue)


if __name__ == '__main__':
    run(main)
