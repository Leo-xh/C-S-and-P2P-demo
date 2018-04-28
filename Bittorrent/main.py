from twisted.internet import reactor
from twisted.internet import task
from PeerProtocol import PeerProtocol
from PeerFactory import PeerFactory
from Peer import Peer
from Client import RequestClient

INTERVAL_CONNECT_PEER = 5
INTERVAL_ADD_REQUEST = 7
INTERVAL_SEND_REQUEST = 4
LISTEN_TCP_PORT = 6788


def readMetafileFromFile(filename):
    pass

def main():
    metafile = readMetafileFromFile('test.torrent')
    peer = Peer(reactor, metafile, 'file.txt')

    reactor.listenTCP(LISTEN_TCP_PORT, PeerFactory)
    loopConnectPeer = task.LoopingCall(peer.tryConnectPeer)
    loopAddRequest = task.LoopingCall(peer.tryAddRequest)
    loopSendRequest = task.LoopingCall(peer.trySendRequest)

    loopConnectPeer.start(INTERVAL_CONNECT_PEER)
    loopAddRequest.start(INTERVAL_ADD_REQUEST)
    loopSendRequest.start(INTERVAL_SEND_REQUEST)

    reactor.run()

if __name__ == '__main__':
    main()
