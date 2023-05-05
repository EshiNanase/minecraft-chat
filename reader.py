import asyncio
import time
import aiofiles
from datetime import datetime
import argparse
from context_manager import open_socket
from requests import ConnectionError
from functools import partial

MAX_RECONNECT_ATTEMPTS = 3


async def log(text, history):

    if history:
        async with aiofiles.open(args.history, 'a', encoding='utf-8') as file:
            await file.write(f'[{datetime.now().strftime("%d.%m.%y %H:%M")}] {text}\n')


async def connect_endlessly(open_socket_function, log_function):
    attempts = 0
    while True:

        try:
            async with open_socket_function() as streamers:
                reader = streamers[0]
                await read_chat(reader, log_function)

        except ConnectionError:
            log_function('Соединение нарушено!')
            if attempts < MAX_RECONNECT_ATTEMPTS:
                await log_function('Попытка восстановить соединение...')
                time.sleep(15)
                attempts += 1
            else:
                await log_function('Невозможно установить соединение!')
                raise RuntimeError('Невозможно установить соединение')


async def read_chat(reader, log_function):

    await log_function('Установлено соединение!')
    try:
        while True:
            data = await reader.readline()
            data_decoded = data.decode()
            print(data_decoded)
            await log_function(f'{data_decoded}')

    except ConnectionError:
        await log_function('Соединение прервано!')


async def main(args):

    host = args.host
    port = args.port
    history = args.history

    log_function = partial(log, history=history)
    open_socket_function = partial(open_socket, host=host, port=port)

    await connect_endlessly(open_socket_function, log_function)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='указать хост', default='minechat.dvmn.org')
    parser.add_argument('--port', type=int, help='указать порт', default=5000)
    parser.add_argument('--history', help='указать будет ли запись переписки и куда')
    args = parser.parse_args()

    asyncio.run(main(args))
