from twisted.internet.protocol import ClientFactory, ServerFactory
import PeerProtocol
class PeerClientFactory(ClientFactory):
    protocol = PeerProtocol.PeerProtocol

    def __init__(self, peer):
        self.peer = peer
        # self.flag = False

    def buildProtocol(self, addr):
        print("building")
        return self.p

    def startedConnecting(self, connector):
        print("connecting")
        self.p = self.protocol(self.peer)
        self.p.factory = self
        self.p.sendConn = True
        return
        # pass
        
    def clientConnectionLost(self, connector, reason):
        pass

    def clientConnectionFailed(self, connector, reason):
        pass

class PeerServerFactory(ServerFactory):
    protocol = PeerProtocol.PeerProtocol

    def __init__(self, peer):
        self.peer = peer

    def buildProtocol(self, addr):
        print("building")
        p = self.protocol(self.peer)
        p.factory = self
        return p
