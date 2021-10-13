import socket
import os
import logging
from datetime import datetime
import hashlib
import threading
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address given on the command line
ip=''
puerto=10100
server_address = (ip, 10002)

sock.bind(server_address)
print('starting up on {} port {}'.format(*sock.getsockname()))
sock.listen(25)

# Separador
SEPARATOR = "SEPARATOR"

#Archivos a enviar
file1 = "Archivos/temp_100MB_file.txt"
file2 = "Archivos/temp_250MB_file.txt"

#Nombre archivos a enviar
filename1 = "temp_100MB_file.txt"
filename2 = "temp_250MB_file.txt"

#Tamaño de los archivos
filesize1 = os.path.getsize(file1)
filesize2 = os.path.getsize(file2)

#Array vacio de conecciones
conexiones = []

#Array vacio con tiempos de entrega del archivo
tiempos = []

#Array vacio con variable que indica si la transmisión fue exitosa o no
exitos = []

#Nombre log
LOG_FILENAME = datetime.now().strftime('./Logs/%Y_%m_%d_%H_%M_%S.log')

#Variable para cerrar servidor
fin = False

#Tamaño del buffer
BUFFER_SIZE = 1024


#Función envío de archivos
def archivo(num_archivo, c, i):
    nombreArchivo = ''
    tamArchivo = 0
    arch = ''
    #udpsock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #udpsock.bind((ip,puerto+i))
    if (num_archivo == 1):
        nombreArchivo = filename1
        tamArchivo = filesize1
        arch = file1
    elif (num_archivo == 2):
        nombreArchivo = filename2
        tamArchivo = filesize2
        arch = file2
    start_time = datetime.now()
    udpsock.sendto(f"{nombreArchivo}{SEPARATOR}{tamArchivo}", ip, puerto+i)
    with open(arch, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                end_time = datetime.now()
                tiempo = end_time - start_time
                tiempos.append(tiempo)
                break
            udpsock.sendto(bytes_read, ip, puerto+i)
    message = b'Finaliza transmision'
    udpsock.sendto(message, ip, puerto+i)
    md5(udpsock, arch, i)

#Función de creación y envío de hash
def md5(connection, fname, i):
    md5 = hashlib.md5()
    with open(fname, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            md5.update(data)
    connection.sendto(md5.hexdigest().encode('ISO-8859-1'), ip, puerto+i)
    data = connection.recv(BUFFER_SIZE)
    mensaje2 = data.decode('utf-8')
    exito = 0
    if ('Los valores son iguales' in mensaje2):
        exito = 1
    elif ('Los valores son diferentes' in mensaje2):
        exito = 0
    exitos.append(exito)

#Función para crear el log
def log(filenameF, filesize, exitos, tiempos):
    filename = LOG_FILENAME
    logging.basicConfig(filename = filename, encoding='utf-8', level=logging.INFO)
    logging.info('Nombre archivo:' + filenameF)
    logging.info('Tamaño archivo:' + str(filesize))
    i = 1
    for c in conexiones:
        logging.info('Cliente ' + str(i))
        if (exitos[i-1] == 1):
            logging.info('Archivo fue entregado exitosamente')
        else:
            logging.info('Archivo no fue entregado exitosamente')
        logging.info('Tiempo de transferencia archivo cliente ' + str(i) + ': '+ str(tiempos[i-1]) + " milisegundos")
        i += 1
    return filename

if __name__ == "__main__":
 while True:
    threads = []
    print('waiting for a connection')
    num_archivo = int(input('¿Qué archivo desea enviar? (1: 100MB, 2: 250MB)'))
    num_clientes = int(input('¿A cuantos clientes desea enviar el archivo?'))
    nomArchivo = ''
    tamArchivo = 0
    if (num_archivo == 1):
        nomArchivo = filename1
        tamArchivo = filesize1
    elif (num_archivo == 2):
        nomArchivo = filename2
        tamArchivo = filesize2

    udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpsock.bind((ip, 65535))
    try:
        while True:
            connection, client_address = sock.accept()
            data = connection.recv(BUFFER_SIZE)
            print('received {!r}'.format(data))
            mensaje = data.decode('utf-8')
            if mensaje == ('Listo para recibir'):
                conexiones.append(connection)
            if len(conexiones) >= num_clientes:
                i=1
                for c in conexiones:
                    x = threading.Thread(target=archivo, args=(num_archivo, c, i))

                    x.start()
                    time.sleep(1)
                    threads.append(x)
                    i += 100
                for x in threads:
                    x.join()
                fin = True
                break
    finally:
      #  filename = log(nomArchivo, tamArchivo, exitos, tiempos)
        connection.close()
        if fin:
            break