from twisted.internet.protocol import Factory
from PeerProtocol import PeerProtocol
class PeerFactory(Factory):
    protocol = PeerProtocol

    def __init__(self, peer):
        self.peer = peer

    def buildProtocol(self, addr):
        p = self.protocol(self.peer)
        p.factory = self
        return p

