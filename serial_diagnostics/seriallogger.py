from fakeport import FakePort
from reader import Reader
from argparse import ArgumentParser
from serial import Serial
from colorama import init, Fore
from time import time, sleep
import sys
from Queue import Queue, Empty
from util import get_datestr

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
    parser.add_argument('--savechars', action='store_true', default=False,
            help='Log each received character to CSV files')
    parser.add_argument('--savecsv', action='store_true', default=False,
            help='Log lines as CSV')
    parser.add_argument('--savetext', action='store_true', default=False,
            help='Log lines as text')
    return parser.parse_args()

def port1_lineCB(line):
    lineq.put((time() - start_time, 1, line), False, 10.0)

def port2_lineCB(line):
    lineq.put((time() - start_time, 2, line), False, 10.0)

def format_line(timestamp, port, line, color=False):
    if color:
        if port == 1:
            return "[%9.3f]: %s" % (timestamp, Fore.GREEN + line + Fore.RESET)
        else:
            return "[%9.3f]: %s" % (timestamp, Fore.BLUE + line + Fore.RESET)
    else:
        return "[%9.3f](%d): %s" % (timestamp, port, line)

def csv_header():
    return "time,port,line\r\n"

def format_csv(timestamp, port, line):
    hexline = []
    for char in line:
        hexline.append(hex(ord(char))[2:])
    return "%.3f,%d,%s\r\n" % (timestamp, port, ''.join(hexline))

def main():
    args = parse_args()

    # Open ports and readers
    if args.port1 == 'fake':
        port1 = FakePort(charrange=('0', 'z'), timeout=0)
    else:
        port1 = Serial(args.port1, args.baud1, timeout=0)
    read1 = Reader(port1, charlog=args.savechars)

    if args.port2 == 'fake':
        port2 = FakePort(charrange=('0', 'z'), timeout=0)
    else:
        port2 = Serial(args.port2, args.baud2, timeout=0)
    if args.port2 == args.port1:
        sleep(1.0)
    read2 = Reader(port2, charlog=args.savechars)

    # Open files if needed
    linelog = None
    if args.savecsv:
        linelog = open(get_datestr('lines.csv'), 'w')
        linelog.write(csv_header())
    elif args.savetext:
        linelog = open(get_datestr('lines.txt'), 'w')

    # Connect callbacks
    read1.setLineCB(port1_lineCB)
    read2.setLineCB(port2_lineCB)

    # Catch exceptions to ensure files are safely closed
    try:
        while(True):
            # Catch Empty - no bytes are ready to process
            try:
                msg = lineq.get(False, 1.0)
            except Empty:
                continue
            if args.savecsv:
                linelog.write(format_csv(*msg))
                linelog.flush()
            elif args.savetext:
                linelog.write(format_line(*msg)+'\r\n')
                linelog.flush()
            print format_line(*msg, color=True)
    except:
        print "Exception raised, Quitting"
        raise
    finally:
        port1.close()
        port2.close()
        read1.close()
        read2.close()
        if linelog is not None:
            linelog.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
