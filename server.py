import socket
import json
from arduinoLedRGB import controlLed

HOST = '192.168.68.105'  # Dirección IP del servidor
PORT = 65432  # Puerto a utilizar

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print('Esperando conexiones...')

    conn, addr = s.accept()
    with conn:
        print('Conexión establecida por', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                print("Conexión cerrada por el cliente.")
                break
            print('Mensaje recibido:', data.decode())

            # Convertir a JSON
            json_data = json.loads(data.decode())

            # Obtener el color
            color = json_data['color']

            # Controlar el bombillo
            controlLed(color)
            
            conn.sendall(data)
    print("Servidor cerrado.")
