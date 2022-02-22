# import socket module
from socket import *
# In order to terminate the program
import sys

#use to run
#python solution.py
#http://127.0.0.1:13331/helloworld.html


def webServer(port=13331):
  serverSocket = socket(AF_INET, SOCK_STREAM)
  #Prepare a server socket
  serverSocket.bind(("", port))
  #Fill in start ???
  serverSocket.listen(1)
  while True:
    #Establish the connection
    # print('Ready to serve...')
    connectionSocket, addr =  serverSocket.accept()
    try:

      try:
        message = connectionSocket.recv(1024).decode()
        filename = message.split()[1]
        f = open(filename[1:])        
        outputdata =  f.read()
     
        #Send one HTTP header line into socket.
        #Fill in start
        connectionSocket.send('HTTP/1.0 200 OK\nContent-Type: text/html\n\n'.encode())
        #Fill in end

        #Send the content of the requested file to the client
        for i in range(0, len(outputdata)):
          connectionSocket.send(outputdata[i].encode())
        connectionSocket.send("\r\n".encode())
        connectionSocket.close()
      except IOError:
        pass
        # Send response message for file not found (404)
        #Fill in start
        return_message = 'HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n'
        return_message += '<html><body><p>Error 404: File not found.</p></body></html>'
        connectionSocket.send(return_message.encode())
        #Fill in end
        #Close client socket
        #Fill in start
        connectionSocket.close()
        #Fill in end

    except (ConnectionResetError, BrokenPipeError):
      pass
    
  serverSocket.close()
  sys.exit()  # Terminate the program after sending the corresponding data

if __name__ == "__main__":
  webServer(13331)