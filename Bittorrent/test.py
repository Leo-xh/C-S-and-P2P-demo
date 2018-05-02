#file = open("test.txt",'wb')
#file.seek(1024*1024)
#file.write(b'\x00')
#file.close()

file = open("test.txt", 'rb+')
file.seek(1024, 0)
file.write(b'\x11'*1024)
file.close()