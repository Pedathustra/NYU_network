from socket import *
# from decouple import config
# import os 
import ssl 
import base64
#  https://www.dev2qa.com/python-built-in-local-smtp-server-example/
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
    # is_local = True if mailserver == '127.0.0.1' else False

    # context_instance = ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)
    # username = base64.b64encode(config('EMAIL_FROM').encode('utf-8')) + endline.encode()
    # password = base64.b64encode(config('EMAIL_FROM_PASSWORD').encode('utf-8')) + endline.encode()
    # mail_to = (os.getenv('EMAIL_TO') or 'bogus@yahoo.com')
    mail_to = 'bogus@gmail.com'
    username = 'bogus@gmail.com'
    # print(mail_to)
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((mailserver, port))
    recv = client_socket.recv(1024).decode()

    send_command(client_socket, f'HELO Alice{endline}'.encode(), print_results)
    send_command(client_socket, f'STARTTLS{endline}'.encode(), print_results)   
    
    # ssl_context = context_instance.wrap_socket(client_socket)
    # context = client_socket if is_local else ssl_context 
    context = client_socket

    # if not is_local:
    #     send_command(ssl_context, f'AUTH LOGIN{endline}'.encode(), print_results)   
    #     send_command(ssl_context, username, print_results)   
    #     send_command(ssl_context, password, print_results)   
    #use <> for gmail
    send_command(context, f'MAIL FROM: {username}{endline}'.encode(), print_results)   
    send_command(context, f'RCPT TO: {mail_to}{endline}'.encode(), print_results)
    send_command(context, f'DATA{endline}'.encode(), print_results)  
    send_command(context, f'{msg}{endmsg}'.encode(), print_results) 
    # send_command(context, f'.{endline}'.encode(), print_results) 
    send_command(context, f'QUIT{endline}'.encode(), print_results) 
    
if __name__ == '__main__':
    smtp_client(1025, '127.0.0.1')
    # smtp_client(587, 'smtp.gmail.com')