import tracker
import tparser

torrent = tparser.open_file("Cowboy Bebop - Movie.torrent")

##print(tracker.create_connection_request())

tracker.get_peers(torrent, lambda peers: print(peers))
