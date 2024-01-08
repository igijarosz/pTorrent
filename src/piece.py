from src import tparser
import math


class Piece:
    def __init__(self, torrent):
        def create_pieces_arr():
            size = self.size
            arr = [None] * size
            for i in range(size):
                arr[i] = [False] * tparser.blocks_per_piece(torrent, i)
            return arr

        self.size = len(torrent[b"info"][b"pieces"]) // 20
        self.requested = create_pieces_arr()
        self.received = create_pieces_arr()

    def add_requested(self, piece_block):
        block_index = piece_block["begin"] // tparser.BLOCK_LEN
        self.requested[piece_block["index"]][block_index] = True

    def add_received(self, piece_block):
        block_index = piece_block["begin"] // tparser.BLOCK_LEN
        self.received[piece_block["index"]][block_index] = True

    def needed(self, piece_block):
        if all(all(x for x in y) for y in self.requested):
            for i in range(len(self.received)):
                self.requested[i] = self.received[i].copy()

        block_index = piece_block["begin"] // tparser.BLOCK_LEN

        return not self.requested[piece_block["index"]][block_index]

    def get_progress(self):
        pieces_received = len(list(filter(lambda x: all(z for z in x), self.received)))
        return math.floor((pieces_received / self.size)*10000)/100

    def is_done(self):
        return all(all(x for x in y) for y in self.received)
