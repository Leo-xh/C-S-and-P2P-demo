import struct
import random
import socket
from utils import *
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol


class RequestClient(DatagramProtocol):
    ''' connect to the tracker and get response
    1. send a connect datagram when start running until received a response
    2. store the connection_id and send a announce request until recived a
        response
    3. retransmit methods
    4. the connection_id is expired 60s since received
    args must contains the following items:
        1. info_hash
        2. peer_id
        3. downloaded
        4. left
        5. uploaded
        6. event
        7. key
        8. num_want
        9. protocol_id
    '''

    def __init__(self, ipstr='127.0.0.1',
                 port=56789, trackerIpstr='127.0.0.1',
                 trackerPort=56789, **args,):

        super(RequestClient, self).__init__()
        # data to transfer
        self.protocol_id = args['protocol_id']

        self.info_hash = args['info_hash']
        self.peer_id = args['peer_id']
        self.downloaded = args['downloaded']
        self.left = args['left']
        self.uploaded = args['uploaded']
        self.event = args['event']
        self.key = args['key']
        self.num_want = args['num_want']

        # data to use
        self.clientPort = args['clientPort']
        self.interval = 0
        self.transaction_id = 0
        self.connection_id = 0
        self.port = port
        self.ipstr = ipstr
        self.ip = ip2int(ipstr)
        self.trackerIpstr = trackerIpstr
        self.trackerIp = ip2int(self.trackerIpstr)
        self.trackerPort = trackerPort
        self.connectReqFormat = "!qii"
        self.connectRecvFormat = "!iiq"
        self.announceReqFormat = "!qii20s20sqqqiiiih"
        self.announceRecvFormat = "!iii"  # following N (ip-port) turples

        self.retransConn = None
        self.retransTimesConn = -1
        self.retransAnnoun = None
        self.retransTimesAnnoun = -1
        self.peerList = {}
        self.connected = False

        self.portSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.portSocket.setblocking(False)
        self.portSocket.bind(('127.0.0.1', self.clientPort))
        self.portSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # start the reactor with a sentence and connect to the tracket
    def startProtocol(self):
        print("The requestClient is running")
        self.connect()

    def stopProtocol(self):
        print("The requestClient is stopped")

    def datagramReceived(self, datagram, addr):
        if(len(datagram) < 16 or
                (self.connected is True and len(datagram) < 20)):
            return
        dataRecv = struct.unpack("!ii", datagram[:8])
        actionRecv = dataRecv[0]
        transaction_idRecv = dataRecv[1]
        if(transaction_idRecv == self.transaction_id):
            # connect response
            if(actionRecv == 0):
                self.retransTimesConn = -1
                self.retransConn.cancel()
                connection_idRecv = struct.unpack("!q", datagram[8:])
                self.connection_id = connection_idRecv
                self.connected = True
                self.announce()
                reactor.callLater(60, self.connect())
            # announce response
            elif(actionRecv == 1):
                self.retransTimesAnnoun = -1
                self.retransAnnoun.cancel()
                self.peerList = {}
                intervalRecv = struct.unpack("!q", datagram[8:12])
                self.interval = intervalRecv
                sizeOfpeerList = (len(datagram) - 12) / 6
                for i in range(0, sizeOfpeerList):
                    (ip, port) = struct.unpack(
                        "!ih", datagram[12 + i * 6:12 + (i + 1) * 6])
                    self.peerList.append((ip2int(ip), port))

    def connect(self):
        self.retransTimesConn += 1
        print("connecting, the %dth try" % self.retransTimesConn)
        self.transaction_id = random.randint(0, 2 * 32 - 1)
        action = 0
        packet = struct.pack(
            self.connectReqFormat, self.protocol_id,
            action, self.transaction_id)
        self.transport.write(packet, (self.trackerIpstr, trackerPort))
        self.retransConn = reactor.callLater(
            15 * 2**self.retransTimesConn, self.connect)

    def announce(self):
        self.retransAnnoun += 1
        print("announcing, the %dth try" % self.retransTimesAnnoun)
        self.transaction_id = randint(0, 2**32 - 1)
        packet = struct.pack(announceReqFormat, self.connection_id, 1,
                             self.transaction_id, self.info_hash,
                             self.peer_id, self.downloaded, self.left,
                             self.event, self.ip, self.key, self.num_want,
                             self.port)
        self.transport.write(packet, (self.trackerIpstr, trackerPort))
        self.retransTimesAnnoun = reactor.callLater(
            15 * 2**self.retransTimesAnnoun, self.announce)


if __name__ == '__main__':
    trackerIpstr = '127.0.0.1'
    protocol_id = 1
    trackerPort = 56789
    clientPort = 56788
    info_hash = 0
    peer_id = 0
    downloaded = 0
    left = 0
    uploaded = 0
    event = 0
    key = 0
    num_want = 0

    reqClient = RequestClient(clientPort=clientPort,
                              protocol_id=1, info_hash=info_hash,
                              peer_id=peer_id,
                              downloaded=downloaded,
                              left=left, uploaded=uploaded, event=event,
                              key=key, num_want=num_want)
    port = reactor.adoptDatagramPort(
        reqClient.portSocket.fileno(), socket.AF_INET, reqClient)
    reactor.run()
