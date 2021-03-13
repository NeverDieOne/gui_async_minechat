import asyncio
import argparse
import os

from dotenv import load_dotenv

from listen_minechat import listen_tcp_connection
import gui


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Read messages from TCP connection')
    parser.add_argument('--port', default=os.getenv('LISTEN_PORT') or 5000, help='Port to connection')
    parser.add_argument('--host', default=os.getenv('HOST') or 'minechat.dvmn.org', help='Host to connection')
    parser.add_argument('--file', default=os.getenv('OUTPUT_FILE') or 'output.txt', help='Output file with chat')
    return parser.parse_args()


async def main():
    load_dotenv()
    args = get_args()

    message_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()


    await asyncio.gather(
        listen_tcp_connection(args.host, args.port, message_queue),
        gui.draw(message_queue, sending_queue, status_updates_queue)
    )


if __name__ == '__main__':
    asyncio.run(main())
