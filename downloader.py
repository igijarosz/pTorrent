import messages
import socket
import io


def download_from_peers(torrent, peers):
    print(peers)
    for peer in peers:
        try:
            download(torrent, peer)
            print("next peer:")
        except Exception as error:
            print(error)
            pass


def download(torrent, peer):
    print(peer)

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
        if handshake:
            msg_len = int.from_bytes(message_buffer[0:8], "big") + 49
        else:
            msg_len = int.from_bytes(message_buffer[0:32], "big") + 4

        message_buffer.extend(data)

        while len(message_buffer) >= 4 and len(message_buffer) >= msg_len:
            handle_message(message_buffer[0:msg_len], sock)
            message_buffer = message_buffer[msg_len:]
            handshake = False


def handle_message(msg, sock):
    if is_handshake(msg):
        sock.sendall(messages.create_interested())


def is_handshake(msg):
    return len(msg) == int.from_bytes(msg[0:8], "big") + 49 and msg[1:20].decode("utf-8") == "BitTorrent protocol"
