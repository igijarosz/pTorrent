import socket
import bencoder
import peer_connection

import urllib.parse
import urllib.request
import hashlib
import random
import struct

# generate random client id
client_id = f"-pT1000-{random.randint(100000000000, 999999999999)}"

# open the file
text = open("Cowboy Bebop - Movie.torrent", "rb").read()

# get info hash
info_dict = text[text.find(bytes("infod", "utf-8")) + 4:-1]
info_hash = hashlib.sha1(info_dict).digest()
info_hash_parsed = urllib.parse.quote_plus(info_hash)

# decode the file
file_contents = bencoder.Bdecode(text.decode("utf-8", errors="ignore"))[0]

# assemble the url
announce = file_contents["announce"]
port = "6881"
length = file_contents["info"]["length"]
tracker_url = f"{announce}?info_hash={info_hash_parsed}&peer_id={client_id}&port={port}&left={length}"

# connect to the tracker
tracker_response_loc = urllib.request.urlretrieve(tracker_url, "Temp/response")[0]
tracker_response = open(tracker_response_loc, "rb").read()
urllib.request.urlcleanup()

announce_list = file_contents["announce-list"]
piece_length = file_contents["info"]["piece length"]
pieces = file_contents["info"]["pieces"]
name = file_contents["info"]["name"]

# FIXME: a really unsafe way to find where the peers start
peers_start = tracker_response.find(bytes("peers", "utf-8")) + 9
peers_end = tracker_response.rfind(bytes("peers", "utf-8")) - 2
peers_bytes = tracker_response[peers_start:peers_end]

# get ip of the peers
ip_list = []
for j in range(0, len(peers_bytes)):

    peer_ip = ""
    peer_port = 0
    for i in range(0, 6):
        try:
            if i < 4:
                peer_ip += str(int.from_bytes(struct.unpack("!c", peers_bytes[j + i:j + i + 1:1])[0], "big")) + "."
            if i == 4:
                peer_port += int.from_bytes(struct.unpack("!c", peers_bytes[j + i:j + i + 1:1])[0], "big") * 256
            if i == 5:
                peer_port += int.from_bytes(struct.unpack("!c", peers_bytes[j + i:j + i + 1:1])[0], "big")
        except:
            continue

    ip_list.append((peer_ip[:-1], peer_port))
print(ip_list)

# create the request message
request = b'\x13BitTorrent protocol\x00\x00\x00\x00\x00\x00\x00\x00' + info_hash + bytearray(client_id, "utf-8")

# socket connection
peer_connection.connect(ip_list, request)

for i in range(0, len(peer_connection.peer_list)):
    print(peer_connection.peer_list[i].id, peer_connection.peer_list[i].ip)
    peer_connection.peer_list[i].interested()