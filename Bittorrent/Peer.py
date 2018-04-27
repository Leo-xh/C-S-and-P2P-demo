import random

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
        self.blockList = []  # a list of blockInfo
        # TODO : initialize the blockList
        self.requestList = []   # a list of peerId


class Peer():
    def __init__(self,
                 reactor,
                 metafile,
                 downloadFilename,
                 bitfieldFilename='bitfield'):
        self.peerList = []  # same as the one in client
        self.activePeerList = []  # a list of activePeer
        self.requestCount = 0  # total requests
        self.reactor = reactor
        self.metafile = metafile
        self.downloadFilename = downloadFilename
        self.bitfield = self.__readBitfieldFromFile(bitfieldFilename)
        self.bitfieldFilename = bitfieldFilename
        self.peerId = self.__generatePeerId()

    def __generatePeerId(self):
        # xh adds
        class peerIDCreator(object):

            def __init__(self):
                self.version = 1.0

            def getPeerID(self):
                pid = 'M' + str(self.version).replace('.', '-') + '-'
                for i in range(0, 20 - len(pid)):
                    pid += chr(random.randint(0, 127))
                return pid
        pIdCreator = peerIDCreator()
        return pIdCreator.getPeerID()

    def __readBitfieldFromFile(self, filename):
        pass

    def __updateBitfield(self, pieceId, addPiece=True):
        pass

    def __writePiece(self, piece):  # write a Piece to file
        pass

    def __downloadFinished(self):
        pass

        # xh adds
    def __getInfoHash(self):
        pass

    def __getPeerId(self):
        pass

    def __getBitfield(self):
        pass

    def __getBlockData(self, pieceID, blockOffset, blockLen):
        pass

    def __pieceFinished(self, pieceId, blockOffset, data):
        pass

    def peerListReceived(self, peerList):
        self.peerList = peerList

    def tryConnectPeer(self):
        pass

    def tryAddRequest(self):  # add a peer to a request list
        pass

    def trySendRequest(self):
        pass

    # TODO : timeout and abort connections

