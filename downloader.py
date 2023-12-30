import messages
import socket
import asyncio


def start_async_download(peers):
    asyncio.run(download_from_peers(peers))


async def download_from_peers(peers):

    for peer in peers:
        




async def download(peer):
    print(peer)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect(peer)
    sock.listen()

    while True:
        await asyncio.sleep(1)
        data = sock.recv(1024)
        if not data:
            break
        print(data)
    print("konieeec")