import asyncio
import argparse
import json


async def dialogue(reader, writer):

    while True:
        message = input('Ваше сообщение: ')
        writer.write(f'{message}\n\n'.encode())
        await writer.drain()
        await reader.readline()


async def login(reader, writer, hash):

    await reader.readline()

    if hash:

        writer.write(f'{hash}\n'.encode())
        await writer.drain()
        await reader.readline()

    else:

        writer.write('\n'.encode())
        await writer.drain()
        await reader.readline()
        username = input('Введите ник: ')
        writer.write(f'{username}\n\n'.encode())
        await writer.drain()
        response_with_hash = await reader.readline()
        hash = json.loads(response_with_hash.decode())['account_hash']
        print(f'Ваш хеш: {hash}')


async def main(args):

    host = args.host
    port = args.port
    hash = args.hash

    reader, writer = await asyncio.open_connection(host=host, port=port)

    await login(reader, writer, hash)
    await dialogue(reader, writer)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='указать хост')
    parser.add_argument('--port', type=int, help='указать порт')
    parser.add_argument('--hash', help='указать хеш')
    args = parser.parse_args()

    asyncio.run(main(args))
