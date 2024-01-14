import math
import bencodepy
import hashlib

BLOCK_LEN = 16384


def open_file(filename):
    torrent_file = open(filename, "rb").read()
    return bencodepy.decode(torrent_file)


def info_hash(torrent):
    info = bencodepy.encode(torrent[b"info"])
    return hashlib.sha1(info).digest()


def size(torrent):
    size = torrent[b"info"][b"length"]
    return size.to_bytes(8, "big")

def size_mb(torrent):
    piece_length = torrent[b"info"][b"piece length"] / 1024
    pieces = len(torrent[b"info"][b"pieces"]) / 1024
    return piece_length * pieces / 20.0


def piece_len(torrent, piece_index):
    total_length = torrent[b"info"][b"length"]
    piece_length = torrent[b"info"][b"piece length"]
    last_piece_length = total_length % piece_length
    last_piece_index = math.floor(total_length / piece_length)

    if last_piece_index == piece_index:
        return last_piece_length
    else:
        return piece_length


def blocks_per_piece(torrent, piece_index):
    piece_length = piece_len(torrent, piece_index)

    return math.ceil(piece_length / BLOCK_LEN)


def block_len(torrent, piece_index, block_index):
    piece_length = piece_len(torrent, piece_index)
    last_piece_length = piece_length % BLOCK_LEN
    last_piece_index = math.floor(piece_length / BLOCK_LEN)

    if block_index == last_piece_index:
        return last_piece_length
    else:
        return BLOCK_LEN
