from socket import *
from decouple import config
import ssl 
import base64
def smtp_client(port=1025, mailserver='127.0.0.1'):
    msg = "\r\n My message"
    endmsg = "\r\n.\r\n"
    endline = '\r\n'

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((mailserver, port))

    recv = client_socket.recv(1024).decode()

    helo_command = f'HELO Alice{endline}'
    client_socket.send(helo_command.encode())
    recv1 = client_socket.recv(1024).decode()

    #send auth info
    message = f'STARTTLS{endline}'
    client_socket.send(message.encode())
    auth_recv = client_socket.recv(1024).decode()

    context_instance = ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)

    ssl_context = context_instance.wrap_socket(client_socket)

    from_address = config('EMAIL_FROM')
    password = config('EMAIL_FROM_PASSWORD')
        
    from_address_b64 = base64.b64encode(from_address.encode('utf-8')) + endline.encode()
    password_b64 = base64.b64encode(password.encode('utf-8')) + endline.encode()
    ssl_context.send(f'AUTH LOGIN{endline}'.encode())
    auth_recv = ssl_context.recv(1024)
    print('auth request', auth_recv)

    ssl_context.send(from_address_b64)
    auth_recv = ssl_context.recv(1024).decode()
    print(f'un: {auth_recv}')
    
    ssl_context.send(password_b64)
    auth_recv = ssl_context.recv(1024).decode()
    print('un', auth_recv)

    # Send MAIL FROM command and handle server response.
    # see above
    #TODO remove <> from MAIL FROM
    mail_from = f'MAIL FROM: <{from_address}>{endline}'.encode()
        
    ssl_context.send(mail_from)
    mail_from_recv = ssl_context.recv(1024).decode()
    print('mail_from_recv', mail_from_recv)

    
    # Send RCPT TO command and handle server response.
    mail_to = config('EMAIL_TO')
    rcpt_to = f'RCPT TO: <{mail_to}>{endline}'.encode()
        
    ssl_context.send(rcpt_to)
    mail_to_recv = ssl_context.recv(1024).decode()
    print('mail_to_recv', mail_to_recv)

    # ..\Networking\github\NYU_network\solution.py
    # Send DATA command and handle server response.
    ssl_context.send(f'DATA{endline}'.encode())
    send_data_recv = ssl_context.recv(1024).decode()
    print('send_data_recv', send_data_recv)
 
    # Send message data.
    ssl_context.send(f'{msg}{endmsg}'.encode())
    send_msg_data_recv = ssl_context.recv(1024).decode()
    print('send_data_recv', send_msg_data_recv)
    
    # Message ends with a single period, send message end and handle server response.
    ssl_context.send(f'.{endline}'.encode())
    send_recv = ssl_context.recv(1024).decode()
    print('send_recv', send_data_recv)


    quit = f'QUIT{endline}'
    ssl_context.send(quit.encode())
    quit_rcv = ssl_context.recv(1024).decode()
    print('done')

if __name__ == '__main__':
    # smtp_client(1025, '127.0.0.1')
    smtp_client(587, 'smtp.gmail.com')