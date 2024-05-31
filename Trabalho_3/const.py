# ---------------------CONSTANTES---------------------#

# Define o endereço do servidor e a porta
#MODE    = "server" 
DOWNLOAD   = "169.254.25.251"

#MODE     = "client"
UPLOAD = "169.254.44.240"

MODE = ''
PORT = 2223

# Define os tamanhos para o pacote
PACKET = 'teste de rede *2023*' * 25 # 500 bytes
MSG    = f"{PACKET}".encode('utf-8')
TIME   = 20

# ----------------------------------------------------#