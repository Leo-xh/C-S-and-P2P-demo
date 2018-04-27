from twisted.internet.interfaces import IReactorTCP
from twisted.internet import task
from PeerProtocol import PeerProtocol
from PeerFactory import PeerFactory
from Peer import Peer
from Client import RequestClient

INTERVAL_CONNECT_PEER = 5
INTERVAL_ADD_REQUEST = 7
INTERVAL_SEND_REQUEST = 4

def readMetafileFromFile(filename):
    pass

def main():
    metafile = readMetafileFromFile('test.torrent')
    reactor = IReactorTCP('')
    peer = Peer(reactor, metafile, 'file.txt')

    loopConnectPeer = task.LoopingCall(peer.tryConnectPeer)
    loopAddRequest = task.LoopingCall(peer.tryAddRequest)
    loopSendRequest = task.LoopingCall(peer.trySendRequest)

    loopConnectPeer.start(INTERVAL_CONNECT_PEER)
    loopAddRequest.start(INTERVAL_ADD_REQUEST)
    loopSendRequest.start(INTERVAL_SEND_REQUEST)
    reactor.run()

if __name__ == '__main__':
    main()
