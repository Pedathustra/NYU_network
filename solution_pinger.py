from socket import *
import socket as sock
import os
import sys
import struct
import time
import select
import binascii
import statistics
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


def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    time_sent = time.time() # it's the same here as if created in sendOnePing. Leaving it here so I don't have to adjust function signatures
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)
        # Fill in start
 
        recp_icmp_type, recp_icmp_code, recp_icmp_checksum, recp_icmp_id, recp_icmp_seqno = struct.unpack("! b b H H h", recPacket[20:28]) #(1)(1)(2)(2)(2)
        # sent_icmp_type, sent_icmp_code, sent_icmp_checksum, sent_icmp_id, sent_icmp_seqno = struct.unpack("! b b H H h", recPacket[20:28]) #(1)(1)(2)(2)(2)
        recp_be_icmp_id = sock.ntohs(recp_icmp_id)

        #todo: add seqno
        if ID == recp_icmp_id or ID == recp_be_icmp_id:  # not full proof. Still a remote chance this could have a false positive. 
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
    return 

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
    # timeout=1 means: If one second goes by without a reply from the server,  	
    # # the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")
    # Calculate vars values and return them
    #  vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)),str(round(stdev(stdev_var), 2))]
    # Send ping requests to a server separated by approximately one second
    delay_values = []
    packet_min = 0
    packet_max = 0
    packet_sum = 0
    top_range = 4
    for i in range(0,top_range):
        delay = doOnePing(dest, timeout)
        if delay > packet_max:
            packet_max = delay
        if delay < packet_min or packet_min == 0:
            packet_min = delay
        packet_sum += delay
        delay_values.append(delay)
        time.sleep(1)  # one second
    packet_avg = packet_sum / top_range
    packet_std_dev = statistics.stdev(delay_values)
    # vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)),str(round(packet_std_dev, 2))]
    vars = [str(packet_min), str(packet_avg), str(packet_max),str(packet_std_dev)]
    return vars

if __name__ == '__main__':
    resp = ping("google.co.il")
    print(resp[0])
    print(resp[1])
    print(resp[2])
    print(resp[3])
    
    