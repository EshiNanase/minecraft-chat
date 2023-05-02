import asyncio
import aiofiles
from datetime import datetime
import argparse


async def main(args):

    host = args.host[0]
    port = int(args.port[0])
    history = args.history

    reader, writer = await asyncio.open_connection(host=host, port=port)
    if history:
        async with aiofiles.open('data.txt', 'a', encoding='utf-8') as file:
            await file.write(f'[{datetime.now().strftime("%d.%m.%y %H:%M")}] Установлено соединение\n')
    try:
        while True:
            data = await reader.readline()
            data_decoded = data.decode()
            print(data_decoded)
            if history:
                async with aiofiles.open('data.txt', 'a', encoding='utf-8') as file:
                    await file.write(f'[{datetime.now().strftime("%d.%m.%y %H:%M")}] {data_decoded}')
    except UnicodeDecodeError:
        writer.close()
        await writer.wait_closed()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', action='append', help='указать хост')
    parser.add_argument('--port', action='append', help='указать порт')
    parser.add_argument('--history', action='store_true', help='включить/выключить запись переписки')
    args = parser.parse_args()

    asyncio.run(main(args))
