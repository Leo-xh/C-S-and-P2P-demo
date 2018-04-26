import struct
import socket
import utils
import random
#from twisted.internet import reactor
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory

class peerIDCreator(object):
    def __init__(self):
        self.version = 1.0
    def getPeerID(self):
        pid = 'M'+str(self.version).replace('.','-')+'-'
        for i in range(0,20-len(pid)):
            pid += chr(random.randint(0,127))
        return pid
    
'''
    the port and ip to connect is received
    args must contains:
        1. info_hash
        
'''
class Handshake(Protocol):
    def __init__(self,**args):
        self.protocolName = "Compact Bittorrent Protocol/1.0"
        self.protocolLength = len(self.protocolName)
        self.InfoHash = args['info_hash']
#        self.port = args['port']
#        self.ip = args['ip']
        self.peerIdCreator = peerIDCreator()
        self.peerID = self.peerIdCreator.getPeerID()
        self.format = "!B%ds8s20s20s"%self.protocolLength
        self.shaked = []
            
    def shake(self):
        print("shaking")
        packet = struct.pack(self.format, self.protocolLength,self.protocolName.encode(),
                             bytes(8),self.InfoHash.encode(),self.peerID.encode())
        self.transport.write(packet)
        
    def dataReceived(self, data):
        print("data received from ", self.transport.getPeer())
        buffer = b''
        buffer += data
#        print(buffer[0:1])
        # will the package be empty
        length = struct.unpack('!B',buffer[0:1])[0]
        if(len(buffer) < length+49):
            return
        else:
            (length, protocolNameRecv, reserved, infohashRecv, 
             peerIDRecv) = struct.unpack(self.format, buffer[0:length+49])
            protocolNameRecv = protocolNameRecv.decode()
            peerIDRecv = peerIDRecv.decode()
            infohashRecv = infohashRecv.decode()
            if((protocolNameRecv != self.protocolName) or (infohashRecv != self.InfoHash) 
               or (peerIDRecv == self.peerID)):
                self.transport.abortConnection()
                print("fail")
            else:
                buffer = buffer[length+49:]
                print("ok")
                if(peerIDRecv not in self.shaked):
                    self.shake()
                    self.shaked.append(peerIDRecv)
                
    def connectionLost(self, reason):
        print("the connection is shut down")            
                
    def connectionMade(self):
        self.shake()
    
class HandshakeFactory(ClientFactory):
#    protocol = Handshake
    def __init__(self, **args):
        self.protocol = None
        self.InfoHash = args['info_hash']
    def startedConnecting(self, connector):
        print("connecting to ", connector.getDestination())
    def buildProtocol(self, addr):
        print("connected")
        return Handshake(info_hash=self.InfoHash)
#        self.protocol = 
#        print(addr)
        

if __name__ == '__main__':
    reactor.listenTCP(46352,HandshakeFactory(info_hash="11111111111111111111"))
    reactor.connectTCP('127.0.0.1',56789,HandshakeFactory(info_hash="11111111111111111111"))
    reactor.run()