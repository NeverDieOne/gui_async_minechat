import argparse
import asyncio
import logging
import os
import socket
import time
from tkinter import messagebox

from anyio import ExceptionGroup, create_task_group, run
from async_timeout import timeout
from dotenv import load_dotenv

import gui
import listen_minechat
import write_minechat
from exceptions import InvalidToken

watchdog_logger = logging.getLogger('watchdog_logger')


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='GUI for Minechat')
    parser.add_argument(
        '--l_port',
        default=os.getenv('LISTEN_PORT') or 5000,
        type=int,
        help='Port to read messages'
    )
    parser.add_argument(
        '--w_port',
        default=os.getenv('WRITE_PORT') or 5050,
        type=int,
        help='Port to wrtie messages'
    )
    parser.add_argument(
        '--host',
        default=os.getenv('HOST') or 'minechat.dvmn.org',
        help='Host to connection'
    )
    parser.add_argument(
        '--file',
        default=os.getenv('OUTPUT_FILE') or 'output.txt',
        help='Output file with chat'
    )
    parser.add_argument(
        '--token',
        default=os.getenv('MINECHAT_TOKEN'),
        help='Token to connect'
    )
    parser.add_argument(
        '--username',
        default=os.getenv('MINECHAT_USERNAME') or 'JustName',
        help='Username to connect'
    )

    args = parser.parse_args()
    if not args.token:
        raise InvalidToken('Token is required argument')

    return args


async def handle_connection(
    args: argparse.Namespace,
    message_queue: asyncio.Queue,
    sending_queue: asyncio.Queue,
    file_queue: asyncio.Queue,
    watchdog_queue: asyncio.Queue,
    status_queue: asyncio.Queue
) -> None:
    while True:
        try:
            async with create_task_group() as tg:
                await tg.spawn(
                    listen_minechat.listen_tcp_connection,
                    args.host,
                    args.l_port,
                    message_queue,
                    file_queue,
                    status_queue,
                    watchdog_queue
                )
                await tg.spawn(
                    write_minechat.write_tcp_connection,
                    args.host,
                    args.w_port, 
                    args.token,
                    sending_queue,
                    status_queue, 
                    watchdog_queue
                )
                await tg.spawn(
                    watch_for_connection,
                    watchdog_queue, 
                    sending_queue
                )
        except (ConnectionError, socket.gaierror, ExceptionGroup):
            logging.info('Some trouble with connecion')
            await asyncio.sleep(10)


async def watch_for_connection(
    watchdog_queue: asyncio.Queue,
    sending_queue: asyncio.Queue
) -> None:
    while True:
        sending_queue.put_nowait('')
        timestamp = int(time.time())
        time_out = 2
        try:
            async with timeout(time_out):
                message = await watchdog_queue.get()
                watchdog_logger.info(f'[{timestamp}] {message}')
        except asyncio.exceptions.TimeoutError:
            watchdog_logger.info(
                f'[{timestamp}] {time_out}s timeout is elapsed'
            )
            raise ConnectionError
        await asyncio.sleep(1)


async def main():
    load_dotenv()
    args = get_args()

    logging.basicConfig(level=logging.DEBUG)

    message_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    file_queue = asyncio.Queue()
    watchdog_queue = asyncio.Queue()

    try:
        async with create_task_group() as tg:
            await tg.spawn(
                listen_minechat.save_messages,
                args.file,
                message_queue,
                file_queue
            )
            await tg.spawn(
                handle_connection,
                args,
                message_queue,
                sending_queue,
                file_queue,
                watchdog_queue,
                status_updates_queue
            )
            await tg.spawn(
                gui.draw,
                message_queue,
                sending_queue,
                status_updates_queue
            )
    except InvalidToken:
        messagebox.showwarning(
            'Неверный токен', 'Проверьте токен, сервер его не узнал.'
        )
    except (KeyboardInterrupt, gui.TkAppClosed):
        pass


if __name__ == '__main__':
    run(main)
