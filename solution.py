from socket import *

# https://www.dev2qa.com/python-built-in-local-smtp-server-example/
# python -m smtpd -c DebuggingServer -n 127.0.0.1:1025
# python ..\Networking\github\NYU_network\solution.py

def send_command(client, message, print_results=False):
    client.send(message)
    recv = client.recv(1024).decode()
    if (print_results):
        print(recv)     

def smtp_client(port=1025, mailserver='127.0.0.1'):
    msg = "\r\n My message"
    endmsg = "\r\n.\r\n"
    endline = '\r\n'
    print_results = False

    mail_to = 'bogus@gmail.com'
    username = 'bogus@gmail.com'

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((mailserver, port))
    recv = client_socket.recv(1024).decode()

    send_command(client_socket, f'HELO Alice{endline}'.encode(), print_results)
    send_command(client_socket, f'MAIL FROM: {username}{endline}'.encode(), print_results)   
    send_command(client_socket, f'RCPT TO: {mail_to}{endline}'.encode(), print_results)
    send_command(client_socket, f'DATA{endline}'.encode(), print_results)  
    send_command(client_socket, f'{msg}{endmsg}'.encode(), print_results) 
    # send_command(client_socket, f'{endmsg}'.encode(), print_results) 
    send_command(client_socket, f'QUIT{endline}'.encode(), print_results) 
    
if __name__ == '__main__':
    smtp_client(1025, '127.0.0.1')
 