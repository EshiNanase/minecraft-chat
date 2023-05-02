import asyncio
import argparse


async def main(args):

    host = args.host[0]
    port = int(args.port[0])

    reader, writer = await asyncio.open_connection(host=host, port=port)
    await reader.readline()
    writer.write('\n'.encode())
    await writer.drain()
    await reader.readline()
    username = input('Введите ник: ')
    writer.write(f'{username}\n'.encode())
    await writer.drain()
    await reader.readline()

    while True:
        message = input('Ваше сообщение: ')
        writer.write(f'{message}\n'.encode())
        await writer.drain()
        await reader.readline()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', action='append', help='указать хост')
    parser.add_argument('--port', action='append', help='указать порт')
    args = parser.parse_args()

    asyncio.run(main(args))
