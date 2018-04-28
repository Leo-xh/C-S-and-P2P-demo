import random
import bencode
import hashlib
import os
from bitstring import BitArray
from math import *
import PeerFactory

MAX_NUM_ACTIVE_PEERS = 3
MAX_NUM_REQUESTS = 10
MAX_NUM_REQUESTS_PER_PIECE = 1

BLOCK_SIZE = 16384 # 2^14


class ActivePeer(object):
    def __init__(self, peerID, protocol):
        self.peerID = peerID
        self.bitfield = None
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
        # print(self.pieceLength)
        self.SHA1 = SHA1
        self.have = False
        self.blockList = {}  # key: offset, val: blockInfo
        self._initBlockList()
        # print(len(self.blockList))
        self.requestList = []   # a list of peerID
    
    def _initBlockList(self):
        for i in range(0, ceil(self.pieceLength/BLOCK_SIZE)):
            if i != ceil(self.pieceLength/BLOCK_SIZE)-1:
                self.blockList.update({i*BLOCK_SIZE : self.blockInfo(i*BLOCK_SIZE,BLOCK_SIZE)})
            else:
                self.blockList.update({i*BLOCK_SIZE : self.blockInfo(i*BLOCK_SIZE,self.pieceLength - i * BLOCK_SIZE)})
        
    def _readBlockData(self, fileReader):
        self.have = True
        for i in self.blockList.keys():
            self.blockList[i].dataReceived = True
            self.blockList[i].data = fileReader.read(self.blockList[i].size)


