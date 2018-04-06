import sys
import os
import socket
import struct
import threading
from Crypto.Cipher import AES
# -*- coding=utf-8 -*-

'''
use serverIp = '127.0.0.1', serverPort = 6789
'''

'''
Protocol type is MFTP(0)
Service is File Transfer(0)
Version is 1.0
ID is choosed as the first number that is not in IDs
'''
serverIp = '127.0.0.1'
serverPort = 6789
IDs = []
messageSize = 2060  # head plus databody
reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
reqSocket.connect((serverIp, serverPort))


def request(fileName, filePath):
    print("Requesting %s" % fileName)
    global reqSocket
    idExp = 0
    while True:
        if idExp not in IDs:
            break
    protocol = 0
    service = 0
    version = 1
    packet = struct.pack('!4H200s', protocol, service,
                         version, idExp, fileName.encode())
    reqSocket.send(packet)
    with open(os.path.join(filePath, fileName), 'wb') as file:
        while True:
            more = reqSocket.recv(messageSize)
            if more:
                header = struct.unpack('!6H', more[:12])
                recvErrorCode = header[5]
                recvLen = header[4]
                idRecv = header[3]
                if recvErrorCode == 1:
                    print("File does not exist, please check the inputted name")
                    break
                if recvLen == 0:
                    print("File Received, saved as %s" %
                          os.path.join(filePath, fileName))
                    break
                recvData = struct.unpack('!%ds' % (recvLen - 12), more[12:])
                file.write(recvData[0])


def client():
    # fileName = input("Please enter the name of the file:")
    # filePath = input("Please enter the path of the file:")
    fileName = "test.mp4"
    filePath = ""
    request(fileName, filePath)

if __name__ == '__main__':
    client()
