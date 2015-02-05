from serial import FileLike
from Queue import Queue, Empty
from threading import Thread, enumerate
from time import sleep, time
from random import randint
from atexit import register


class FakePort(Thread, FileLike):
    '''
    Simulates a fake serial port

    Will emit random characters, line terminated
    Implements pyserial.FileLike, so should be somewhat useable as a replacement
    for a normal pyserial serial port.
    '''
    def __init__(self, port=0, baud=0, timeout=None, rate=10.0, linelength=40, terminator="\r\n"):
        super(FakePort, self).__init__()
        self.timeout = timeout
        if self.timeout is None:
            self.block = True
        else:
            self.block = False
        self.daemon = True
        self.q = Queue()
        self.running = True
        self.rate = rate
        self.linelength = linelength
        self.terminator = terminator
        register(self.__del__)
        self.start()

    def __del__(self):
        # Ensure the thread is closed savely upon delete
        self.close()

    def run(self):
        # Overriding Thread.run()
        # Thread is responsible for generating random characters
        while(self.running):
            sleep(1.0/self.rate)
            self.q.put(chr(randint(0, 255)), False, 1.0)
            if randint(1, self.linelength) == 1:
                for char in self.terminator:
                    self.q.put(char)

    def read(self, size=1):
        ''' Read size bytes from the serial port.

        If a timeout is set it may return less characters as requested.
        With no timeout it will block until the requested number of bytes is read.
        '''
        if size == 1:
            try:
                return self.q.get(self.block, self.timeout)
            except Empty:
                return ''
        else:
            line = []
            while(len(line) < size):
                try:
                    line.append(self.q.get(self.block, self.timeout))
                except Empty:
                    break
            return ''.join(line)


    def write(self, data):
        ''' Write the string data to the port.

        NOTE - This does nothing, always returns the length of the input string'''
        return len(data)

    def flush(self):
        ''' Flush input buffer, discarding all it’s contents.
        '''
        while not self.q.empty():
            self.q.get(True)

    def close(self):
        ''' Close port immediately

        will block until the random character generator thread has closed.'''
        self.running = False
        self.flush()
        self.join()

