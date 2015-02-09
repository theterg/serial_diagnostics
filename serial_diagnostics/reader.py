from threading import Thread
from time import sleep, time
from atexit import register
from util import get_datestr
import sys


class Reader(Thread):
    def __init__(self, port, terminator='\r\n', charlog=False):
        super(Reader, self).__init__()
        self.running = True
        self.daemon = True
        self.terminator = terminator
        self.port = port
        self.chars = []
        self.times = []
        self.charCB = None
        self.lineCB = None
        if charlog:
            self.charlog = open(get_datestr(port.name.split('/')[-1]+'.csv'), 'w')
            self.charlog.write("time,char\r\n")
        else:
            self.charlog = None
        self.starttime = time()
        register(self.__del__)
        self.start()

    def __del__(self):
        self.close()

    def run(self):
        line = []
        while(self.running):
            char = self.port.read(1)
            if len(char) != 1:
                continue
            if self.charlog is not None:
                self.charlog.write("%.6f,%02x\r\n" %(time() - self.starttime, ord(char)))
                self.charlog.flush()
            line.append(char)
            if self.charCB is not None:
                self.charCB(char)
            if self.lineCB is not None and self.terminator in line:
                self.lineCB(''.join(line))
                line = []

    def close(self):
        self.running = False
        self.join()
        if self.charlog is not None:
            self.charlog.close()

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
