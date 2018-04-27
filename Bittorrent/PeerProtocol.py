from twisted.internet.protocol import Protocol
import struct


class PeerProtocol(Protocol):
    def __init__(self, peer):
        self.peer = peer
        self.bitfieldSent = False
        self.msgLen = 0  # ?? need ?
        self.msgID = 0  # ?? need ?
        self.recvBuff = b''

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
        pass

    def pieceReceived(self, data):
        # message ID is 7
        # if piece download finished, call Peer.pieceFinished
        if len(self.recvBuff) < 8 + self.msgLen:
            return
        pieceID, blockOffset = struct.unpack("!II", self.recvBuff[0:8])
        pieceData = self.recvBuff[8:self.msgLen]
        self.recvBuff = self.recvBuff[self.msgLen:]
        self.peer.pieceFinished(pieceID, blockOffset, pieceData)
