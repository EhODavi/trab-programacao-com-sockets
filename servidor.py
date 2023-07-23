import socket
import threading

clientes_ativos = []
arquivos_recebidos = []


def escuta():
    while True:
        con, cliente = tcp.accept()

        msg = con.recv(1024).decode()

        if msg[0:4] == 'FILE':
            inicio_conteudo_arquivo = msg.find('\n')

            nome_arquivo = msg[5:inicio_conteudo_arquivo]

            inicio_conteudo_arquivo = inicio_conteudo_arquivo + 1

            conteudo_arquivo = msg[inicio_conteudo_arquivo::]

            arquivos_recebidos.append((nome_arquivo, conteudo_arquivo))

            msg_a_enviar = 'INFO:O arquivo ' + nome_arquivo + ' foi disponibilizado'

            for cliente_ativo in clientes_ativos:
                udp.sendto(msg_a_enviar.encode(), (cliente_ativo[1], cliente_ativo[2]))

        elif msg[0:3] == 'GET':
            nome_arquivo = msg[4::]
            conteudo_arquivo = ''

            for arquivo_recebido in arquivos_recebidos:
                if arquivo_recebido[0] == nome_arquivo:
                    conteudo_arquivo = arquivo_recebido[1]

                    break

            if conteudo_arquivo == '':
                conteudo_arquivo = 'NULL'

            con.send(conteudo_arquivo.encode())

        con.close()


print('Aguardando conexão')

HOST = ''
PORT = 20000

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

orig = (HOST, PORT)

udp.bind(orig)
tcp.bind(orig)

tcp.listen(1)

t = threading.Thread(target=escuta)
t.start()

while True:
    msg, cliente = udp.recvfrom(1024)

    msg = msg.decode()

    msg_list = msg.split(':')

    if msg_list[0] == 'USER':
        msg_a_enviar = 'INFO:' + msg_list[1] + ' entrou'

        for cliente_ativo in clientes_ativos:
            udp.sendto(msg_a_enviar.encode(), (cliente_ativo[1], cliente_ativo[2]))

        clientes_ativos.append((msg_list[1], cliente[0], cliente[1]))

    elif msg_list[0] == 'MSG':
        nome = ''

        for cliente_ativo in clientes_ativos:
            if cliente_ativo[2] == cliente[1]:
                nome = cliente_ativo[0]
                break

        msg_a_enviar = 'MSG:' + nome + ':' + msg[4::]

        for cliente_ativo in clientes_ativos:
            if cliente_ativo[0] != nome:
                udp.sendto(msg_a_enviar.encode(), (cliente_ativo[1], cliente_ativo[2]))

    elif msg_list[0] == 'LIST':
        msg_a_enviar = 'Clientes conectados:\n'

        for i in range(len(clientes_ativos)):
            if i == len(clientes_ativos) - 1:
                msg_a_enviar = msg_a_enviar + clientes_ativos[i][0]
            else:
                msg_a_enviar = msg_a_enviar + clientes_ativos[i][0] + ', '

        udp.sendto(msg_a_enviar.encode(), (cliente[0], cliente[1]))
    else:
        nome = ''

        for cliente_ativo in clientes_ativos:
            if cliente_ativo[2] == cliente[1]:
                nome = cliente_ativo[0]
                break

        for cliente_ativo in clientes_ativos:
            if cliente_ativo[0] != nome:
                msg_a_enviar = 'INFO:' + nome + ' saiu'
            else:
                msg_a_enviar = 'BYE'

            udp.sendto(msg_a_enviar.encode(), (cliente_ativo[1], cliente_ativo[2]))

        clientes_ativos.remove((nome, cliente[0], cliente[1]))

t.join()
udp.close()
tcp.close()
