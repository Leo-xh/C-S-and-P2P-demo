from twisted.internet.protocol import Protocol
class PeerProtocol(Protocol):

    def __init__(self, peer):
        self.peer = peer
        self.bitfieldSent = False

    def connectionMade(self):
        pass

    def connectionLost(self):
        pass

    def dataReceived(self, data):
        pass

    def handshakeReceived(self, data):
        pass

    def handshakeReplyReceived(self, data):
        pass

    def bitfieldReceived(self, data):
        pass

    def requestReceived(self, data):
        pass

    def haveReceived(self, data):
        pass

    def pieceReceived(self, data): # if piece download finished, call Peer.pieceFinished
        pass

