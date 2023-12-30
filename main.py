import tracker
import tparser
import downloader

torrent = tparser.open_file("Cowboy Bebop - Movie.torrent")

tracker.get_peers(torrent, lambda peers: downloader.start_async_download(peers))
