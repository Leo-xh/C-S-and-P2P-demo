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
secretary_key = "project-C/S and P2P protocol key"
serverPort = 6789
IDs = []
# messageSize = 2060  # head plus databody
messageSize = 1036
Encryptor = AES.new(secretary_key)

protocol = 0
version = 1


class UnExist(Exception):

    def __init__(self, arg="File does not exist, please check the input"):
        super(UnExist, self).__init__(arg)


def request(fileName, filePath, ServiceOfThread):
    reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reqSocket.connect((serverIp, serverPort))
    print("Requesting %s" % fileName)
    idExp = 0
    while True:
        if idExp not in IDs:
            break
        idExp += 1
    IDs.append(idExp)
    packet = struct.pack('!4H200s', protocol, ServiceOfThread, version, idExp,
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
                recvSer = header[1]
                # may be valid length

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
                if ServiceOfThread == 1:
                    print(recvLen - 12)
                    recvData = Encryptor.decrypt(recvData[0])
                    recvData = recvData[:recvSer]
                else:
                    recvData = recvData[0]
                file.write(recvData)
                # print(recvData)

                recvBuff = recvBuff[recvLen:]
                # print("!%ds" % (recvLen - 12))
                # print("Received %dB" % recvLen)
    except UnExist as e:
        print(e.args)
        os.remove(os.path.join(filePath, fileName))

    except Exception as e:
        print(e.args)
        os.remove(os.path.join(filePath, fileName))

        raise e
    finally:
        reqSocket.close()


def lookup():
    reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reqSocket.connect((serverIp, serverPort))
    print("Looping up the server")
    ServiceOfThread = 2
    idExp = 0
    packet = struct.pack('!4H200s', protocol,
                         ServiceOfThread, version, idExp, b'')
    reqSocket.send(packet)
    recvBuff = b''
    Filelist = ''
    try:
        while True:
            recvBuff += reqSocket.recv(messageSize)

            while len(recvBuff) < 12:
                recvBuff += reqSocket.recv(messageSize)

            header = struct.unpack('!6H', recvBuff[:12])
            recvErrorCode = header[5]
            recvLen = header[4]
            idRecv = header[3]
            recvSer = header[1]
            # may be valid length

            if recvErrorCode == 1:
                raise UnExist()
                break

            if recvLen == 12:
                print(Filelist)
                break

            while len(recvBuff) < recvLen:
                recvBuff += reqSocket.recv(messageSize)

            recvData = struct.unpack("!%ds" % (recvLen - 12),
                                     recvBuff[12:recvLen])

            Filelist += recvData[0].decode()
            recvBuff = recvBuff[recvLen:]

    except Exception as e:
        print(e.args)


ModeDict = {"Plain": 0, "Encryted": 1}


def client():
    operation = ''
    while operation != 'E' or operation != 'e':
        if operation == 'R' or operation == 'r':
            fileName = input("Please enter the name of the file:")
            filePath = input("Please enter the path of the file:")
            Mode = input("Please choose the transmit mode(Plain or Encryted):")
            try:
                service = ModeDict[Mode]
            except Exception as e:
                continue
            if (filePath == ''):
                # filePath = 'D:\downloads'
                filePath = 'downloads'
                if (not os.path.exists(filePath)):
                    os.makedirs(filePath)
            task = threading.Thread(
                target=request, args=(fileName, filePath, service))
            task.start()
            task.join()
        if operation == 'L' or operation == 'l':
            task = threading.Thread(target=lookup)
            task.start()
            task.join()
        operation = input(
            "Enter \n\
             (R)equest to request a file,\n\
             (L)ook to request the contents in the server,\n\
             (E)xit to exit the client\n")


if __name__ == '__main__':
    client()
