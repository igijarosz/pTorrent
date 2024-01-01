import math

import messages
import socket
import piece
import que


def download_from_peers(torrent, peers):
    pieces = piece.Piece(torrent)
    file = open("cos", "wb")
    for peer in peers:
        try:
            download(torrent, peer, pieces, file)
        except Exception as error:
            print(error)
            pass


def download(torrent, peer, pieces, file):
    queue = que.Queue(torrent)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    sock.connect(peer)
    sock.sendall(messages.create_handshake(torrent))
    message_buffer = bytearray()
    handshake = True

    while True:
        data = sock.recv(1024)
        if not data:
            break
        print(data)
        msg_len = 0

        message_buffer.extend(data)

        if handshake:
            msg_len = int.from_bytes(message_buffer[0:1], "big") + 49

        else:
            msg_len = int.from_bytes(message_buffer[0:4], "big") + 4

        while len(message_buffer) >= 4 and len(message_buffer) >= msg_len:
            handle_message(message_buffer[0:msg_len], sock, pieces, queue, torrent, file)
            message_buffer = message_buffer[msg_len:]
            handshake = False


def handle_message(msg, sock, pieces, queue, torrent, file):
    if is_handshake(msg):
        sock.sendall(messages.create_interested())
    else:
        msg = messages.parse(msg)

        if msg["id"] == 0:
            handle_choke(sock)
        if msg["id"] == 1:
            handle_unchoke(sock, pieces, queue)
        if msg["id"] == 4:
            handle_have(msg["payload"], sock, pieces, queue)
        if msg["id"] == 5:
            handle_bitfield(msg["payload"], sock, pieces, queue)
        if msg["id"] == 7:
            handle_piece(sock, pieces, queue, torrent, file, msg["payload"])


def is_handshake(msg):
    return len(msg) == int.from_bytes(msg[0:1], "big") + 49 and msg[1:20].decode("utf-8") == "BitTorrent protocol"


def handle_choke(sock):
    sock.close()


def handle_unchoke(sock, pieces, queue):
    queue["choked"] = False
    request_piece(sock, pieces, queue)


def handle_have(payload, sock, pieces, queue):
    piece_index = int.from_bytes(payload[0:4], "big")
    queue_empty = queue.length() == 0

    queue.queue(piece_index)

    if queue_empty:
        request_piece(sock, pieces, queue)


def handle_bitfield(payload, sock, pieces, queue):
    queue_empty = queue.length() == 0

    for i in range(len(payload)):
        byte = payload[i]
        for j in range(8):
            if byte % 2:
                queue.queue(i * 8 + 7 - j)
            byte = math.floor(byte / 2)

    if queue_empty:
        request_piece(sock, pieces, queue)


def handle_piece(sock, pieces, queue, torrent, file, piece_response):
    pieces.add_received(piece_response)

    offset = piece_response["index"] * torrent[b"info"][b"piece length"] + piece_response["begin"]

    file.seek(offset)
    file.write(piece_response["block"])

    if pieces.is_done():
        sock.close()
        print("done!")
        file.close()
        exit()
    else:
        request_piece(sock, pieces, queue)


def request_piece(sock, pieces, queue):
    if queue.choked:
        return None

    while queue.length():
        piece_block = queue.deque()

        if pieces.needed(piece_block):
            sock.sendall(messages.create_request(piece_block))
            pieces.add_requested(piece_block)
            break
