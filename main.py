import sys
from src import downloader, tparser, tracker

sys.tracebacklimit = 0

torrent = tparser.open_file(sys.argv[1])
tracker.get_peers(torrent, lambda peers: downloader.download_from_peers(torrent, peers))

