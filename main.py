import urllib.parse
import hashlib

text = open("Cowboy Bebop - Movie.torrent", "rb").read()

info_hash_start = text.find(bytes("infod", "utf-8")) + 4
info_d_end = text[info_hash_start:-1]
info_hash = hashlib.sha1(info_d_end).digest()

text = text.decode("utf-8", errors="ignore")


def Bdecode(input_data):
    data = list(input_data)

    while len(data) > 0:

        element = data.pop(0)
        if element.isnumeric():
            length = ""
            while element.isnumeric():
                length += str(element)
                if len(data) > 0:
                    element = data.pop(0)
            string = ""
            for i in range(int(length)):
                if len(data) > 0:
                    string += data.pop(0)

            return string, data

        if element == "i":
            integer = ""
            element = data.pop(0)
            while element.isnumeric() or element == "-":
                integer += element
                element = data.pop(0)
            return integer, data

        if element == "l":
            lista = []
            element = data.pop(0)
            while element != "e":
                if len(data) == 0:
                    return lista, data
                data.insert(0, element)
                value, data = Bdecode(data)
                lista.append(value)
                element = data.pop(0)
            return lista, data

        if element == "d":
            dictionary = {}
            element = data.pop(0)
            while element != "e":
                if len(data) == 0:
                    return dictionary, data
                data.insert(0, element)
                key, data = Bdecode(data)
                value, data = Bdecode(data)
                dictionary[key] = value
                if len(data) > 0:
                    element = data.pop(0)
            return dictionary, data


file_contents = Bdecode(text)[0]

# file_tuple = (file_contents["announce"], file_contents["announce-list"], file_contents["info"]["piece length"],
# file_contents["info"]["pieces"], file_contents["info"]["name"], file_contents["info"]["length"])

announce = file_contents["announce"]
announce_list = file_contents["announce-list"]
piece_length = file_contents["info"]["piece length"]
pieces = file_contents["info"]["pieces"]
name = file_contents["info"]["name"]
length = file_contents["info"]["length"]


print(urllib.parse.quote_plus(info_hash))

client_id = f"-pT1000-123456789123"




