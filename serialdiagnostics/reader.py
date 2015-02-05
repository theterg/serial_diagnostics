from threading import Thread
from time import sleep, time
from atexit import register


class Reader(Thread):
    def __init__(self, port, terminator='\r\n'):
        super(Reader, self).__init__()
        self.running = True
        self.daemon = True
        self.terminator = terminator
        self.port = port
        self.chars = []
        self.times = []
        self.charCB = None
        self.lineCB = None
        self.starttime = time()
        register(self.__del__)
        self.start()

    def __del__(self):
        self.close()

    def run(self):
        line = []
        while(self.running):
            char = self.port.read(1)
            if len(char) == 0:
                continue
            self.chars.append(char)
            line.append(char)
            self.times.append(time() - self.starttime)
            if self.charCB is not None:
                self.charCB(char)
            if self.lineCB is not None and \
                    line[(-1)*len(self.terminator):] == list(self.terminator):
                self.lineCB(''.join(line[:(-1)*len(self.terminator)]))
                line = []

    def close(self):
        self.running = False
        self.join()

    def getChars(self):
        return self.chars

    def getTimes(self):
        return self.times

    def setCharCB(self, func):
        if hasattr(func, '__call__') or func is None:
            self.charCB = func
        else:
            raise TypeError('func must be callable')

    def setLineCB(self, func):
        if hasattr(func, '__call__') or func is None:
            self.lineCB = func
        else:
            raise TypeError('func must be callable')
