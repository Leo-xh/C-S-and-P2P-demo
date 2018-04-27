import struct
import utils
from twisted.internet.protocol import Protocol
from peer import Peer
from bitstring import BitArray


class PeerProtocol(Protocol):
    protocolName = "Compact Bittorrent Protocol/1.0"
    protocolMsgLen = len(protocolName)
    formatForHandshake = "!B%ds8s20s20s" % protocolMsgLen
    formatMessageHead = "!IB"  # message self.msgLen and message id

    def __init__(self, peer):
        self.peer = peer
        self.bitfieldSent = False
        self.bitfieldRecv = b''
        self.msgLen = 0  # 4 bytes
        self.msgID = -1  # 1 bytes
        self.recvBuff = b''
        #        xh adds, used to denote that handshake is finished
        self.shaked = False
        self.shakeSend = False

    def __handshake(self):
        print("shaking")
        packet = struct.pack(formatForHandshake, protocolMsgLen,
                             protocolName.encode(), bytes(8),
                             self.peer.__getInfoHash().encode(),
                             self.peer.__getPeerId().encode())
        self.transport.write(packet)
        self.shakeSend = True

    def __sendBitfield(self):
        print("sending bitfield")
        self.msgLenOfBitfield = len(self.peer.__getBitfield()) + 1
        packet = struct.pack(
            (formatMessageHead + "%ds") % self.msgLenOfBitfield,
            self.msgLenOfBitfield + 1, 5, self.peer.__getBitfield())
        self.transport.write(packet)
        self.bitfieldSent = True

    def __sendHave(self, pieceIndex):
        print("sending Have")
        packet = struct.pack(formatMessageHead, 5, 4, pieceIndex)
        self.transport.write(packet)

    def __sendRequest(self, pieceIndex, blockOffset, blockLength):
        packet = struct.pack("!IBIII", 13, 6, pieceIndex, blockOffset,
                             blockLength)
        self.transport.write(packet)

    def __sendPiece(self, pieceIndex, blockOffset, blockData):
        packet = struct.pack("!BII%ds" % len(blockData), 7, pieceID,
                             blockOffset, blockData)
        packet = struct.pack("!I", len(packet)) + packet
        self.transport.write(packet)

    def connectionMade(self):
        print("Handshaking to ", self.transport.getPeer())
        self.__handshake()

    def connectionLost(self):
        print("connection Lost")

    def dataReceived(self, data):
        self.recvBuff += data
        if len(self.recvBuff) == 0:
            return
        if self.shaked == False:  # handshake
            if len(self.recvBuff) >= struct.unpack("!B",
                                                   self.recvBuff)[0] + 49:
                if self.shakeSend == False:  # handshake recv
                    self.handshakeReceived()
                else:  # handshake reply recv
                    self.handshakeReplyReceived()
        else:  # others
            if len(self.recvBuff) >= 5:
                self.msgLen, self.msgID = struct.unpack("!IB", self.recvBuff)
                if len(self.recvBuff) >= self.msgLen + 4:
                    if self.msgID == 4:
                        self.haveReceived()
                    elif self.msgID == 5:
                        self.bitfieldReceived()
                    elif self.msgID == 6:
                        self.requestReceived()
                    elif self.msgID == 7:
                        self.pieceReceived()

    def handshakeReceived(self):
        print("Handshake from ", self.transport.getPeer())
        #        self.msgLen = struct.unpack('!B', self.recvBuff[0:1])[0]
        #        if(len(self.recvBuff) < self.msgLen + 49):
        #            return
        #        else:
        (self.msgLen, protocolNameRecv,
         reserved, infohashRecv, peerIDRecv) = struct.unpack(
             formatForHandshake, self.recvBuff[0:self.msgLen + 49])
        protocolNameRecv = protocolNameRecv.decode()
        peerIDRecv = peerIDRecv.decode()
        infohashRecv = infohashRecv.decode()
        if ((protocolNameRecv != protocolName)
                or (infohashRecv != self.peer.__getInfoHash())
                or (peerIDRecv == self.peer.__getpeerID())):
            self.transport.abortConnection()
            print("handshake fail")
        else:
            self.recvBuff = self.recvBuff[self.msgLen + 49:]
            print("handshake received")
            self.__handshake()
            self.shaked = True

    def handshakeReplyReceived(self):
        print("Handshake rely from ", self.transport.getPeer())
        #        self.recvBuff += data
        #        self.msgLen = struct.unpack('!B', self.recvBuff[0:1])[0]
        #        if(len(self.recvBuff) < self.msgLen + 49):
        #            return
        #        else:
        (self.msgLen, protocolNameRecv,
         reserved, infohashRecv, peerIDRecv) = struct.unpack(
             formatForHandshake, self.recvBuff[0:self.msgLen + 49])
        protocolNameRecv = protocolNameRecv.decode()
        peerIDRecv = peerIDRecv.decode()
        infohashRecv = infohashRecv.decode()
        if ((protocolNameRecv != protocolName)
                or (infohashRecv != self.peer.__getInfoHash())
                or (peerIDRecv == self.peer.__getpeerID())):
            self.transport.abortConnection()
            print("handshake fail")
        else:
            self.recvBuff = self.recvBuff[self.msgLen + 49:]
            print("handshake finished")
            self.shaked = True
            self.__sendBitfield()

    def bitfieldReceived(self):
        print("bitfield Received")
        #        self.msgLen = struct.unpack('!I', self.recvBuff[0:4])[0]
        #        if(self.msgLen > len(data) - 4):
        #            self.recvBuff += data
        #            return
        self.bitfieldRecv = struct.unpack('!%ds' % self.msgLen - 1,
                                          self.recvBuff[5:self.msgLen + 4])[0]
        self.recvBuff = self.recvBuff[self.msgLen + 4:]
        if (self.bitfieldSent == False):
            self.__sendBitfield()

    def requestReceived(self):
        # message ID is 6
        pieceID, blockOffset, blockLen = struct.unpack("!III",
                                                       self.recvBuff[5:17])
        self.recvBuff = self.recvBuff[17:]
        blockData = self.peer.__getBlockData(pieceID, blockOffset, blockLen)
        self.__sendPiece(pieceID, blockOffset, blockData)

    def haveReceived(self):
        print("Have receive")
        #        self.msgLen = struct.unpack('!I', self.recvBuff[0:4])[0]
        #        if(self.msgLen > len(data) - 4):
        #            self.recvBuff += data
        #            return
        position = struct.unpack('!I', self.recvBuff[5:9])[0]
        self.recvBuff = self.recvBuff[9:]
        bitfield = BitArray(self.bitfieldRecv)
        bitfield.set(True, position)
        self.bitfieldRecv = bitfield.bytes

    def pieceReceived(self):
        # message ID is 7
        # if piece download finished, call Peer.pieceFinished
        pieceID, blockOffset = struct.unpack("!II", self.recvBuff[5:13])
        pieceData = self.recvBuff[13:self.msgLen + 4]
        self.recvBuff = self.recvBuff[self.msgLen + 4:]
        self.peer.__pieceFinished(pieceID, blockOffset, pieceData)
