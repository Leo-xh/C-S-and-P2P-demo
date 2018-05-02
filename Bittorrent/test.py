#file = open("test.txt",'wb')
#file.seek(1024*1024)
#file.write(b'\x00')
#file.close()

file = open("test.txt", 'rb+')
for i in range(0,64,2):
    file.seek(16384*i, 0)
    file.write(b'\x11'*16384)
file.close()