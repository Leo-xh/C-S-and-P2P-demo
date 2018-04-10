import sys
import os
import socket
import struct
import threading
import time
from Crypto.Cipher import AES
# -*- coding=utf-8 -*-

secretary_key = "project-C/S and P2P protocol key"
serverIp = '127.0.0.1'
serverPort = 6789
messageSize = 1036
requestSize = 208
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((serverIp, serverPort))
serverSocket.listen(10)
Encryptor = AES.new(secretary_key)
pad = b'0'


class UnExist(Exception):
    def __init__(self, arg="File does not exist, the connection is closed"):
        super(UnExist, self).__init__(arg)


def service():
    print("listening")
    while True:
        newsock, addrAndPort = serverSocket.accept()
        print("Request accepted")
        task = threading.Thread(
            target=dealRequest, args=(newsock, addrAndPort))
        task.start()


def dealRequest(sock, addrAndPort):
    # resourPath = 'D:\Resources'
    resourPath = 'Resources'
    global Encryptor

    print("Tackleing a request from %s" % str(addrAndPort))
    request = sock.recv(requestSize)
    reqPro, reqSer, reqVer, reqId, filename = struct.unpack('!4H200s', request)
    if reqSe == 1:
        filename = filename.decode().split('\00')[0]
        print("Sending file %s" % filename)
    elif reqSer == 2:
        with open("catalogueFile.txt", "w") as catalogueFile:
            catalogueFile.write(requestCatalogue())
        filename = "catalogueFile.txt"
    try:
        if os.path.exists(os.path.join(resourPath, filename)):
            errorCode = 0
            FileSize = os.path.getsize(os.path.join(resourPath, filename))
            filereq = os.path.join(resourPath, filename)
            Sendsize = 0
            if reqSer == 1:
                FileSize += 16 - FileSize % 16
            with open(os.path.join(resourPath, filename), 'rb') as sendFile:
                while True:
                    dataBody = sendFile.read(messageSize - 12)
                    if not dataBody:
                        packet = struct.pack('!6H', reqPro, reqSer, reqVer,
                                             reqId, 12, errorCode)
                        sock.sendall(packet)
                        if reqSer == 1:
                            print("\nThe file is sent")
                        break
                    else:
                        if reqSer == 1:
                            appended = (16 - (len(dataBody) % 16)) * pad
                            validLen = len(dataBody)
                            reqSer = validLen
                            dataBody += appended
                            dataBody = Encryptor.encrypt(dataBody)
                        packet = struct.pack(
                            '!6H%ds' % len(dataBody), reqPro, reqSer, reqVer,
                            reqId, 12 + len(dataBody), errorCode, dataBody)
                        # print(dataBody)
                        sock.sendall(packet)
                        Sendsize += len(dataBody)
                        if reqSer == 1:
                            sys.stdout.write("\rSend %f%%" %
                                             ((Sendsize / FileSize) * 100))
                            sys.stdout.flush()

        else:
            errorCode = 1
            packet = struct.pack('!6H', reqPro, reqSer, reqVer, reqId, 12,
                                 errorCode)
            sock.sendall(packet)
            raise UnExist()
    except UnExist as e:
        print(e.args)
    except Exception as e:
        print(e.args)
        print(packet)
        raise e
    finally:
        sock.close()


def requestCatalogue(sourcePath='Resources', dirpath='.'):
    fileList = ""
    dirpathFather, catalogueName, fileNames = next(os.walk(sourcePath))
    for i in fileNames:
        fileList += (os.path.join(dirpath, i) + "\n")
    for i in catalogueName:
        fileList += requestCatalogue(
            os.path.join(sourcePath, i), os.path.join(dirpath, i))
    return fileList


if __name__ == '__main__':
    service()