from src import tparser


class Queue:
    def __init__(self, torrent):
        self.torrent = torrent
        self._queue = []
        self.choked = True

    def queue(self, piece_index):
        n_blocks = tparser.blocks_per_piece(self.torrent, piece_index)

        for i in range(0, n_blocks):
            piece_block = {
                "index": piece_index,
                "begin": i * tparser.BLOCK_LEN,
                "length": tparser.block_len(self.torrent, piece_index, i)
            }

            self._queue.append(piece_block)

    def deque(self):
        elem = self._queue[0]
        self._queue = self._queue[1:]

        return elem

    def peek(self):
        return self._queue[0]

    def length(self):
        return len(self._queue)
