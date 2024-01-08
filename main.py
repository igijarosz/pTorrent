from src import downloader, tparser, tracker

torrent = tparser.open_file("debian 12.4.0 edu.torrent")

tracker.get_peers(torrent, lambda peers: downloader.download_from_peers(torrent, peers))
