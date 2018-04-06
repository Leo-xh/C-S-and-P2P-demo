import sys
import os
import socket
import struct
import threading
from Crypto.Cipher import AES
# -*- coding=utf-8 -*-


serverIp = '127.0.0.1'
serverPort = 6789
messageSize = 2060
requestSize = 208
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((serverIp, serverPort))
serverSocket.listen(10)


def service():
    print("listening")
    while True:
        newsock, addrAndPort = serverSocket.accept()
        dealRequest(newsock, addrAndPort)


def dealRequest(sock, addrAndPort):
    resourPath = 'Resources'
    print("Tackleing a request from %s" % str(addrAndPort))
    request = sock.recv(requestSize)
    reqPro, reqSer, reqVer, reqId, filename = struct.unpack('!4H200s', request)
    filename = filename.decode().split('\00')[0]
    print("Sending file %s" % filename)
    if os.path.exists(os.path.join(resourPath, filename)):
        with open(os.path.join(resourPath, filename), 'rb') as sendFile:
            dataBody = sendFile.read(2048)
            errorCode = 0
            packet = struct.pack('!6H%ds' % len(
                dataBody), reqPro, reqSer, reqVer, reqId, 12 + len(dataBody), errorCode, dataBody)
            print("This packet is %dB" % len(packet))
            sock.sendall(packet)
    else:
        errorCode = 1
        packet = struct.pack('!6H', reqPro, reqSer,
                             reqVer, reqId, 12, errorCode)
        sock.sendall(packet)
    sock.close()

if __name__ == '__main__':
    service()
