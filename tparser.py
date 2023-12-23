import bencodepy
import hashlib


def open_file(filename):
    torrent_file = open(filename, "rb").read()
    return bencodepy.decode(torrent_file)


def info_hash(torrent):
    info = bencodepy.encode(torrent[b"info"])
    return hashlib.sha1(info).digest()


def size(torrent):
    size = torrent[b"info"][b"length"]
    return size.to_bytes(8, "big")
