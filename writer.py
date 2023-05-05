import asyncio
import argparse
import logging
import aiofiles
from context_manager import open_socket
from functools import partial
from requests import ConnectionError
import time

MAX_RECONNECT_ATTEMPTS = 3


async def authorize(reader, writer, hash):

    await reader.readline()

    if hash:
        await login(reader, writer, hash)
    else:
        await register(reader, writer)

    writer.write(f'\n'.encode())
    await writer.drain()
    await reader.readline()

    return True


async def connect_endlessly(open_socket_function, authorize_function):
    attempts = 0

    while True:

        try:
            async with open_socket_function() as streamers:
                reader, writer = streamers

                if await authorize_function(reader, writer):
                    await write_in_chat(reader, writer)

        except ConnectionError:
            print('Соединение нарушено!')
            if attempts < MAX_RECONNECT_ATTEMPTS:
                print('Попытка восстановить соединение...')
                time.sleep(15)
                attempts += 1
            else:
                raise RuntimeError('Невозможно установить соединение')


async def write_down_account_info(account_info):
    async with aiofiles.open('account.txt', 'w', encoding='utf-8') as file:
        await file.write(account_info)


async def write_in_chat(reader, writer):

    while True:

        message = input('Ваше сообщение: ').replace(r'\n', '')
        writer.write(f'{message}\n\n'.encode())
        await writer.drain()
        response = await reader.readline()
        logging.debug(response.decode())


async def login(reader, writer, hash):

    writer.write(f'{hash}\n'.encode())
    await writer.drain()
    response = await reader.readline()

    logging.debug(response.decode())

    if 'null' in response.decode():
        raise RuntimeError('Неверный хеш!')


async def register(reader, writer):

    writer.write('\n'.encode())
    await writer.drain()
    response = await reader.readline()
    logging.debug(response.decode())

    username = input('Введите ник: ').replace('\n', '')
    writer.write(f'{username}\n\n'.encode())
    await writer.drain()
    response = await reader.readline()
    logging.debug(response.decode())

    await write_down_account_info(response.decode())
    print(f'Ваша информация об аккаунте была записана в account.txt!')


async def main(args):

    host = args.host
    port = args.port
    hash = args.hash
    debug = args.debug

    if debug:
        logging.basicConfig(level=logging.DEBUG)

    authorize_function = partial(authorize, hash=hash)
    open_socket_function = partial(open_socket, host=host, port=port)
    await connect_endlessly(open_socket_function, authorize_function)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='указать хост', default='minechat.dvmn.org')
    parser.add_argument('--port', type=int, help='указать порт', default=5050)
    parser.add_argument('--hash', help='указать хеш')
    parser.add_argument('--debug', action='store_true', help='указать включен/выключен дебаг сообщений в консоль')
    args = parser.parse_args()

    asyncio.run(main(args))
