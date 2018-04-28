from twisted.internet.protocol import Factory
import PeerProtocol
class PeerFactory(Factory):
    protocol = PeerProtocol.PeerProtocol

    def __init__(self, peer):
        self.peer = peer

    def buildProtocol(self, addr):
        p = self.protocol(self.peer)
        p.factory = self
        return p

    def startedConnecting(self, connector):
        pass
        
    def clientConnectionLost(self, connector, reason):
        pass

    def clientConnectionFailed(self, connector, reason):
        pass
