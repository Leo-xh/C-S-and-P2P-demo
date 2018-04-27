import struct
import utils
from twisted.internet.protocol import Protocol
from peer import Peer
from bitstring import BitArray


class PeerProtocol(Protocol):

    def __init__(self, peer):
        self.peer = peer
        self.bitfieldSent = False
        self.protocolName = "Compact Bittorrent Protocol/1.0"
        self.protocolself.msgLen = len(self.protocolName)
        self.formatForHandshake = "!B%ds8s20s20s" % self.protocolself.msgLen
        self.formatMessageHead = "!IB"  # message self.msgLen and messaeg id
        self.bitfieldRecv = b''
        self.msgLen = 0
        self.msgID = -1
        self.recvBuff = b''
        #        xh adds, used to denote that handshake is finished
        self.shaked = False
        self.shakeSend = False

    def connectionMade(self):
        print("Handshaking to ", self.transport.getPeer())
        self.__handshake()

    def connectionLost(self):
        print("connection Lost")

    def dataReceived(self, data):
        pass

    def handshakeReceived(self, data):
        print("Handshake from ", self.transport.getPeer())
#        self.msgLen = struct.unpack('!B', self.recvBuff[0:1])[0]
#        if(len(self.recvBuff) < self.msgLen + 49):
#            return
#        else:
        (self.msgLen, protocolNameRecv, reserved, infohashRecv,
         peerIDRecv) = struct.unpack(self.formatForHandshake, self.recvBuff[0:self.msgLen + 49])
        protocolNameRecv = protocolNameRecv.decode()
        peerIDRecv = peerIDRecv.decode()
        infohashRecv = infohashRecv.decode()
        if((protocolNameRecv != self.protocolName) or (infohashRecv != self.peer.__getInfoHash())
           or (peerIDRecv == self.peer.__getpeerID())):
            self.transport.abortConnection()
            print("handshake fail")
        else:
            self.recvBuff = self.recvBuff[self.msgLen + 49:]
            print("handshake received")
            self.__handshake()
            self.shaked = True
            self.__sendBitfield()

    def handshakeReplyReceived(self, data):
        print("Handshake rely from ", self.transport.getPeer())
#        self.recvBuff += data
#        self.msgLen = struct.unpack('!B', self.recvBuff[0:1])[0]
#        if(len(self.recvBuff) < self.msgLen + 49):
#            return
#        else:
        (self.msgLen, protocolNameRecv, reserved, infohashRecv,
         peerIDRecv) = struct.unpack(self.formatForHandshake, self.recvBuff[0:self.msgLen + 49])
        protocolNameRecv = protocolNameRecv.decode()
        peerIDRecv = peerIDRecv.decode()
        infohashRecv = infohashRecv.decode()
        if((protocolNameRecv != self.protocolName) or (infohashRecv != self.peer.__getInfoHash())
           or (peerIDRecv == self.peer.__getpeerID())):
            self.transport.abortConnection()
            print("handshake fail")
        else:
            self.recvBuff = self.recvBuff[self.msgLen + 49:]
            print("handshake finished")
            self.shaked = True
            self.__sendBitfield()

    def bitfieldReceived(self, data):
        print("bitfield Received")
#        self.msgLen = struct.unpack('!I', self.recvBuff[0:4])[0]
#        if(self.msgLen > len(data) - 4):
#            self.recvBuff += data
#            return
        self.bitfieldRecv = struct.unpack(
            '!%ds' % self.msgLen, self.recvBuff[5:])[0]
        if(self.bitfieldSent == False):
            self.__sendBitfield()

    def requestReceived(self, data):
        # message ID is 6
        if len(self.recvBuff) < 12:
            return
        pieceID, blockOffset, blockLen = struct.unpack("!III",
                                                       self.recvBuff[0:12])
        self.recvBuff = self.recvBuff[12:]
        sendData = self.peer.getBlockData(pieceID, blockOffset, blockLen)
        packet = struct.pack("!BII%ds" % (blockLen), 7, pieceID, blockOffset,
                             sendData.decode())  # ?? need decode() ?
        packet = struct.pack("!I", len(packet)) + packet
        self.transport.write(packet)

    def haveReceived(self, data):
        print("Have receive")
#        self.msgLen = struct.unpack('!I', self.recvBuff[0:4])[0]
#        if(self.msgLen > len(data) - 4):
#            self.recvBuff += data
#            return
        position = struct.unpack('!I', self.recvBuff[5:])[0]
        bitfield = BitArray(self.bitfieldRecv)
        bitfield.set(True, position)
        self.bitfieldRecv = bitfield.bytes

    def sendHave(self, pieceIndex):
        print("sending Have")
        packet = struct.pack(self.formatMessageHead, 5, 4, pieceIndex)
        self.transport.write(packet)

    def __handshake(self):
        print("shaking")
        packet = struct.pack(self.formatForHandshake, self.protocolself.msgLen, self.protocolName.encode(), bytes(8),
                             self.peer.__getInfoHash().encode(), self.peer.__getPeerId().encode())
        self.transport.write(packet)
        self.shakeSend = True

    def __sendBitfield(self):
        print("sending bitfield")
        self.msgLenOfBitfield = len(self.peer.__getBitfield()) + 1
        packet = struct.pack((self.formatMessageHead + "%ds") % self.msgLenOfBitfield,
                             self.msgLenOfBitfield + 1, 5, self.peer.__getBitfield())
        self.transport.write(packet)
        self.bitfieldSent = True

    def pieceReceived(self, data):
        # message ID is 7
        # if piece download finished, call Peer.pieceFinished
        if len(self.recvBuff) < 8 + self.msgLen:
            return
        pieceID, blockOffset = struct.unpack("!II", self.recvBuff[0:8])
        pieceData = self.recvBuff[8:self.msgLen]
        self.recvBuff = self.recvBuff[self.msgLen:]
        self.peer.pieceFinished(pieceID, blockOffset, pieceData)
