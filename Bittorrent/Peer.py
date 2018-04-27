import random

MAX_NUM_ACTIVE_PEERS = 3
MAX_NUM_REQUESTS = 10
MAX_NUM_REQUESTS_PER_PIECE = 1

# NUM_BLOCKS_PER_PIECE = ?
# BLOCK_SIZE
# PIECE_SIZE


class ActivePeer():
    def __init__(self, peerID, protocol):
        self.peerID = peerID
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

    def _init_(self, pieceIndex):
        self.pieceIndex = pieceIndex
        self.have = False
        self.blockList = []  # a list of blockInfo
        # TODO : initialize the blockList
        self.requestList = []   # a list of peerID


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
        self.bitfield = self._readBitfieldFromFile(bitfieldFilename)
        self.bitfieldFilename = bitfieldFilename
        self.peerID = self._generatepeerID()

    def _generatepeerID(self):
        # xh adds
        class peerIDCreator(object):

            def _init_(self):
                self.version = 1.0

            def getpeerID(self):
                pid = 'M' + str(self.version).replace('.', '-') + '-'
                for i in range(0, 20 - len(pid)):
                    pid += chr(random.randint(0, 127))
                return pid
        pIdCreator = peerIDCreator()
        return pIdCreator.getpeerID()

    def _readBitfieldFromFile(self, filename):
        pass

    def _updateBitfield(self, pieceIndex, addPiece=True):
        pass

    def _writePiece(self, piece):  # write a Piece to file
        pass

    def _downloadFinished(self):
        pass

        # xh adds
    def _getInfoHash(self):
        pass

    def _getpeerID(self):
        pass

    def _getBitfield(self):
        pass

    def _getBlockData(self, pieceIndex, blockOffset, blockLen):
        pass

    def _pieceFinished(self, pieceIndex, blockOffset, data):
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

