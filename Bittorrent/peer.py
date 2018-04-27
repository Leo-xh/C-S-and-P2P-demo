from twisted.internet.protocol import Factory, Protocol
from twisted.internet.interfaces import IReactorTCP

MAX_NUM_ACTIVE_PEERS = 3
MAX_NUM_REQUESTS = 10
MAX_NUM_REQUESTS_PER_PIECE = 1
# NUM_BLOCKS_PER_PIECE = ?
# BLOCK_SIZE
# PIECE_SIZE


class ActivePeer():

    def __init__(self, peerId, protocol):
        self.peerId = peerId
        self.bitfield = 0
        self.protocol = protocol


class Piece():

    class blockInfo():

        def __init__(self, offset, size):
            self.offset = offset
            self.size = size
            self.requestSent = False
            self.dataReceived = False
            self.data = None

    def __init__(self, pieceId):
        self.pieceId = pieceId
        self.have = False
        self.blockList = []     # a list of blockInfo
        # TODO : initialize the blockList
        self.requestList = []   # a list of peerId


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



class PeerFactory(Factory):
    protocol = PeerProtocol

    def __init__(self, peer):
        self.peer = peer

    def buildProtocol(self, addr):
        p = self.protocol(self.peer)
        p.factory = self
        return p


class Peer():

    def __init__(self, reactor, metafile, downloadFilename, bitfieldFilename='bitfield'):
        self.peerList = []   # same as the one in client
        self.activePeerList = []  # a list of activePeer
        self.requestCount = 0   # total requests
        self.reactor = reactor
        self.metafile = metafile
        self.downloadFilename = downloadFilename
        self.bitfield = self.__readBitfieldFromFile(bitfieldFilename)
        self.bitfieldFilename = bitfieldFilename
        self.peerId = self.__generatePeerId()

    def __generatePeerId(self):
        pass

    def __readBitfieldFromFile(self, filename):
        pass

    def __updateBitfield(self, pieceId, addPiece=True):
        pass

    def __writePiece(self, piece): # write a Piece to file
        pass

    def __downloadFinished(self):
        pass

    def peerListReceived(self, peerList):
        self.peerList = peerList

    def tryConnectPeer(self):
        pas

    def tryAddRequest(self):  # add a peer to a request list
        pass

    def trySendRequest(self):
        pass

    def pieceFinished(self, pieceId):
        pass
    # TODO : timeout and abort connections
