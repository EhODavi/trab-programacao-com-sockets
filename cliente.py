import socket
import threading


def escuta():
    while True:
        msg, serv = udp.recvfrom(1024)
        msg = msg.decode()

        if msg == 'BYE':
            break

        msg_list = msg.split(':')

        if msg_list[0] == 'INFO':
            print(msg[5::])
        elif msg_list[0] == 'MSG':
            print(f"{msg_list[1]} disse: {msg_list[2]}")
        else:
            print(msg)


HOST = '127.0.1.1'
PORT = 20000

nome_usuario = input("Nome de usuário: ")

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

dest = (HOST, PORT)

msg = "USER:" + nome_usuario
udp.sendto(msg.encode(), dest)

t = threading.Thread(target=escuta)
t.start()

msg = input()

while True:
    if msg == '/bye':
        msg = 'BYE'
        udp.sendto(msg.encode(), dest)

        break
    elif msg == '/list':
        msg = 'LIST'
        udp.sendto(msg.encode(), dest)
    elif msg[0:5] == '/file':
        nome_arquivo = msg[6::]

        arquivo = open(nome_arquivo, "r+b")

        conteudo_arquivo = arquivo.read()

        tcp.connect(dest)

        msg = 'FILE:' + nome_arquivo + '\n' + str(conteudo_arquivo)
        tcp.send(msg.encode())

        tcp.close()
        arquivo.close()
    elif msg[0:4] == '/get':
        nome_arquivo = msg[5::]

        tcp.connect(dest)

        msg = 'GET:' + nome_arquivo
        tcp.send(msg.encode())

        conteudo_arquivo = tcp.recv(1024).decode()

        tcp.close()
    else:
        msg = 'MSG:' + msg
        udp.sendto(msg.encode(), dest)

    msg = input()

t.join()
udp.close()
