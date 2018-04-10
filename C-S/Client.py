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
# messageSize = 2060  # head plus databody
messageSize = 1488


class UnExist(Exception):

    def __init__(self, arg="File does not exist, please check the input"):
        super(UnExist, self).__init__(arg)


def request(fileName, filePath):
    reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reqSocket.connect((serverIp, serverPort))
    print("Requesting %s" % fileName)
    idExp = 0
    while True:
        if idExp not in IDs:
            break
        idExp += 1
    IDs.append(idExp)
    protocol = 0
    service = 0
    version = 1
    packet = struct.pack('!4H200s', protocol, service, version, idExp,
                         fileName.encode())
    reqSocket.send(packet)
    recvBuff = b''
    try:
        with open(os.path.join(filePath, fileName), 'wb') as file:
            while True:
                recvBuff += reqSocket.recv(messageSize)

                while len(recvBuff) < 12:
                    recvBuff += reqSocket.recv(messageSize)

                header = struct.unpack('!6H', recvBuff[:12])
                recvErrorCode = header[5]
                recvLen = header[4]
                idRecv = header[3]

                if recvErrorCode == 1:
                    raise UnExist()
                    break

                if recvLen == 12:
                    print("File Received, sized %dB, ID %d, saved as %s" %
                          (os.path.getsize(os.path.join(filePath, fileName)),
                           idExp, os.path.join(filePath, fileName)))
                    IDs.remove(idExp)
                    break

                while len(recvBuff) < recvLen:
                    recvBuff += reqSocket.recv(messageSize)

                recvData = struct.unpack("!%ds" % (recvLen - 12),
                                         recvBuff[12:recvLen])
                file.write(recvData[0])

                recvBuff = recvBuff[recvLen:]
                # print("!%ds" % (recvLen - 12))
                # print("Received %dB" % recvLen)
    except UnExist as e:
        print(e.args)
        os.remove(os.path.join(filePath, fileName))

    except Exception as e:
        print(e.args)
        print(recvLen)
        os.remove(os.path.join(filePath, fileName))

        raise e

    reqSocket.close()


def client():
    operation = input(
        "Enter (R)equest to request a file, (E)xit to exit the client\n")
    while operation != 'E' or operation != 'e':
        fileName = input("Please enter the name of the file:")
        filePath = input("Please enter the path of the file:")
        if (filePath == ''):
            # filePath = 'D:\downloads'
            filePath = 'downloads'
            if (not os.path.exists(filePath)):
                os.makedirs(filePath)
        task = threading.Thread(target=request, args=(fileName, filePath))
        task.start()
        operation = input(
            "Enter (R)equest to request a file, (E)xit to exit the client\n")


if __name__ == '__main__':
    client()
