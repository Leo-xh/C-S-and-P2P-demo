class test(object):
    int1 = 1
    class b(object):
        pass
    def __printint(self):
        print(self.int1)
    def printint2(self):
        b()
        self.__printint()