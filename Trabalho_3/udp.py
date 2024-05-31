import socket
import time
import re
import const

SERVER = const.DOWNLOAD
CLIENT = const.UPLOAD
PORT = const.PORT
PACKET = const.PACKET
TIME = const.TIME

_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def format_number(number):
    return '{:,.0f}'.format(number).replace(',', '.')

def formatar_velocidade(bits_por_segundo):
    if bits_por_segundo >= 1e9:
        return f'{bits_por_segundo / 1e9:.2f} Gbps'
    elif bits_por_segundo >= 1e6:
        return f'{bits_por_segundo / 1e6:.2f} Mbps'
    elif bits_por_segundo >= 1e3:
        return f'{bits_por_segundo / 1e3:.2f} Kbps'
    else:
        return f'{bits_por_segundo:.2f} bps'

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

# Manda as mensagens para o servidor
def send_pack():
    packets_sent = 0
    msg = f"{PACKET}".encode('utf-8')
    start_time = time.time()
    aux_time = start_time
    end_time = start_time + TIME
    while(time.time() < end_time):
        current_time = time.time() - aux_time
        _socket.sendto(msg, (SERVER, PORT))
        packets_sent += 1
        if current_time >= 1:
            print(f"Tempo: {int(time.time()-start_time)} | pacotes: {packets_sent}")
            aux_time = time.time()
    tempo = time.time()-start_time
    print(f"Tempo final: {(tempo):.5f} | pacotes: {packets_sent}")
    print(f"\nVelocidade de transmissão: {packets_sent/(tempo):.2f} pacotes/segundo")
    return packets_sent, tempo

def run_client():
    # Cria o socket UDP
    print(f"[CONNECTING] Sendind message to host {SERVER} on port {PORT}")
        
    while True:
        start = input("Press enter to start: ")
        if start == '':
            break
    
    # Envia o pacote
    packets_sent, tempo = send_pack()
 
    msg = f"{'pacotes'}{packets_sent}".encode('utf-8')
    for i in range(1000):    
        _socket.sendto(msg, (SERVER, PORT))

    bits = len(PACKET) * packets_sent * 8
    
    _socket.close()
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
    # Cria o socket UDP e o associa ao endereço e porta do servidor
    _socket.bind((SERVER, PORT))
    print(f"[CONNECTING] Server opened on port {PORT}")
    
    loop = True
    packages_received = 0
    packages_sent = 0
    
    # Define o padrão da expressão regular da mensagem de encerramento
    padrao = r'pacotes(\d+)'
    #padrao = r'$(\d+)$'

    while True: 
        data, addr = _socket.recvfrom(len(PACKET))  
        
        # Inicia a contagem do tempo na primeira mensagem recebida
        if data != '' and loop:
            start = time.time()
            loop = False
            print(f"Mensagem recebida, aguarde {TIME} segundos...")

        msg = data.decode('utf-8')
    
        # Tenta encontrar uma correspondência na string
        encerramento = re.match(padrao, msg)

        if encerramento:
            # Se houver correspondência, o número estará no primeiro grupo de captura
            packages_sent = int(encerramento.group(1))
            print("Número encontrado:", packages_sent)
            break

        tempo = time.time()
        packages_received += 1


    # Calcula o número de pacotes enviados e a velocidade de transmissão
    bits = len(PACKET) * packages_sent * 8
    bits_sec = bits / (tempo-start)
    bits_sec = formatar_velocidade(bits_sec)
    bits_sec = bits_sec.replace(".", ",")
    
    # imprime o relatório
    imprimir_relatorio(packages_sent, packages_received, tempo-start, bits, bits_sec)

    _socket.close()
    print(f"[CLOSE] Connection closed")

    time.sleep(1)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((CLIENT, PORT+1))
    msg = f"{int(packages_received)}".encode('utf-8')
    client_socket.send(msg)
    client_socket.close()

def main():
    while True:
        mode = input("Enter mode (client or server): ")
        if mode == "client":
            run_client()
            break
        elif mode == "server":
            run_server()
            break
        else:
            print("[ERROR] Invalid mode...")

if __name__ == "__main__":
    main()