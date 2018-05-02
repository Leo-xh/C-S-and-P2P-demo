import sys 
sys.path.append("../")
import bencode
from twisted.internet import reactor
from twisted.internet import task
import socket
import PeerProtocol
import PeerFactory
import Peer
from Client import RequestClient

INTERVAL_CONNECT_PEER = 5
INTERVAL_ADD_REQUEST = 1/20
INTERVAL_SEND_REQUEST = 1/20
# PEER_LISTEN_TCP_PORT = 6788
# CLIENT_UDP_PORT = 56788
import random
PEER_LISTEN_TCP_PORT = random.randint(6000, 7000)
CLIENT_UDP_PORT = random.randint(50000, 57000)

def readMetafileFromFile(filename):
    return bencode.decode(open(filename, 'rb').read())

def main():
    metafile = readMetafileFromFile('test.torrent')
    peer = Peer.Peer(PEER_LISTEN_TCP_PORT, reactor, metafile)
    reqClient = RequestClient(
        peer,
        PEER_LISTEN_TCP_PORT,
        clientIpstr = '127.0.0.1',
        # clientIpstr=socket.gethostbyname(socket.gethostname()),
        clientPort=CLIENT_UDP_PORT,
        protocol_id=1,
        info_hash=peer._getInfoHash(),
        peer_id=peer._getPeerID(),
        downloaded=0,
        left=0,
        uploaded=0,
        event=0,
        key=0,
        num_want=0)

    reactor.adoptDatagramPort(reqClient.portSocket.fileno(),
                              socket.AF_INET, reqClient)

    reactor.listenTCP(PEER_LISTEN_TCP_PORT, peer.Serverfactory)
    # loopConnectPeer = task.LoopingCall(peer.tryConnectPeer)
    loopAddRequest = task.LoopingCall(peer.tryAddRequest)
    loopSendRequest = task.LoopingCall(peer.trySendRequest)

    reactor.callLater(INTERVAL_CONNECT_PEER, peer.tryConnectPeer)
    # loopConnectPeer.start(INTERVAL_CONNECT_PEER)
    loopAddRequest.start(INTERVAL_ADD_REQUEST)
    loopSendRequest.start(INTERVAL_SEND_REQUEST)

    reactor.run()

if __name__ == '__main__':
    main()