class Peer():
    def __init__(self,
                 peerPort,
                 reactor,
                 metafile,
                 downloadFilename,
                 bitfieldFilename='bitfield'):
        self.peerPort = peerPort
        self.peerList = []  # same as the one in client
        self.connected = {} # whether a peer has been connected, key: item in peerList
        self.activePeerList = {}  # key: peerID, val: activePeer
        self.requestCount = 0  # total requests
        self.reactor = reactor
        self.Clientfactory = PeerFactory.PeerClientFactory(self)
        self.Serverfactory = PeerFactory.PeerServerFactory(self)
        self.metafile = metafile
        self.FileInfo = self.metafile['info']
        self.info_hash = hashlib.sha1(str(self.FileInfo).encode()).digest()
        # pay attention
        self.fileLength = self.FileInfo['length']
        # print(self.fileLength)
        self.md5sum = self.FileInfo.get('md5sum')
        self.name = self.FileInfo['name']
        self.pieceLength = self.FileInfo['piece length']
        # print(self.pieceLength)
        self.downloadFilename = downloadFilename
        self.pieceList = []
        self._initPieceList()
        self.bitfield = self._readBitfieldFromFile(bitfieldFilename)
        self.bitfieldFilename = bitfieldFilename
        self.peerID = self._generatePeerID()
        self._initFile(downloadFilename)
        self._initData()
        
        
    def _initFile(self, filename):
        if not os.path.exists(filename):
            self.file = open(filename, 'wb')
            # self.file.seek(self.metafile['info']['length']-1)  # ychz debug 16:47 
            # self.file.write(b'\x00')
            self.file.close()
            
        
        
    def _initPieceList(self):
        for i in range(0, len(self.FileInfo['pieces'])//20):
            if i != len(self.FileInfo['pieces'])//20 - 1:
                self.pieceList.append(Piece(i, self.pieceLength, self.FileInfo['pieces'][i*20:(i+1)*20]))
            else:
                self.pieceList.append(Piece(i, len(self.FileInfo['pieces'])-20*i, self.FileInfo['pieces'][i*20:]))


    def _initData(self):
        # print(self.bitfield)
        # print(len(self.FileInfo['pieces'])//20)
        fileReader = open(self.downloadFilename, 'rb')
        bit = BitArray(self.bitfield)
        for i in range(0, len(self.FileInfo['pieces'])//20):
            if bit[i] == True:
                fileReader.seek(self.pieceLength * i)
                self.pieceList[i]._readBlockData(fileReader)

    def _generatePeerID(self):
        # xh adds
        class peerIDCreator(object):

            def __init__(self):
                self.version = 1.0

            def getpeerID(self):
                pid = 'M' + str(self.version).replace('.', '-') + '-'
                for i in range(0, 20 - len(pid)):
                    pid += chr(random.randint(0, 127))
                return pid
        pIdCreator = peerIDCreator()
        return pIdCreator.getpeerID()

    def _readBitfieldFromFile(self, filename):
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                return file.read()
        else:
            # print("init bitfield")
            file = open(filename, 'wb')
            ret = bytes(ceil(len(self.pieceList)/8))
            file.write(ret)
            file.close()
            return ret

    def _updateBitfield(self, pieceIndex, addPiece=True):
        # print(BitArray(self.bitfield))
        tmp = BitArray(self.bitfield)
        tmp.set(addPiece, pieceIndex)
        self.bitfield = tmp.bytes

    def _updateOtherBitfield(self, pieceIndex, peerID):
        tmp = BitArray(self.activePeerList[peerID].bitfield)
        tmp.set(True, pieceIndex)
        self.activePeerList[peerID].bitfield = tmp.bytes

    def _writePiece(self, piece):  # write a Piece to file
        # print(piece.blockList)
        self.file = open(self.downloadFilename, 'ab')
        self.file.seek(piece.pieceIndex * self.pieceLength)
        blockOffsets = sorted(list(piece.blockList.keys()))
        # print(blockOffsets)
        # ret = 0
        for offset in blockOffsets:
            self.file.write(piece.blockList[offset].data)
        # print(ret)
        self.file.close()
        file = open(self.bitfieldFilename, 'wb')
        file.write(self.bitfield)
        file.close()
        count = 0
        for piece in self.pieceList:
            if piece.have == True:
                count += 1 
                # return
        print("Received %d pieces" % count)
        if(count == len(self.pieceList)):
            self._downloadFinished()

    def _downloadFinished(self):
        print(self.downloadFilename, " downloaded.")

        # xh adds
    def _getInfoHash(self):
        return self.info_hash

    def _getPeerID(self):
        return self.peerID

    def _getBitfield(self):
        return self.bitfield

    # need not blockLen
    def _getBlockData(self, pieceIndex, blockOffset, blockLen):
        return self.pieceList[pieceIndex].blockList[blockOffset].data

    def _isActivePeerID(self, peerID):
        for ID in self.activePeerList:
            if peerID == ID:
                return True
        return False

    def _addActivePeer(self, peerID, protocol):
        self.activePeerList[peerID] = ActivePeer(peerID, protocol)

    def _addActivePeerBitfield(self, peerID, bitfield):
        self.activePeerList[peerID].bitfield = bitfield

    def _pieceFinished(self, pieceIndex):
        self.pieceList[pieceIndex].have = True
        self.requestCount -= len(self.pieceList[pieceIndex].requestList)
        for activePeer in self.activePeerList.values():
            activePeer.protocol._sendHave(pieceIndex)
        self._writePiece(self.pieceList[pieceIndex])
        self._updateBitfield(pieceIndex)
    
    def _blockReceived(self, pieceIndex, blockOffset, data, dataSize):
        self.pieceList[pieceIndex].blockList[blockOffset].data = data
        self.pieceList[pieceIndex].blockList[blockOffset].dataReceived = True
        for block in self.pieceList[pieceIndex].blockList.values():
            if block.dataReceived != True:
                return 
        self._pieceFinished(pieceIndex)
        
    def peerListReceived(self, peerList):
        self.peerList = peerList
        for peer in peerList:
            if peer not in self.connected:
                if peer == ('127.0.0.1', self.peerPort):
                    self.connected[peer] = True
                else:
                    self.connected[peer] = False

    def tryConnectPeer(self):
        # print(self.peerList)
        if len(self.activePeerList) < MAX_NUM_ACTIVE_PEERS:
            for peer in self.peerList:
                if not self.connected[peer]:
                    self.reactor.connectTCP(peer[0], peer[1], self.Clientfactory)
                    self.connected[peer] = True
                    # print("try connect")
                    return

    def tryAddRequest(self):  # add a peer to a request list
        if self.requestCount < MAX_NUM_REQUESTS:
            # TODO : rarest-first order
            for pieceIndex in range(len(self.pieceList)):
                piece = self.pieceList[pieceIndex]
                if not piece.have and len(piece.requestList) < MAX_NUM_REQUESTS_PER_PIECE:
                    for peer in self.activePeerList.values():
                        if not peer.peerID in piece.requestList:
                            bitfield = BitArray(peer.bitfield)
                            if bitfield[pieceIndex]:
                                self.pieceList[pieceIndex].requestList.append(peer.peerID)
                                self.requestCount += 1
                                # print("try add request")        
                                return

    def trySendRequest(self):
        #for pieceIndex in range(len(self.pieceList)):
        for piece in self.pieceList:
            if not piece.have and len(piece.requestList) > 0:
                for block in piece.blockList.values():
                    if not block.requestSent and not block.dataReceived:
                        sel = random.randint(0, len(piece.requestList)-1)
                        peerID = piece.requestList[sel]
                        self.activePeerList[peerID].protocol._sendRequest(piece.pieceIndex,
                                                                          block.offset,
                                                                          block.size)
                        self.pieceList[piece.pieceIndex].blockList[block.offset].requestSent = True
                        # print("send request")        
                        return


    # TODO : timeout and abort connections
    # TODO : cap on active peers should apply to income connection

