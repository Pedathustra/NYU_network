from socket import *
import os
import sys
import struct
import time
import select
import binascii
import ipaddress
import math
ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise

def checksum(string):
# In this function we make the checksum of our packet
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

def build_packet():

    myChecksum = 0
    my_id = os.getpid() & 0xFFFF
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, my_id, 1)
    data = struct.pack("d", time.time())
    myChecksum = checksum(header + data)    
    
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, my_id, 1)
    packet = header + data
    return packet 

def get_route(hostname):
    timeLeft = TIMEOUT
    tracelist1 = [] #This is your list to use when iterating through each trace 
    tracelist2 = [] #This is your list to contain all traces
    a = 1
    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)
            icmp = getprotobyname("icmp")
            mySocket = socket(AF_INET, SOCK_RAW, icmp)
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    tracelist1.append("* * * Request timed out.")
                    tracelist2.append(tracelist1)
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    tracelist1.append("* * * Request timed out.")
                    tracelist2.append(tracelist1) #You should add the list above to your all traces list                    
            except timeout:
                continue
                
            else:
                #Fill in start
                # https://docs.python.org/3/library/ipaddress.html
                # https://docs.python.org/3/library/struct.html
                hop_hostname = ''
                types, recp_icmp_code, recp_icmp_checksum, recp_icmp_id, recp_icmp_seqno = struct.unpack("! b b H H h", recvPacket[20:28]) #(1)(1)(2)(2)(2)
                recp_ttl, recp_protocol, recp_ip_checksum, recp_src, rec_dest = struct.unpack("! B B H 4s 4s", recvPacket[8:20]) 
                hop_source_ip = str(ipaddress.IPv4Address(recp_src))
                tracelist1.append(str(ttl))
                try:
                    (hop_hostname, ar, hop_ip) = gethostbyaddr(hop_source_ip)
                except herror:
                    hop_hostname = 'hostname not returnable'
                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0] 
                    time_elapsed = math.ceil((timeReceived-t) * 1000)
                    tracelist1.extend([f'{time_elapsed}ms', hop_source_ip, hop_hostname])
                elif types == 3: # Destination Unreachable.
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    time_elapsed = math.ceil((timeReceived-t) * 1000)
                    tracelist1.extend([f'{time_elapsed}ms', hop_source_ip, hop_hostname])
                    # tracelist1.append('Destination Unreachable')
                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    time_elapsed = math.ceil((timeReceived-timeSent) * 1000)
                    tracelist1.extend([f'{time_elapsed}ms', hop_source_ip, hop_hostname])
                    if (hop_source_ip == destAddr):
                        return tracelist2
                else:
                    #Fill in start
                    tracelist1.append('ICMP Error ')
                    #If there is an exception/error to your if statements, you should append that to your list here
                    #Fill in end
                break
            finally:
                tracelist2.append(tracelist1)
                tracelist1 = []
                mySocket.close()
    return tracelist2
if __name__ == '__main__':
    print(get_route("google.co.il"))
    #print(get_route("yahoo.com"))
    
    