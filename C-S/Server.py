import sys
import os
import socket
import struct
import threading
from Crypto.Cipher import AES
# -*- coding=utf-8 -*-


# serverIp = '127.0.0.1'
serverIp = '192.168.199.218'
# Leo's laptop in dormitory
serverPort = 6789
messageSize = 2060
requestSize = 208
delimiter = b'\xff\xff'
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((serverIp, serverPort))
serverSocket.listen(10)


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
    # test

    print("Tackleing a request from %s" % str(addrAndPort))
    request = sock.recv(requestSize)
    reqPro, reqSer, reqVer, reqId, filename = struct.unpack('!4H200s', request)
    filename = filename.decode().split('\00')[0]
    print("Sending file %s" % filename)
    try:
        if os.path.exists(os.path.join(resourPath, filename)):
            errorCode = 0
            with open(os.path.join(resourPath, filename), 'rb') as sendFile:
                while True:
                    dataBody = sendFile.read(2046)
                    if not dataBody:
                        packet = struct.pack(
                            '!6H', reqPro, reqSer, reqVer, reqId, 12, errorCode)
                        sock.sendall(packet)
                        print("The file is sent")
                        break
                    else:
                        packet = struct.pack('!6H%ds' % (len(
                            dataBody) + 2), reqPro, reqSer, reqVer, reqId, 12 + len(dataBody) + 2, errorCode, dataBody + delimiter)
                        # print("This packet is %dB" % len(packet))
                        sock.sendall(packet)
        else:
            errorCode = 1
            packet = struct.pack('!6H', reqPro, reqSer,
                                 reqVer, reqId, 12, errorCode)
            sock.sendall(packet)
            raise UnExist()
    except UnExist as e:
        print(e.args)
    except Exception as e:
        print(e.args)
        print(packet)
        # raise e
    finally:
        sock.close()

if __name__ == '__main__':
    service()
