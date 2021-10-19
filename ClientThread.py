
import socket
import os
import hashlib
import time
import threading
import logging
from datetime import datetime
import pyshark

#Separador
SEPARATOR = "SEPARATOR"

#Tamaño del buffer
BUFFER_SIZE = 1024

#Nombre log
LOG_FILENAME = datetime.now().strftime('./Logs/%Y_%m_%d_%H_%M_%S.log')

#Array vacio de conecciones
conexiones = []

#Array vacio con tiempos de entrega del archivo
tiempos = []

#Array vacio con variable que indica si la transmisión fue exitosa o no
exitos = []

#Array vacio con el número de paquetes enviados
paquetes = []

#Array vacio con el número de bytes enviados
bytes = []

#Variable para cerrar conexiones
fin = False

filenames = []
filesizes = []

#Puertos e ip
#IP servidor
ipServ='localhost'
ipCli='localhost'
#Puerto sockets UDP
puerto2=65535

#Función de creación y envío de hash
def md5(connection, fname, hashrecibido, i):
    mssg = ''
    exito = 0
    md5 = hashlib.md5()
    with open(fname, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            md5.update(data)
    if (format(md5.hexdigest()) == hashrecibido):
        mssg = b'Los valores son iguales'
        exito = 1
    else:
        mssg = b'Los valores son diferentes'
        exito = 0
    exitos.append(exito)
    connection.send(mssg)

#Función para crear el log
def log(filenames, filesizes, exitos, tiempos, paquetes, bytes):
    filename = LOG_FILENAME
    logging.basicConfig(filename = filename, encoding='utf-8', level=logging.INFO)
    logging.info('Nombre archivo:' + filenames[0])
    logging.info('Tamaño archivo:' + str(filesizes[0]))
    i = 0
    for c in conexiones:
        logging.info('Cliente ' + str(i+1))
        if (exitos[i] == 1):
            logging.info('Archivo fue entregado exitosamente')
        else:
            logging.info('Archivo no fue entregado exitosamente')
        logging.info('Tiempo de transferencia archivo cliente ' + str(i+1) + ': '+ str(tiempos[i]) + " milisegundos")
        logging.info('Total de paquetes transmitidos cliente ' + str(i+1) + ': ' + str(paquetes[i]))
        logging.info('Total de bytes transmitidos cliente ' + str(i+1) + ': ' + str(bytes[i]))
        i += 1
    return filename

#Función para crear los clientes
def createSocket(i, num_clientes):
    sock = socket.create_connection((ipServ, 10000))
    conexiones.append(i)
    udpsock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    time.sleep(1)
    udpsock.bind((ipCli, puerto2-i))
    while True:
        message = b'Listo para recibir'
        sock.send(message)
        received = sock.recv(BUFFER_SIZE)
        if('SEPARATOR' in received.decode('ISO-8859-1')):
            filenameF, filesizeF = received.decode('ISO-8859-1').split(SEPARATOR)
            newFilename = 'Cliente'+str(i)+'-Prueba'+str(num_clientes)+'.txt'
            newFilename = os.path.basename(newFilename)
            var=os.path.join("./ArchivosRecibidos", newFilename)
            filesizeF = int(filesizeF)
            filenames.append(filenameF)
            filesizes.append(filesizeF)
        try:
            start_time = datetime.now()
            paqs = 0
            bytes_env = 0
            with open(var, "w") as f:
                while True:
                    bytes_read, addr = udpsock.recvfrom(BUFFER_SIZE)
                    if ('Finaliza transmision' in bytes_read.decode('ISO-8859-1')):
                        end_time = datetime.now()
                        tiempo = end_time - start_time
                        tiempos.append(tiempo)
                        paquetes.append(paqs)
                        bytes.append(bytes_env)
                        break
                    f.write(bytes_read.decode('ISO-8859-1'))
                    paqs += 1
                    bytes_env += BUFFER_SIZE
            f.close()
        finally:
            received= sock.recv(BUFFER_SIZE)
            md5(sock,var,received.decode('ISO-8859-1'), i)
            fin = True
            print('closing socket')
            sock.close()
            if (fin):
                break

if __name__ == "__main__":
    while True:
        threads = []
        num_clientes = int(input('¿Cuantos clientes recibirán el archivo?'))
        try:
            while True:
                for i in range (num_clientes):
                    x = threading.Thread(target=createSocket, args=(i+1, num_clientes))
                    time.sleep(1)
                    x.start()
                    threads.append(x)
                for x in threads:
                    x.join()
                fin = True
                break
        finally:
            filenameLog = log(filenames, filesizes, exitos, tiempos, paquetes, bytes)
            if fin:
                break
