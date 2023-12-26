import socket
import urllib.parse
import secrets
import io
import tparser

client_id = bytearray()
client_id.extend(bytes('-pT0001-', "UTF-8"))
client_id.extend(secrets.token_bytes(12))


## funkcja pobierająca peery z dict torrent
def get_peers(torrent, callback):
    announce_list = [x[0] for x in torrent[b"announce-list"]]
    announce_list.reverse()
    for announce in announce_list:
        announce = str(announce, "utf-8")
        if not announce.startswith("udp"):
            continue
        url = urllib.parse.urlparse(announce)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(0.5)
            sock.connect((url.hostname, url.port))
            sock.sendall(create_connection_request())
            ## imo jakas petla co dane robi
            while True:
                data = io.BytesIO(sock.recv(1024))
                resp_type = response_type(data)
                if resp_type == "connect":
                    connection_response = parse_connection_response(data)
                    announce_request = create_announce_request(connection_response["connectionId"], torrent, url.port)
                    sock.sendall(announce_request)
                elif resp_type == "announce":
                    announce_response = parse_announce_response(data)
                    callback(announce_response["peers"])
                    return
        except Exception as error:
            print(error)
            pass


def response_type(response):
    action = int.from_bytes(response.read(4), "big")
    if action == 0:
        return "connect"
    if action == 1:
        return "announce"


def create_connection_request():
    buffer = bytearray()
    buffer.extend(0x41727101980.to_bytes(8, "big"))
    buffer.extend(0x0.to_bytes(4, "big"))
    buffer.extend(secrets.token_bytes(4))
    return bytes(buffer)


def parse_connection_response(response):
    conn_resp = dict()
    conn_resp["transactionId"] = response.read(4)
    conn_resp["connectionId"] = response.read(8)
    return conn_resp


def create_announce_request(id, torrent, port):
    buffer = bytearray()
    buffer.extend(int.from_bytes(id, "big").to_bytes(8, "big"))             # connection id
    buffer.extend(0x1.to_bytes(4, "big"))                                   # action
    buffer.extend(secrets.token_bytes(4))                                   # transaction id
    buffer.extend(tparser.info_hash(torrent))                               # info hash
    buffer.extend(client_id)                                                # client id
    buffer.extend(0x0.to_bytes(8, "big"))                                   # downloaded
    buffer.extend(tparser.size(torrent))                                    # left
    buffer.extend(0x0.to_bytes(8, "big"))                                   # uploaded
    buffer.extend(0x0.to_bytes(4, "big"))                                   # event
    buffer.extend(0x0.to_bytes(4, "big"))                                   # ip address
    buffer.extend(secrets.token_bytes(4))                                   # key
    buffer.extend((-1).to_bytes(4, "big", signed=True))                     # num want
    buffer.extend(port.to_bytes(2, "big"))                                  # port
    return bytes(buffer)


def parse_announce_response(response):
    def group(iterable):
        groups = []
        for i in range(0, len(iterable), 6):
            groups.append(iterable[slice(i, i + 6)])
        return groups
    ann_resp = dict()
    ann_resp["action"] = response.read(4)
    ann_resp["transactionId"] = response.read(4)
    ann_resp["leechers"] = response.read(4)
    ann_resp["seeders"] = response.read(4)
    ann_resp["peers"] = [(parse_peer_ip(x[0:4]), int.from_bytes(x[4:6], "big")) for x in group(response.read())]

    return ann_resp

def parse_peer_ip(stuff):
    ip = ""
    ip += str(stuff[0]) + "."
    ip += str(stuff[1]) + "."
    ip += str(stuff[2]) + "."
    ip += str(stuff[3])
    return ip