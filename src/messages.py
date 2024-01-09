import math

from src import tparser
from src import idgen


def create_handshake(torrent):
    buffer = bytearray()

    buffer.extend(0x13.to_bytes(1, "big"))
    buffer.extend("BitTorrent protocol".encode("utf-8"))
    buffer.extend(0x0.to_bytes(8, "big"))
    buffer.extend(tparser.info_hash(torrent))
    buffer.extend(idgen.client_id)

    return bytes(buffer)


def create_keep_alive():
    buffer = bytearray()

    buffer.extend(0x0.to_bytes(4, "big"))

    return bytes(buffer)


def create_choke():
    buffer = bytearray()

    buffer.extend(0x1.to_bytes(4, "big"))
    buffer.extend(0x0.to_bytes(1, "big"))

    return bytes(buffer)


def create_unchoke():
    buffer = bytearray()

    buffer.extend(0x1.to_bytes(4, "big"))
    buffer.extend(0x1.to_bytes(1, "big"))

    return bytes(buffer)


def create_interested():
    buffer = bytearray()
    buffer.extend(0x1.to_bytes(4, "big"))
    buffer.extend(0x2.to_bytes(1, "big"))

    return bytes(buffer)


def create_uninterested():
    buffer = bytearray()

    buffer.extend(0x1.to_bytes(4, "big"))
    buffer.extend(0x3.to_bytes(1, "big"))

    return bytes(buffer)


def create_have(payload):
    buffer = bytearray()

    buffer.extend(0x5.to_bytes(4, "big"))
    buffer.extend(0x4.to_bytes(1, "big"))
    buffer.extend(payload.to_bytes(4))

    return bytes(buffer)


def create_bitfield(pieces):
    buffer = bytearray()
    buffer.extend((math.ceil(pieces.size / 8.0) + 1).to_bytes(4, "big"))
    buffer.extend(0x5.to_bytes(1, "big"))
    buffer.extend(pieces.create_bitfield().to_bytes(math.ceil(pieces.size / 8.0), "big"))


    return bytes(buffer)


def create_request(payload):
    buffer = bytearray()

    buffer.extend(0x13.to_bytes(4, "big"))
    buffer.extend(0x6.to_bytes(1, "big"))
    buffer.extend(payload["index"].to_bytes(4, "big"))
    buffer.extend(payload["begin"].to_bytes(4, "big"))
    buffer.extend(payload["length"].to_bytes(4, "big"))

    return bytes(buffer)


def create_piece(payload):
    buffer = bytearray()

    buffer.extend((len(payload["block"]) + 9).to_bytes(4, "big"))
    buffer.extend(0x7.to_bytes(1, "big"))
    buffer.extend(payload["index"].to_bytes(4, "big"))
    buffer.extend(payload["begin"].to_bytes(4, "big"))
    buffer.extend(payload["block"])

    return bytes(buffer)


def create_cancel(payload):
    buffer = bytearray()

    buffer.extend(0x13.to_bytes(4, "big"))
    buffer.extend(0x8.to_bytes(1, "big"))
    buffer.extend(payload["index"].to_bytes(4, "big"))
    buffer.extend(payload["begin"].to_bytes(4, "big"))
    buffer.extend(payload["length"].to_bytes(4, "big"))

    return bytes(buffer)


def create_port(payload):
    buffer = bytearray()

    buffer.extend(0x3.to_bytes(4, "big"))
    buffer.extend(0x9.to_bytes(1, "big"))
    buffer.extend(payload.to_bytes(2, "big"))


def parse(msg):
    id = None
    if len(msg) > 4:
        id = int.from_bytes(msg[4:5], "big")

    payload = None
    if len(msg) > 5:
        payload = msg[5:]

    if id == 6 or id == 7 or id == 8:
        rest = payload[8:]
        payload = {
            "index": int.from_bytes(payload[0:4], "big"),
            "begin": int.from_bytes(payload[4:8], "big")
        }

        if id == 7:
            payload["block"] = rest
        else:
            payload["length"] = rest

    return {
        "size": int.from_bytes(msg[0:4], "big"),
        "id": id,
        "payload": payload
    }
