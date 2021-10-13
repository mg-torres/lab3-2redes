
import socket
import os
import hashlib
import time
import threading
import logging
from datetime import datetime

#Separador
SEPARATOR = "SEPARATOR"

#Tamaño del buffer
BUFFER_SIZE = 1024

#Nombre log
LOG_FILENAME = datetime.now().strftime('./Logs/%Y_%m_%d_%H_%M_%S_CLI.log')

#Array vacio de conecciones
conexiones = []

#Array vacio con tiempos de entrega del archivo
tiempos = []

#Array vacio con variable que indica si la transmisión fue exitosa o no
exitos = []

#Variable para cerrar conexiones
fin = False

filenames = []
filesizes = []

#Puerto e ip
ip=''
puerto=10100
server_address = (ip, puerto)

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
    connection.sendto(mssg, ip, puerto+i)

#Función para crear el log
def log(filenames, filesizes, exitos, tiempos):
    filename = LOG_FILENAME
    logging.basicConfig(filename = filename, encoding='utf-8', level=logging.INFO)
    logging.info('Nombre archivo:' + filenames[0])
    logging.info('Tamaño archivo:' + str(filesizes[0]))
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

#Función para crear los clientes
def createSocket(i, num_clientes):
    sock = socket.create_connection(('localhost', 10002))
    conexiones.append(i)
    udpsock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    while True:
        message = b'Listo para recibir'
        sock.send(message)
        #received = sock.recv(BUFFER_SIZE).decode('ISO-8859-1')
        received = udpsock.recvfrom(BUFFER_SIZE)
        if('SEPARATOR' in received):
            filenameF, filesizeF = received.split(SEPARATOR)
            newFilename = 'Cliente'+str(i+1)+'-Prueba'+str(num_clientes)+'.txt'
            newFilename = os.path.basename(newFilename)
            var=os.path.join("./ArchivoRecibidos", newFilename)
            filesizeF = int(filesizeF)
            filenames.append(filenameF)
            filesizes.append(filesizeF)
        try:
            start_time = datetime.now()
            with open(var, "w") as f:
                while True:
                    bytes_read = udpsock.recvfrom(BUFFER_SIZE)
                    if ('Finaliza transmision' in bytes_read.decode('ISO-8859-1')):
                        end_time = datetime.now()
                        tiempo = end_time - start_time
                        tiempos.append(tiempo)
                        break
                    f.write(bytes_read.decode('ISO-8859-1'))
        finally:
            f.close()
            received = udpsock.recvfrom(BUFFER_SIZE).decode('ISO-8859-1')
            md5(udpsock,var,received, i)
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
            #filenameLog = log(filenames, filesizes, exitos, tiempos)
            if fin:
                break
