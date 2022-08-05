# Protocolo HFTP
Llamaremos Home-made File Transfer Protocol (HFTP) a un protocolo de transferencia de
archivos casero.
    
HFTP es un protocolo de capa de aplicación que usa TCP como protocolo de transporte. Un servidor de HFTP escucha pedidos en el puerto TCP 19500.

El cliente HFTP inicia el intercambio de mensajes mediante pedidos o comandos al servidor. El
servidor envía una respuesta a cada uno antes de procesar el siguiente hasta que el cliente
envía un comando de fin de conexión. En caso de que el cliente envíe varios pedidos
consecutivos, el servidor HFTP los responde en el orden en que se enviaron. El protocolo
HFTP es un protocolo ASCII, no binario, por lo que todo lo enviado (incluso archivos binarios)
será legible por humanos como strings.

## Comandos disponibles 
`get_file_listing`  = Este comando no recibe argumentos y busca obtener la lista de
archivos que están actualmente disponibles. El servidor responde
con una secuencia de líneas terminadas en \r\n, cada una con el
nombre de uno de los archivos disponible. Una línea sin texto
indica el fin de la lista.

`get_metadata FILENAME` = Este comando recibe un argumento FILENAME especificando un
nombre de archivo del cual se pretende averiguar el tamaño . El2
servidor responde con una cadena indicando su valor en bytes.

`get_slice FILENAME OFFSET SIZE` = Este comando recibe en el argumento FILENAME el nombre de
archivo del que se pretende obtener un slice o parte. La parte se
especifica con un OFFSET (byte de inicio) y un SIZE (tamaño de la
parte esperada, en bytes), ambos no negativos . El servidor3
responde con el fragmento de archivo pedido codificado en
base64 y un \r\n.

| Comandos   |  Respuestas  |
|------------|--------------|
| `get_file_listing`| 0 OK\r\n       |
|                     | archivo1.txt\r\n |
|                     | archivo2.jpg\r\n |
|                     | \r\n             |
|--------------------|-------------------|
|`get_metadata FILENAME`| 0 OK\r\n       |
|                       | 3199\r\n |
|--------------------|-------------------|
|`get_slice FILENAME OFFSET SIZE`| 0 OK\r\n  |
|                                |Y2Fsb3IgcXVlIGhhY2UgaG95LCA=\r\n |
|--------------------|-------------------|
| `quit` | 0 OK\r\n |

## Ejecucion 

En la carpeta `testdata` es en donde pueden agregar archivos para que el cliente pida informacion sobre dichos archivos.

### Del lado del server 
```
federico@federico:~/github/HFTP$ python3 server.py
Serving testdata on 0.0.0.0:19500.
```
### Del lado del cliente

Puede utilizar el comando `telnet "dir IP" "num Port"`

```
federico@federico:~/github/HFTP$ telnet 0.0.0.0 19500
Trying 0.0.0.0...
Connected to 0.0.0.0.
Escape character is '^]'.
```
y ya pueden mandar los comandos al servidor.