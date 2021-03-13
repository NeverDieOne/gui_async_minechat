import asyncio
import argparse
import os
import logging
from tkinter import messagebox

from dotenv import load_dotenv

import listen_minechat
import write_minechat
import gui
from exceptions import InvalidToken


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Read messages from TCP connection')
    parser.add_argument('--l_port', default=os.getenv('LISTEN_PORT') or 5000, type=int, help='Port to read messages')
    parser.add_argument('--w_port', default=os.getenv('WRITE_PORT') or 5050, type=int, help='Port to wrtie messages')
    parser.add_argument('--host', default=os.getenv('HOST') or 'minechat.dvmn.org', help='Host to connection')
    parser.add_argument('--file', default=os.getenv('OUTPUT_FILE') or 'output.txt', help='Output file with chat')
    parser.add_argument('--token', default=os.getenv('MINECHAT_TOKEN'), help='Token to connect')
    parser.add_argument('--text', help='Text message to write in chat')
    parser.add_argument('--username', default=os.getenv('MINECHAT_USERNAME') or 'JustName', help='Username to connect')
    return parser.parse_args()


async def main():
    load_dotenv()
    args = get_args()

    logging.basicConfig(level=logging.DEBUG)

    message_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    file_queue = asyncio.Queue()


    try:
        await asyncio.gather(
            listen_minechat.listen_tcp_connection(args.host, args.l_port, message_queue, file_queue, status_updates_queue),
            listen_minechat.save_messages(args.file, message_queue, file_queue),
            write_minechat.write_tcp_connection(args.host, args.w_port, args.token, sending_queue, status_updates_queue),
            gui.draw(message_queue, sending_queue, status_updates_queue),
        )
    except InvalidToken as e:
        messagebox.showwarning('Неверный токен', 'Проверьте токен, сервер его не узнал.')


if __name__ == '__main__':
    asyncio.run(main())
