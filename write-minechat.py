import argparse
import asyncio
import logging
import json
import os

from dotenv import load_dotenv

from socket_context import open_connection


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


async def write_to_tcp_connection(arguments):
    async with open_connection(arguments.host, arguments.port) as connection:
        reader, writer = connection

        token = arguments.token or input('Введи token: ')

        recieved_data = await authorise(token, writer, reader)

        if not recieved_data:
            print('Неизвестный токен. Регистрируем новый.')
            username = arguments.username or input('Введи желаемый nickname: ')
            recieved_data = await register(arguments.username, writer, reader)
            print(f'Запомни свой токен: {recieved_data["account_hash"]}')

        await reader.readuntil(b'\n')
        print(f'Добро пожаловать в чат {recieved_data["nickname"]}')

        message = arguments.text or input('>> ')
        await submit_message(writer, message)


if __name__ == '__main__':
    load_dotenv()

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Write messages to TCP connection')
    parser.add_argument('--token', default=os.getenv('MINECHAT_TOKEN'), help='Token to connect')
    parser.add_argument('--text', help='Text message to write in chat')
    parser.add_argument('--host', default=os.getenv('HOST') or 'minechat.dvmn.org', help='Host to connection')
    parser.add_argument('--port', default=os.getenv('WRITE_PORT') or 5050, help='Port to connection')
    parser.add_argument('--username', default=os.getenv('MINECHAT_USERNAME') or 'JustName', help='Username to connect')
    args = parser.parse_args()

    asyncio.run(write_to_tcp_connection(args))
