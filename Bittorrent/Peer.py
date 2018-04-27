import random
import bencode
import hashlib
from bitstring import BitArray
from math import *

MAX_NUM_ACTIVE_PEERS = 3
MAX_NUM_REQUESTS = 10
MAX_NUM_REQUESTS_PER_PIECE = 1

BLOCK_SIZE = 16384 # 2^14


class ActivePeer(object):
    def __init__(self, peerID, protocol):
        self.peerID = peerID
        self.bitfield = 0
        self.protocol = protocol


class Piece(object):
    class blockInfo(object):
        def __init__(self, offset, size):
            self.offset = offset
            self.size = size
            self.requestSent = False
            self.dataReceived = False
            self.data = None

    def __init__(self, pieceIndex, pieceLength, SHA1):
        self.pieceIndex = pieceIndex
        self.pieceLength = pieceLength
        self.SHA1 = SHA1
        self.have = False
        self.blockList = {}  # a list of blockInfo
        self._initBlockList()
        # TODO : initialize the blockList
        self.requestList = []   # a list of peerID
    
    def _initBlockList(self):
        for i in range(0, ceil(self.pieceLength/BLOCK_SIZE)):
            if i != ceil(self.pieceLength/BLOCK_SIZE)-1:
                self.blockList.update({i*BLOCK_SIZE : self.blockInfo(i*BLOCK_SIZE,BLOCK_SIZE)})
            else:
                self.blockList.update({i*BLOCK_SIZE : self.blockInfo(i*BLOCK_SIZE,self.pieceLength - i * BLOCK_SIZE)})
        


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
        self.pieceList = []
        self.file = open(downloadFilename, 'ab')
        
    def _initPieceList(self):
        FileInfo = self.metafile['info']
        self.info_hash = hashlib.sha1(FileInfo)
        # pay attention
        self.fileLength = FileInfo['length']
        self.md5sum = FileInfo['md5sum']
        self.name = FileInfo['name']
        self.pieceLength = FileInfo['piece length']
        for i in range(0, len(FileInfo['pieces'])/20):
            if i != len(FileInfo['pieces'])/20 - 1:
                self.pieceList.append(Piece(i, self.pieceLength, FileInfo['pieces'][i*20:(i+1)*20]))
            else:
                self.pieceList.append(Piece(i, len(FileInfo['pieces'])-20*i, FileInfo['pieces'][i*20:]))
                
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
        self.bitfield = BitArray(self.bitfield).set(addPiece, pieceIndex).bytes

    def _writePiece(self, piece):  # write a Piece to file
        self.file.seek(piece.pieceIndex * self.pieceLength)
        blockOffsets = list(piece.blockList.keys()).sort()
        for offset in blockOffsets:
            self.file.write(piece.blockList[offset].data)
        self.file.seek(-piece.pieceIndex * self.pieceLength)
        for piece in self.pieceList:
            if piece.have != True:
                return 
        self._downloadFinished()

    def _downloadFinished(self):
        print(self.downloadFilename, " downloaded.")

        # xh adds
    def _getInfoHash(self):
        return self.info_hash

    def _getpeerID(self):
        return self.peerID

    def _getBitfield(self):
        return self.bitfield

    # need not blockLen
    def _getBlockData(self, pieceIndex, blockOffset, blockLen):
        return self.pieceList[pieceIndex].blockList[blockOffset].data

    def _pieceFinished(self, pieceIndex):
        self.pieceList[pieceIndex].have = True
        for activePeer in self.activePeerList:
            activePeer.protocol._sendHave(pieceIndex)
        self._writePiece(self.pieceList[pieceIndex])
    
    def _blockReceived(self, pieceIndex, blockOffset, data, dataSize):
        self.pieceList[pieceIndex].blockList[blockOffset].data = data
        self.pieceList[pieceIndex].blockList[blockOffset].dataReceived = True
        if self.pieceList[pieceIndex].pieceLength == blockOffset + dataSize:
            self._pieceFinished(pieceIndex)
        
    def peerListReceived(self, peerList):
        self.peerList = peerList

    def tryConnectPeer(self):
        pass

    def tryAddRequest(self):  # add a peer to a request list
        pass

    def trySendRequest(self):
        pass

    # TODO : timeout and abort connections

