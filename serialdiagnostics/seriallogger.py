from fakeport import FakePort
from reader import Reader
from argparse import ArgumentParser
from serial import Serial
from colorama import init, Fore
from time import time
import sys
from Queue import Queue, Empty

init()

start_time = time()
lineq = Queue()

def parse_args():
    parser = ArgumentParser(description='Log recieved characters from two serial ports')
    parser.add_argument('port1', type=str,
            help='The path to serial port #1')
    parser.add_argument('port2', type=str,
            help='The path to serial port #2')
    parser.add_argument('--baud1', type=int, default=115200,
            help='The baud rate of serial port #1')
    parser.add_argument('--baud2', type=int, default=115200,
            help='The baud rate of serial port #2')
    return parser.parse_args()

def port1_lineCB(line):
    lineq.put((time() - start_time, 1, line), False, 10.0)

def port2_lineCB(line):
    lineq.put((time() - start_time, 2, line), False, 10.0)

def print_line(timestamp, port, line):
    if port == 1:
        print "[%9.3f]: %s" % (timestamp, Fore.GREEN + line + Fore.RESET)
    else:
        print "[%9.3f]: %s" % (timestamp, Fore.BLUE + line + Fore.RESET)

def main():
    args = parse_args()
    if args.port1 == 'fake':
        port1 = FakePort(charrange=('0', 'z'), timeout=0)
    else:
        port1 = Serial(args.port1, args.baud1, timeout=0)
    if args.port2 == 'fake':
        port2 = FakePort(charrange=('0', 'z'), timeout=0)
    else:
        port2 = Serial(args.port2, args.baud2, timeout=0)
    read1 = Reader(port1)
    read2 = Reader(port2)
    read1.setLineCB(port1_lineCB)
    read2.setLineCB(port2_lineCB)

    try:
        while(True):
            try:
                msg = lineq.get(False, 1.0)
            except Empty:
                continue
            print_line(*msg)
    except:
        print "Exception raised, Quitting"
        raise
    finally:
        port1.close()
        port2.close()
        read1.close()
        read2.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
