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
# serverIp = '127.0.0.1'
serverIp = '192.168.199.122'
# Leo's laptop in dormitory

serverPort = 6789
IDs = []
messageSize = 2060  # head plus databody


def request(fileName, filePath):
    reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reqSocket.connect((serverIp, serverPort))
    print("Requesting %s" % fileName)
    idExp = 0
    while True:
        if idExp not in IDs:
            break
    IDs.append(idExp)
    protocol = 0
    service = 0
    version = 1
    packet = struct.pack('!4H200s', protocol, service,
                         version, idExp, fileName.encode())
    reqSocket.send(packet)
    pre = b''
    try:
        with open(os.path.join(filePath, fileName), 'wb') as file:
            while True:
                more = pre + reqSocket.recv(messageSize)
                if more:
                    header = struct.unpack('!6H', more[:12])
                    recvErrorCode = header[5]
                    recvLen = header[4]
                    idRecv = header[3]
                    if recvErrorCode == 1:
                        print("File does not exist, please check the input")
                        break
                    if recvLen == 12:
                        print("File Received, sized %dB, ID %d, saved as %s" %
                              (os.path.getsize(os.path.join(filePath, fileName)),
                               idExp, os.path.join(filePath, fileName)))
                        IDs.remove(idExp)
                        break
                    if len(more) < recvLen:
                        more += reqSocket.recv(recvLen - len(more))
                    if len(more) > recvLen:
                        pre = more[recvLen:]
                        more = more[:recvLen]
                    recvData = struct.unpack(
                        '!%ds' % (recvLen - 12), more[12:])
                    file.write(recvData[0])
    except Exception as e:
        print(e.args)
        os.remove(os.path.join(filePath, fileName))
        raise e
        # print(more)


def client():
    operation = input(
        "Enter (R)equest to request a file, (E)xit to exit the client\n")
    while operation != 'E' or operation != 'e':
        fileName = input("Please enter the name of the file:")
        filePath = input("Please enter the path of the file:")
        if(filePath == ''):
            filePath = 'D:\downloads'
            if(not os.path.exists(filePath)):
                os.makedirs(filePath)
        task = threading.Thread(target=request, args=(fileName, filePath))
        task.start()
        operation = input(
            "Enter (R)equest to request a file, (E)xit to exit the client\n")

if __name__ == '__main__':
    client()
