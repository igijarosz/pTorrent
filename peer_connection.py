import socket


class Peer:
    def __init__(self, id, ip, port, bitfield):
        self.id = id
        self.ip = ip
        self.port = port
        self.bitfield = bitfield

    def interested(self):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.settimeout(60)
        print(f"\nConnecting to {self.ip, self.port}...")
        connection.connect((self.ip, self.port))
        print("Connected")
        connection.sendall(b'\x00\x00\x00\x012')
        buffer = connection.recv(1048)
        print(buffer)


peer_list = []


def connect(ip_list, req_msg):
    for i in range(0, len(ip_list) - 1):
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.settimeout(0.05)
            print(f"\nConnecting to {(ip_list[i][0], ip_list[i][1])}...")
            connection.connect((ip_list[i][0], ip_list[i][1]))
            print("Connected")
            connection.sendall(req_msg)
            buffer = connection.recv(1048)
            print("Response:\n", buffer)
            peer = Peer(buffer[48:68], ip_list[i][0], ip_list[i][1], buffer[68:])
            if len(buffer[48:68]) > 0 and len(buffer[68:]) > 5:
                peer_list.append(peer)
            connection.shutdown(1)
            connection.close()
            print("Connection closed")
        except Exception as error:
            print(error)
            connection.close()
            pass
