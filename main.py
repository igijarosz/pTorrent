import bencoder
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
info_dict_start = text.find(bytes("infod", "utf-8")) + 4
info_dict = text[info_dict_start:-1]
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

tracker_response_loc = urllib.request.urlretrieve(tracker_url,"Temp/response")[0]
tracker_response = open(tracker_response_loc, "rb").read()
urllib.request.urlcleanup()

announce_list = file_contents["announce-list"]
piece_length = file_contents["info"]["piece length"]
pieces = file_contents["info"]["pieces"]
name = file_contents["info"]["name"]

#FIXME: a really unsafe way to find where the peers start
peers_start = tracker_response.find(bytes("peers", "utf-8"))+9
peers_end = tracker_response.rfind(bytes("peers", "utf-8"))-2
peers = tracker_response[peers_start:peers_end]

print(peers)

for j in range(0, len(peers)):
    peer_ip = ""
    peer_port = 1
    for i in range(0, 6):
        if i < 4:
            peer_ip += str(int.from_bytes(struct.unpack("!c", peers[j+i:j+i+1:1])[0],"big")) + "."
        else:
            peer_port *= int.from_bytes(struct.unpack("!c", peers[j+i:j+i+1:1])[0],"big")

    print(f"{peer_ip}:{peer_port}")