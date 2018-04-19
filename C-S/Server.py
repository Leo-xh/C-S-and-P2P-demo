import sys
import os
import socket
import struct
import threading
import time
from Crypto.Cipher import AES
# -*- coding=utf-8 -*-



# serverIp = '172.18.35.225'
serverIp = '192.168.199.218'
# Leo's laptop in dormitory

secretary_key = "project-C/S and P2P protocol key"
# serverIp = '127.0.0.1'

serverPort = 6789
messageSize = 1036
requestSize = 208
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((serverIp, serverPort))
serverSocket.listen(10)
Encryptor = AES.new(secretary_key)
pad = b'\x00'
requestList = []
lineNum = 0
nowLine = 0
lock = threading.Lock()


class UnExist(Exception):
    def __init__(self, arg="File does not exist, the connection is closed"):
        super(UnExist, self).__init__(arg)


def myPrint(printStr, num=1):
    global lineNum
    lineNum += num
    print(printStr)


def service():
    global lineNum
    print("listening")
    while True:
        newsock, addrAndPort = serverSocket.accept()
        lock.acquire()
        if len(requestList) != 0:
            myPrint("\n\n\nRequest accepted", 3)
        else:
            myPrint("\nRequest accepted", 2)
        task = threading.Thread(
            target=dealRequest, args=(newsock, addrAndPort))
        task.start()


def dealRequest(sock, addrAndPort):
    # resourPath = 'D:\Resources'
    resourPath = 'Resources'
    global Encryptor
    global lineNum, nowLine, requestList
    printLine = 0

    myPrint("Tackleing a request from " + str(addrAndPort))
    request = sock.recv(requestSize)
    reqPro, reqSer, reqVer, reqId, filename = struct.unpack('!4H200s', request)
    # print(reqSer)
    originreqSer = reqSer
    if reqSer != 2:
        filename = filename.decode().split('\00')[0]
        myPrint("Sending file " + filename)
        if reqSer == 1:
            myPrint("Encrypted")
    elif reqSer == 2:
        with open(os.path.join(resourPath, "catalogueFile.txt"), "w") \
                as catalogueFile:
            catalogueFile.write(requestCatalogue())
        filename = "catalogueFile.txt"
    nowLine = lineNum
    lock.release()
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
                    lock.acquire()
                    dataBody = sendFile.read(messageSize - 12)
                    if not dataBody:
                        packet = struct.pack('!6H', reqPro, reqSer, reqVer,
                                             reqId, 12, errorCode)
                        sock.sendall(packet)
                        if reqSer != 2:
                            print("\nThe file is sent")
                            nowLine += 1
                        lock.release()
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
                        sock.sendall(packet)
                        Sendsize += len(dataBody)
                        reqSer = originreqSer
                        if reqSer != 2:
                            if str(addrAndPort) not in requestList:
                                printLine = lineNum
                                lineNum += 1
                                requestList.append(str(addrAndPort))
                            if printLine == nowLine:
                                print(
                                    "\rSend %f%%" %
                                    ((Sendsize / FileSize) * 100),
                                    end='')
                            elif printLine < nowLine:
                                print(
                                    '\x1b[%dA' %
                                    (nowLine - printLine) + "\rSend %f%%" %
                                    ((Sendsize / FileSize) * 100),
                                    end='')
                            else:
                                print(
                                    '\x1b[%dB' %
                                    (printLine - nowLine) + "\rSend %f%%" %
                                    ((Sendsize / FileSize) * 100),
                                    end='')
                            nowLine = printLine
                    lock.release()
                    # sys.stdout.write("\rSend %f%%" %
                    #                ((Sendsize / FileSize) * 100))
                    # sys.stdout.flush()

        else:
            errorCode = 1
            packet = struct.pack('!6H', reqPro, reqSer, reqVer, reqId, 12,
                                 errorCode)
            sock.sendall(packet)
            raise UnExist()
    except UnExist as e:
        myPrint(e.args)
    except Exception as e:
        myPrint(e.args)
        # print(packet)
        raise e
    finally:
        sock.close()
        if str(addrAndPort) in requestList:
            requestList.remove(str(addrAndPort))
        if len(requestList) == 0:
            print('\x1b[%dB' % (lineNum - nowLine) + '', end='')


def requestCatalogue(sourcePath='Resources', dirpath='.'):
    fileList = ""
    dirpathFather, catalogueName, fileNames = next(os.walk(sourcePath))
    fileNames.sort()
    catalogueName.sort()
    for i in fileNames:
        if i != "catalogueFile.txt":
            fileList += (os.path.join(dirpath, i) + "\n")
    for i in catalogueName:
        fileList += requestCatalogue(
            os.path.join(sourcePath, i), os.path.join(dirpath, i))
    return fileList


if __name__ == '__main__':
    service()
