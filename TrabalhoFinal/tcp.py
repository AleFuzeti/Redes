import socket
import time
import re
import const 

SERVER = const.DOWNLOAD
CLIENT = const.UPLOAD
PORT   = const.PORT
PACKET = const.PACKET
TIME   = const.TIME
MSG    = const.MSG
MODE   = const.MODE
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def format_number(number):
    return '{:,.0f}'.format(number).replace(',', '.')

def formatar_velocidade(bits_sec):
    if bits_sec >= 1e9:
        return f'{bits_sec / 1e9:.2f} Gbps'
    elif bits_sec >= 1e6:
        return f'{bits_sec / 1e6:.2f} Mbps'
    elif bits_sec >= 1e3:
        return f'{bits_sec / 1e3:.2f} Kbps'
    else:
        return f'{bits_sec:.2f} bps'

def imprimir_relatorio(packages_sent, packages_received, tempo, bits, bits_sec):
    print("\n---------------------------------------------------------")
    print(f"| Tempo final: {'{:,.5f}'.format(tempo).replace('.', ',')} segundos")
    print(f"| Tamanho total transmitido: {format_number(int(bits/8))} bytes")
    if packages_sent < packages_received:
        retranmission = packages_received - packages_sent
        print(f"| Pacotes enviados: {format_number(packages_sent)}" )
        print(f"| Pacotes recebidos: {format_number(packages_received - retranmission)} + {format_number(retranmission)} erro(s) = {format_number(packages_received)}")
        packages_sent = packages_received
    else:
        print(f"| Pacotes enviados: {format_number(packages_sent)}" )
        print(f"| Pacotes recebidos: {format_number(packages_received)}")
    print(f"| Pacotes perdidos: {format_number(packages_sent - packages_received)}")
    print(f"| Porcentagem de perda: {(packages_sent - packages_received)/packages_sent*100:.2f}%")
    print(f"| Velocidade de transmissão: {bits_sec}")
    pct_sec = '{:,.5f}'.format(packages_received/(tempo)).replace('.', '@').replace(',', '.').replace('@', ',')
    print(f"| Velocidade de transmissão: {pct_sec} pacotes/segundo")
    print( "---------------------------------------------------------")

def send_pack():
    packets_sent = 0
    start_time = time.time()
    aux_time = start_time
    end_time = start_time + TIME

    while(time.time() < end_time):
        current_time = time.time() - aux_time
        server_socket.send(MSG)
        packets_sent += 1
        if current_time >= 1:
            print(f"Tempo: {int(time.time()-start_time)} | pacotes: {packets_sent}")
            aux_time = time.time()
    tempo = time.time()-start_time
    print(f"Tempo: {int(time.time()-start_time)} | pacotes: {packets_sent}")

    return packets_sent, tempo

def run_client():
    server_socket.connect((SERVER, PORT))
    print("[CONNECTING] client connection established with host " + SERVER + " on port " + str(PORT))

    while True:
        start = input("Press enter to start: ")
        if start == '':
            break

    packets_sent, tempo = send_pack()

    time.sleep(0.5)
    msg = f"${int(packets_sent)}$".encode('utf-8')
    server_socket.send(msg)

    bits = len(PACKET) * packets_sent * 8

    server_socket.close()
    print(f"[CLOSE] Connection closed")

    time.sleep(0.5)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind((CLIENT, PORT+1))
    client_socket.listen(1)
    conn, addr = client_socket.accept()
    while True:
        msg = conn.recv(len(PACKET))  # Usar 'conn' para receber dados da conexão
        msg = msg.decode('utf-8')
        packets_received = int(msg)
        break
    client_socket.close()

    imprimir_relatorio(packets_sent, packets_received, tempo, bits, formatar_velocidade(bits/tempo).replace(".", ","))

def run_server():
    server_socket.bind((SERVER, PORT))
    server_socket.listen(1)
    conn, addr = server_socket.accept()
    loop = True
    packages_received = 0
    packages_sent = 0
    padrao = r'\$(\d+)\$'

    print("[STARTED] server is up and running on host " + SERVER + " on port " + str(PORT))
    print("[CONNECTED] connection accepted with client ")
    
    while True:
        data = conn.recv(len(PACKET))  # Usar 'conn' para receber dados da conexão

        if data != '' and loop:
            loop = False
            print(f"Mensagem recebida, aguarde {TIME} segundos...")
            start = time.time()

        msg = data.decode('utf-8')
        encerramento = re.match(padrao, msg)

        if encerramento:
            packages_sent = int(encerramento.group(1))
            print("Pacotes enviados", packages_sent)
            break
    
        tempo = time.time()
        packages_received += 1

    bits = len(PACKET) * packages_sent * 8
    bits_sec = bits / (tempo-start)
    bits_sec = formatar_velocidade(bits_sec)
    bits_sec = bits_sec.replace(".", ",")
    
    # imprime o relatório
    imprimir_relatorio(packages_sent, packages_received, tempo-start, bits, bits_sec)

    print(f"[CLOSE] Connection closed")

    conn.close()
    server_socket.close()

    time.sleep(1)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((CLIENT, PORT+1))
    msg = f"{int(packages_received)}".encode('utf-8')
    client_socket.send(msg)
    client_socket.close()

def main():
    while True:
        MODE = input("Enter mode (client or server): ")
        if MODE == "client":
            run_client()
            break
        elif MODE == "server":
            run_server()
            break
        else:
            print("[ERROR] Invalid MODE...")

if __name__ == "__main__":
    main()