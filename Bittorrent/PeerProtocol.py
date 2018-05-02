import struct
import utils
import time
#import Peer
from twisted.internet.protocol import Protocol

from bitstring import BitArray

class PeerProtocol(Protocol):

    protocolName = "Compact Bittorrent Protocol/1.0"
    protocolMsgLen = len(protocolName)
    formatForHandshake = "!B%ds8s20s20s" % protocolMsgLen
    formatMessageHead = "!IB"  # message self.msgLen and message id

    def __init__(self, peer):
        self.peer = peer
        #self.bitfield = peer.bitfield
        self.bitfieldSent = False
        #self.bitfieldRecv = b''
        self.msgLen = 0  # 4 bytes
        self.msgID = -1  # 1 bytes
        self.recvBuff = b''
        # xh adds, used to denote that handshake is finished
        self.shaked = False
        self.shakeSent = False
        self.peerIDRecv = None

        self.sendConn = False

    def _handshake(self):
        # print(time.time(), end='')
        # print("Handshaking to ", self.transport.getPeer())
        packet = struct.pack(self.formatForHandshake, self.protocolMsgLen,
                             self.protocolName.encode(), bytes(8),
                             self.peer._getInfoHash(),
                             self.peer._getPeerID().encode())
        self.transport.write(packet)
        self.shakeSent = True

    def _sendBitfield(self):
        # print("sending bitfield")
        LenOfBitfield = len(self.peer._getBitfield())
        packet = struct.pack(
            (self.formatMessageHead + "%ds") % LenOfBitfield,
            LenOfBitfield + 1, 5, self.peer._getBitfield())
        # print(packet)
        self.transport.write(packet)
        self.bitfieldSent = True

    def _sendHave(self, pieceIndex):
        # print("sending Have")
        packet = struct.pack(self.formatMessageHead+'I', 5, 4, pieceIndex)
        self.transport.write(packet)

    def _sendRequest(self, pieceIndex, blockOffset, blockLength):
        packet = struct.pack("!IBIII", 13, 6, pieceIndex, blockOffset,
                             blockLength)
        self.transport.write(packet)

    def _sendPiece(self, pieceIndex, blockOffset, blockData):
        packet = struct.pack("!BII%ds" % len(blockData), 7, pieceIndex,
                             blockOffset, blockData)
        packet = struct.pack("!I", len(packet)) + packet
        self.transport.write(packet)

    def connectionMade(self):
        if self.sendConn == True:
            self._handshake()

    def connectionLost(self, reason): # ychz debug 17:36
        print("connection Lost")

    def dataReceived(self, data):
        # print("reve data /////")
        # print(data)

        self.recvBuff += data
        # print(self.recvBuff)
        if len(self.recvBuff) == 0:
            return
        if self.shaked == False:  # handshake
            self.msgLen = struct.unpack("!B", self.recvBuff[0:1])[0] + 49
            if len(self.recvBuff) >= self.msgLen:
                if self.shakeSent == False:  # handshake recv
                    self.handshakeReceived()
                else:  # handshake reply recv
                    self.handshakeReplyReceived()
        else:  # others
            if len(self.recvBuff) >= 5:
                self.msgLen, self.msgID = struct.unpack("!IB", self.recvBuff[0:5])
                # print(self.msgLen)
                # print(self.msgID)
                if len(self.recvBuff) >= self.msgLen + 4:
                    # print("yes")
                    if self.msgID == 4:
                        self.haveReceived()
                    elif self.msgID == 5:
                        self.bitfieldReceived()
                    elif self.msgID == 6:
                        self.requestReceived()
                    elif self.msgID == 7:
                        self.pieceReceived()
    
    def handshakeReceived(self):
        # print(time.time(), end='')
        # print("Handshake from ", self.transport.getPeer())
        (protocolNameRecv,
         reserved, infohashRecv, peerIDRecv) = struct.unpack(
             "!%ds8s20s20s" % (self.protocolMsgLen), self.recvBuff[1:self.msgLen])
        self.recvBuff = self.recvBuff[self.msgLen:]
        protocolNameRecv = protocolNameRecv.decode()
        peerIDRecv = peerIDRecv.decode()
        infohashRecv = infohashRecv
        if ((protocolNameRecv != self.protocolName)
                or (infohashRecv != self.peer._getInfoHash())
                or (peerIDRecv == self.peer._getPeerID())
                or (self.peer._isActivePeerID(peerIDRecv))):
            self.transport.abortConnection()
            # print("handshake fail")
        else:
            # print("handshake received")
            self._handshake()
            self.shaked = True
            self.peer._addActivePeer(peerIDRecv, self)
            self.peerIDRecv = peerIDRecv

    def handshakeReplyReceived(self):
        # print(time.time(), end='')
        # print("Handshake reply from ", self.transport.getPeer())
        ( protocolNameRecv,
         reserved, infohashRecv, peerIDRecv) = struct.unpack(
             "!%ds8s20s20s" % (self.protocolMsgLen), self.recvBuff[1:self.msgLen])
        self.recvBuff = self.recvBuff[self.msgLen:]
        protocolNameRecv = protocolNameRecv.decode()
        peerIDRecv = peerIDRecv.decode()
        infohashRecv = infohashRecv
        if ((protocolNameRecv != self.protocolName)
                or (infohashRecv != self.peer._getInfoHash())
                or (peerIDRecv == self.peer._getPeerID())
                or (self.peer._isActivePeerID(peerIDRecv))):
            self.transport.abortConnection()
            print("handshake failed")
        else:
            # print("handshake finished")
            self.shaked = True
            self._sendBitfield()
            self.peerIDRecv = peerIDRecv
            self.peer._addActivePeer(peerIDRecv, self)
            # print(peerIDRecv)

    def bitfieldReceived(self):
        # print("bitfield Received")
        self.bitfieldRecv = struct.unpack('!%ds' % (self.msgLen - 1),
                                          self.recvBuff[5:self.msgLen + 4])[0]
        self.recvBuff = self.recvBuff[self.msgLen + 4:]
        if (self.bitfieldSent == False):
            self._sendBitfield()
        # print(self.peerIDRecv)
        self.peer._addActivePeerBitfield(self.peerIDRecv, self.bitfieldRecv)

    def requestReceived(self):
        # message ID is 6
        print("requested")
        pieceIndex, blockOffset, blockLen = struct.unpack("!III",
                                                       self.recvBuff[5:17])
        self.recvBuff = self.recvBuff[17:]
        blockData = self.peer._getBlockData(pieceIndex, blockOffset, blockLen)
        self._sendPiece(pieceIndex, blockOffset, blockData)

    def haveReceived(self):
        # print("Have receive")
        pieceIndex = struct.unpack('!I', self.recvBuff[5:9])[0]
        self.recvBuff = self.recvBuff[9:]
        self.peer._updateOtherBitfield(pieceIndex, self.peerIDRecv)
        # TODO change other peers

    def pieceReceived(self):
        # message ID is 7
        # if piece download finished, call Peer.pieceFinished
        # print("piece")
        pieceIndex, blockOffset = struct.unpack("!II", self.recvBuff[5:13])
        pieceData, = struct.unpack("%ds" % (self.msgLen-9), self.recvBuff[13:self.msgLen + 4])
        self.recvBuff = self.recvBuff[self.msgLen+4:]
        self.peer._blockReceived(pieceIndex, blockOffset, pieceData, self.msgLen-9)
