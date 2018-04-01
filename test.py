from socket import *

testSocket = socket(AF_INET, SOCK_STREAM)
testSocket.bind(('', 60000))
testSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
testSocket.listen(1)
print("listening")
