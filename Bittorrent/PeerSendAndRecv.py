import struct
import bencode


def send(msg_type, piece, pieceData=b''):
    ''' If the piece is the last piece of the metadata, it may be less than 16kiB. '''
    ''' If it is not the last piece of the metadata, it MUST be 16kiB. '''
    packet = bencode.bencode("msg_type") + bencode.bencode(msg_type)
    packet += bencode.bencode("piece") + bencode.bencode(piece)
    if msg_type == 1:  # data
        packet += bencode.bencode("total_size") + bencode.bencode(
            len(pieceData))
        packet = struct.pack("!%ds" % len(packet), packet.encode())
        packet += pieceData
    else:
        packet = struct.pack("!%ds" % len(packet), packet.encode())
    return packet
    # self.transport.write(packet)


recvBuff = b''
recvMsgSize = -1
recvPiece = -1
recvTotalSize = -1


def recv(recvData):
    global recvBuff, recvMsgSize, recvPiece, recvTotalSize
    recvBuff += recvData
    if recvMsgSize == -1:
        if len(recvBuff) < 11 or recvBuff[10:].decode().index('e') == -1:
            return
        else:
            recvBuff = recvBuff[10:]
            index = recvBuff.decode().index('e') + 1
            recvMsgSize = bencode.bdecode(recvBuff.decode()[0:index])
            recvBuff = recvBuff[index:]
    if recvMsgSize != -1 and recvPiece == -1:
        if len(recvBuff) < 8 or recvBuff[7:].decode().index('e') == -1:
            return
        else:
            recvBuff = recvBuff[7:]
            index = recvBuff.decode().index('e') + 1
            recvPiece = bencode.bdecode(recvBuff.decode()[0:index])
            recvBuff = recvBuff[index:]
    if recvMsgSize != -1 and recvPiece != -1:
        print(recvMsgSize)
        print(recvPiece)
        if recvMsgSize == 1:  # data
            if recvTotalSize == -1:
                if len(recvBuff) < 14 or recvBuff[13:].decode().index(
                        'e') == -1:
                    return
                else:
                    recvBuff = recvBuff[13:]
                    index = recvBuff.decode().index('e') + 1
                    recvTotalSize = bencode.bdecode(recvBuff.decode()[0:index])
                    recvBuff = recvBuff[index:]
            if recvTotalSize != -1:
                if len(recvBuff) < recvTotalSize:
                    return
                else:
                    revePieceData = recvBuff[0:recvTotalSize]
                    recvMsgSize = recvPiece = recvTotalSize = -1
                    return revePieceData
        else:
            recvMsgSize = recvPiece = -1
            return b''


recvData = send(1, 1314142, b'10001000fwadwafwafawgwad')
print(recv(recvData))
