##file = open("test.txt",'wb')
##file.seek(1024*1024)
##file.write(b'\x00')
##file.close()

file = open("bitfield", 'wb')
#for i in range(0,64,2):
#    file.seek(16384*i, 0)
file.write(b'\xff'*17995)
file.close()
    