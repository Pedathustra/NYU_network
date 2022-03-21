from socket import *
import os
import sys
import struct
import time
import select
import binascii
# Should use stdev

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0

def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def format_ip(ip_in_bytes):
    return '.'.join(map(str, ip_in_bytes))
def print_name_value(item_name, item_value):
    print(f'{item_name}: {item_value}\n\r')

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)
    # Fill in start
    #     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #   0 |Version|  IHL  |Type of Service|          Total Length         |
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #   4 |         Identification        |Flags|      Fragment Offset    |
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #   8 |  Time to Live |    Protocol   |         Header Checksum       |
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #   12|                       Source Address                          |
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #   16 |                    Destination Address                        |
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #   20 |                    Options                    |    Padding    |
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # https://docs.python.org/3/library/struct.html
    # https://gist.github.com/pklaus/856268/b7194182270c816dee69438b54e42116ab31e53b
        
        # ah ha! Example that works with src, and destination ips
        # source_ip, dest_ip = struct.unpack("! 4s 4s", recPacket[12:20])
        # print(format_ip(source_ip), format_ip(dest_ip))

        # Fetch the ICMP header from the IP packet: 
        # best description
        # https://book.huihoo.com/iptables-tutorial/x1078.htm
        # https://stackoverflow.com/questions/27094637/icmp-pinger-application-in-python-error-operation-not-permitted
        # checksum, sequence number, time to live (TTL), etc
        # https://pythontic.com/modules/socket/byteordering-coversion-functions
        # do i need to know which one and convert? based on os? 
        # Type (1) | Code (1)| Checksum (2) || identifier (2 ) | seqno ( 2  )
        #icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seqno = struct.unpack("! b b H H H", recPacket[20:28]) #(1)(1)(2)(2)(2) #?
        icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seqno = struct.unpack("! b b H H h", recPacket[20:28]) #(1)(1)(2)(2)(2)
      
        print("-------------")
        print_name_value("icmp_type: ", icmp_type)
        print_name_value("icmp_code: ", icmp_code)
        print_name_value("icmp_checksum: ", icmp_checksum)
        print_name_value("icmp_id (seems to be BE): ", icmp_id)
        print_name_value("Orig ID (Seems to be LE): ", ID)
        print_name_value("icmp_seqno: ", icmp_seqno)

        if ID == icmp_id:
            return timeReceived - time_sent
        # Fill in end
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header

    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

 
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
 
    mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str


    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")
    
    # SOCK_RAW is a powerful socket type. For more details:   http://sockraw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)


    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    # print(mySocket, destAddr, delay, myID)
    
    return delay


def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,  	# the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")
    # Calculate vars values and return them
    #  vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)),str(round(stdev(stdev_var), 2))]
    # Send ping requests to a server separated by approximately one second
    for i in range(0,4):
        delay = doOnePing(dest, timeout)
        print(delay)
        time.sleep(1)  # one second

    return vars

if __name__ == '__main__':
    #ping("google.co.il")
    ping("www.google.com")
    #ping("127.0.0.1")