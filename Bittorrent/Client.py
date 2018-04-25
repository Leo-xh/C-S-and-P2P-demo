import struct
import random
from utils import *
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol


class RequestClient(DatagramProtocol):
    ''' connect to the tracker and get response '''
    '''
    1. send a connect datagram when start running until received a response
    2. store the connection_id and send a announce request until recived a
        response
    3. retransmit methods
    4. the connection_id is expired 60s since received
    '''

    def __init__(self, protocol_id=0, ipstr='127.0.0.1',
                 port=6789, trackerIpstr='127.0.0.1',
                 trackerPort=6789, **args,):
        '''
        args must contains the following items:
                1. info_hash
                2. peer_id
                3. downloaded
                4. left
                5. uploaded
                6. event
                7. key
                8. num_want
        '''
        super(RequestClient, self).__init__()
        self.protocol_id = args['protocol_id']

        self.info_hash = args['info_hash']
        self.peer_id = args['peer_id']
        self.downloaded = args['downloaded']
        self.left = args['left']
        self.uploaded = args['uploaded']
        self.event = args['event']
        self.key = args['key']
        self.num_want = args['num_want']

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

    def startProtocol(self):
        print("The requestClient is running")
        connect()

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
                announce()
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
                    self.peerList.append((ip, port))

    def connect(self):
        self.retransTimesConn += 1
        self.transaction_id = random.randint(0, 2 * 32 - 1)
        action = 0
        packet = struct.pack(
            connectReqFormat, self.protocol_id, action, self.transaction_id)
        self.transport.write(packet, (self.trackerIpstr, trackerPort))
        self.retransConn = reactor.callLater(
            15 * 2**self.retransTimesConn, self.connect)

    def announce(self):
        self.retransAnnoun += 1
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
    trackerPort = 6789
    reactor.listenUDP(trackerPort, RequestClient(), trackerIpstr)
    reactor.run()
