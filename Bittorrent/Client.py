import struct
import random
import socket
import utils
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

import time
begin = time.time()


def printTime():
    print("t = %d, " % (time.time() - begin), end='')


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
    ClientIpStr is the listening TCP ip, and ClientPort is the corresponding port.
    '''

    def __init__(self, peer, peerPort, trackerIpstr='127.0.0.1', trackerPort=56789, **args):

        super(RequestClient, self).__init__()
        self.peer = peer
        self.peerPort = peerPort
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
        self.clientIpstr = args['clientIpstr']
        self.clientPort = args['clientPort']
        self.clientIP = utils.ip2int(self.clientIpstr)
        self.trackerIpstr = trackerIpstr
        self.trackerIp = utils.ip2int(self.trackerIpstr)
        self.trackerPort = trackerPort
        self.udp_port = self.clientPort

        self.interval = 0
        self.transaction_id = 0
        self.connection_id = 0
        self.connectReqFormat = "!QII"
        self.connectRecvFormat = "!IIQ"
        self.announceReqFormat = "!QII20s20sQQQIIIIH"
        self.announceRecvFormat = "!III"  # following N (ip-port) turples

        self.retransConn = None
        self.retransTimesConn = -1
        self.retransAnnoun = None
        self.retransTimesAnnoun = -1
        self.peerList = []
        self.connected = False
        self.intervalAnnounce = None

        # socket for the client
        self.portSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.portSocket.setblocking(False)
        self.portSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.portSocket.bind((self.clientIpstr, self.udp_port))

        # start the reactor with a sentence and connect to the tracket
    def startProtocol(self):
        print("The requestClient is running")
        self.connect()

    def stopProtocol(self):
        print("The requestClient is stopped")
        self.portSocket.close()


#        reactor.stop()

    def expired(self):
        self.connected = False

    def datagramReceived(self, datagram, addr):
        '''
        Receive the packet.
        Check whether the packet is at least 16 bytes or 20 bytes for announce.
        Check whether the transaction ID is equal to the one you chose.
        Check whether the action is connect or announce.
        Store the connection ID and interval for future use.
        Do not announce again until interval seconds have passed.
        '''
        if (len(datagram) < 16
                or (self.connected is True and len(datagram) < 12)):
            return
        dataRecv = struct.unpack("!II", datagram[:8])
        actionRecv = dataRecv[0]
        transaction_idRecv = dataRecv[1]
        if (transaction_idRecv == self.transaction_id):
            # connect response
            if (actionRecv == 0):
                self.retransTimesConn = -1
                self.retransTimesAnnoun = -1
                self.retransConn.cancel()
                connection_idRecv = struct.unpack("!Q", datagram[8:])
                self.connection_id = connection_idRecv[0]
                self.connected = True
                reactor.callLater(60, self.expired)
                self.announce()

            # announce response
            elif (actionRecv == 1):
                self.retransTimesConn = -1
                self.retransTimesAnnoun = -1
                self.retransAnnoun.cancel()
                self.peerList = []
                intervalRecv = struct.unpack("!I", datagram[8:12])
                self.interval = intervalRecv[0]
                sizeOfpeerList = (len(datagram) - 12) // 6
                for i in range(0, sizeOfpeerList):
                    (ip, port) = struct.unpack(
                        "!IH", datagram[12 + i * 6:12 + (i + 1) * 6])
                    self.peerList.append((utils.int2ip(ip), port))
                # for peerAddr in self.peerList:
                #     print(peerAddr)
                # print("\n")
#                print(self.peerList)
                self.peer.peerListReceived(self.peerList)
                self.intervalAnnounce = reactor.callLater(
                    self.interval, self.announce)

    '''
    for connect and announce:
    Choose a random transaction ID.
    Fill the connect request structure.
    Send the packet.
    And control the transmission, the tranmit times.
    '''

    def connect(self):
        '''
        Offset  Size            Name            Value
        0       64-bit integer  protocol_id     0x41727101980 // magic constant
        8       32-bit integer  action          0 // connect
        12      32-bit integer  transaction_id
        '''
        self.retransTimesConn += 1
        printTime()
        print("connecting, the %dth try" % self.retransTimesConn)
        self.transaction_id = random.randint(0, 2 * 32 - 1)
        action = 0
        packet = struct.pack(self.connectReqFormat, self.protocol_id, action,
                             self.transaction_id)
        self.transport.write(packet, (self.trackerIpstr, self.trackerPort))
        self.retransConn = reactor.callLater(15 * 2**self.retransTimesConn,
                                             self.connect)
        if (self.retransTimesConn == 8):  # reset retransTimesConn
            self.retransTimesConn = -1

    def announce(self):
        if (not self.connected):
            if (self.intervalAnnounce is not None
                    and self.intervalAnnounce.active()):
                self.intervalAnnounce.cancel()
            if (self.retransAnnoun is not None
                    and self.retransAnnoun.active()):
                self.retransAnnoun.cancel()
            self.connect()
            return
        #    if(self.intervalAnnounce is not None):
        #    if(self.retransAnnoun is not None):
        self.retransTimesAnnoun += 1
        # if (self.retransTimesAnnoun > 0):
        #     self.retransAnnoun.cancel()
        printTime()
        print("announcing, the %dth try" % self.retransTimesAnnoun)
        self.transaction_id = random.randint(0, 2**31 - 1)
        '''
        Offset  Size    Name    Value
        0       64-bit integer  connection_id
        8       32-bit integer  action           1 // announce
        12      32-bit integer  transaction_id
        16      20-byte string  info_hash
        36      20-byte string  peer_id
        56      64-bit integer  downloaded
        64      64-bit integer  left
        72      64-bit integer  uploaded
        80      32-bit integer  event            0 // 0: none;    1: completed; 
                                                     2: started; 3: stopped;
        84      32-bit integer  IP address       0 // default
        88      32-bit integer  key
        92      32-bit integer  num_want         -1 // default
        96      16-bit integer  port
        '''
        packet = struct.pack(self.announceReqFormat, self.connection_id, 1,
                             self.transaction_id, self.info_hash,
                             self.peer_id.encode(), self.downloaded, self.left,
                             self.uploaded, self.event, self.clientIP,
                             self.key, self.num_want, self.peerPort)
        self.transport.write(packet, (self.trackerIpstr, self.trackerPort))
        # reset the Timer
        if (self.retransAnnoun is not None and self.retransAnnoun.active()):
            self.retransAnnoun.cancel()
        self.retransAnnoun = reactor.callLater(15 * 2**self.retransTimesAnnoun,
                                               self.announce)

if __name__ == '__main__':

    clientIpstr = '127.0.0.1'
    # clientPort = 56777
    clientPort = random.randint(10000, 60000)

    protocol_id = 1
    info_hash = '0'
    peer_id = '0'
    downloaded = 0
    left = 0
    uploaded = 0
    event = 0
    key = 0
    num_want = 0

    reqClient = RequestClient(
        peer,
        clientIpstr=clientIpstr,
        clientPort=clientPort,
        protocol_id=1,
        info_hash=info_hash,
        peer_id=peer_id,
        downloaded=downloaded,
        left=left,
        uploaded=uploaded,
        event=event,
        key=key,
        num_want=num_want)
    # in order to adopt a reusable port
    port = reactor.adoptDatagramPort(reqClient.portSocket.fileno(),
                                     socket.AF_INET, reqClient)
    reactor.run()
