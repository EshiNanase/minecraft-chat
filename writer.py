import asyncio
import argparse
import logging
import aiofiles


async def write_down_account_info(account_info):
    async with aiofiles.open('account.txt', 'w', encoding='utf-8') as file:
        await file.write(account_info)


async def write_in_dialogue(reader, writer, debug):

    while True:
        message = input('Ваше сообщение: ').replace('\n', '')
        writer.write(f'{message}\n\n'.encode())
        await writer.drain()
        response = await reader.readline()
        if debug:
            logging.debug(response.decode())


async def login(reader, writer, hash, debug):

    writer.write(f'{hash}\n'.encode())
    await writer.drain()
    response = await reader.readline()

    if debug:
        logging.debug(response.decode())

    if 'null' in response.decode():
        writer.close()
        await writer.wait_closed()
        raise RuntimeError('Неверный хеш!')


async def register(reader, writer, debug):

    writer.write('\n'.encode())
    await writer.drain()
    response = await reader.readline()
    if debug:
        logging.debug(response.decode())

    username = input('Введите ник: ').replace('\n', '')
    writer.write(f'{username}\n\n'.encode())
    await writer.drain()

    response = await reader.readline()
    if debug:
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

    reader, writer = await asyncio.open_connection(host=host, port=port)
    await reader.readline()

    if hash:
        await login(reader, writer, hash, debug)
    else:
        await register(reader, writer, debug)

    await write_in_dialogue(reader, writer, debug)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='указать хост')
    parser.add_argument('--port', type=int, help='указать порт')
    parser.add_argument('--hash', help='указать хеш')
    parser.add_argument('--debug', action='store_true', help='указать включен/выключен дебаг сообщений в консоль')
    args = parser.parse_args()

    asyncio.run(main(args))
