import asyncio
import argparse
import datetime
import os
import socket
import sys

from dotenv import load_dotenv
import aiofiles

from socket_context import open_connection


async def get_message(reader):
    data = await reader.readline()
    time_now = datetime.datetime.now()
    formated_time = time_now.strftime('%e.%m.%Y %H:%M:%S')
    return f"[{formated_time}] {data.decode()}"


async def listen_tcp_connection(host, port, filename):
    while True:
        try:
            async with open_connection(host, port) as connection:
                reader, writer = connection
                async with aiofiles.open(filename, mode='a') as file:
                    while True:
                        message = await get_message(reader)
                        await file.write(message)
        except (TimeoutError, socket.gaierror):
            print(
                'Потеряно соединение с сетью, попытка переподключения через 10 сек',
                file=sys.stderr
            )
            await asyncio.sleep(10)
                    

if __name__ == '__main__':
    load_dotenv()

    parser = argparse.ArgumentParser(description='Read messages from TCP connection')
    parser.add_argument('--port', default=os.getenv('LISTEN_PORT') or 5000, help='Port to connection')
    parser.add_argument('--host', default=os.getenv('HOST') or 'minechat.dvmn.org', help='Host to connection')
    parser.add_argument('--file', default=os.getenv('OUTPUT_FILE') or 'output.txt', help='Output file with chat')
    args = parser.parse_args()

    asyncio.run(listen_tcp_connection(args.host, args.port, args.file))
