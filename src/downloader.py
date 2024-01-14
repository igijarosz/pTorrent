import os

from src import messages
from src import que
from src import piece
import asyncio
import math

def download_from_peers(torrent, peers):
    asyncio.run(create_download_tasks(torrent, peers))

async def create_download_tasks(torrent, peers):
    pieces = piece.Piece(torrent)

    if not os.path.exists("download"):
        os.mkdir("download")
    file = open(f"download/{str(torrent[b'info'][b'name'], 'utf-8')}", "wb")

    tasks = []
    for peer in peers:
        tasks.append(download_retry(torrent, peer, pieces, file))
    
    await asyncio.gather(*tasks) 

async def download_retry(torrent, peer, pieces, file):
    while True:    
        try:
            print("retrying: ", peer)
            await download(torrent, peer, pieces, file)
            print(peer, "FIN")
            break
        except Exception as error:
            pass
            continue

async def download(torrent, peer, pieces, file):
    queue = que.Queue(torrent)

    if peer[1] == 0:
        return

    reader, writer = await asyncio.open_connection(peer[0], peer[1])
    writer.write(messages.create_handshake(torrent))
    await writer.drain()

    message_buffer = bytearray()
    handshake = True

    retry_counter = 0

    while True:
        data = await reader.read(2048)
        if not data or len(data) == 0:
            await asyncio.sleep(0.5)
            retry_counter += 1

            if retry_counter >= 10:
                raise Exception("peer died")

            continue

        msg_len = 0

        message_buffer.extend(data)

        if handshake:
            msg_len = int.from_bytes(message_buffer[0:1], "big") + 49

        else:
            msg_len = int.from_bytes(message_buffer[0:4], "big") + 4

        while len(message_buffer) >= 4 and len(message_buffer) >= msg_len:
            await handle_message(message_buffer[0:msg_len], writer, pieces, queue, torrent, file)
            message_buffer = message_buffer[msg_len:]
            handshake = False


async def handle_message(msg, sock, pieces, queue, torrent, file):
    if is_handshake(msg):
        sock.write(messages.create_bitfield(pieces))
        await sock.drain()
        sock.write(messages.create_interested())
        await sock.drain()
    else:
        msg = messages.parse(msg)

        if msg["id"] == 0:
            handle_choke(sock)
        if msg["id"] == 1:
            await handle_unchoke(sock, pieces, queue)
        if msg["id"] == 2:
            await handle_interested(sock)
        if msg["id"] == 4:
            await handle_have(msg["payload"], sock, pieces, queue)
        if msg["id"] == 5:
            await handle_bitfield(msg["payload"], sock, pieces, queue)
        if msg["id"] == 6:
            await handle_request(sock, pieces, queue)
        if msg["id"] == 7:
            await handle_piece(sock, pieces, queue, torrent, file, msg["payload"])


def is_handshake(msg):
    return len(msg) == int.from_bytes(msg[0:1], "big") + 49 and msg[1:20].decode("utf-8") == "BitTorrent protocol"


def handle_choke(sock):
    sock.close()


async def handle_unchoke(sock, pieces, queue):
    queue.choked = False
    await request_piece(sock, pieces, queue)


async def handle_have(payload, sock, pieces, queue):
    piece_index = int.from_bytes(payload[0:4], "big")
    queue_empty = queue.length() == 0

    queue.queue(piece_index)

    if queue_empty:
        await request_piece(sock, pieces, queue)


async def handle_bitfield(payload, sock, pieces, queue):
    queue_empty = queue.length() == 0

    for i in range(len(payload)):
        byte = payload[i]
        for j in range(8):
            if byte % 2:
                queue.queue(i * 8 + 7 - j)
            byte = math.floor(byte / 2)

    if queue_empty:
        await request_piece(sock, pieces, queue)


async def handle_piece(sock, pieces, queue, torrent, file, piece_response):
    pieces.add_received(piece_response)

    offset = piece_response["index"] * torrent[b"info"][b"piece length"] + piece_response["begin"]

    file.seek(offset)
    file.write(piece_response["block"])
    print(pieces.get_progress(),"%")
    if pieces.is_done():
        sock.close()
        print("done!")
        file.close()

        for task in asyncio.all_tasks():
            task.cancel()

        exit()
    else:
        await request_piece(sock, pieces, queue)


async def handle_interested(sock):
    print(sock[0], "is interested")
    sock.write(messages.create_unchoke())
    await sock.drain()


async def handle_request(sock, pieces, queue):
    print(sock[0], " requests data")
    return None

async def request_piece(sock, pieces, queue):
    if queue.choked:
        return None


    while queue.length():
        piece_block = queue.deque()

        if pieces.needed(piece_block):
            sock.write(messages.create_request(piece_block))
            await sock.drain()
            pieces.add_requested(piece_block)
            break
