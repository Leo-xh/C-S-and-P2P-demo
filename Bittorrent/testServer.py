import struct
import socket
import utils
import random
#from twisted.internet import reactor
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory

from handshake import *
if __name__ == '__main__':
    reactor.listenTCP(56789,HandshakeFactory(info_hash="11111111111111111111"))
    reactor.connectTCP('127.0.0.1',46352,HandshakeFactory(info_hash="11111111111111111111"))
    reactor.run()