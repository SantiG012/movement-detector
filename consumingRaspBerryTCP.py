import socket

# Host and port
# 2 IP: 172.16.22.121 and 172.16.209.52
HOST = "172.16.22.121" # Host raspberry
PORT = 65432 # Port arbitrary

# Method consuming data from socket
def consumeDataRaspBerry():
    # Create socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind socket
        s.bind((HOST, PORT))
        # Listen socket
        s.listen()
        # Accept connection
        conn, addr = s.accept()
        # Print connection
        print("Connected by ", addr)
        # While True
        while True:
            # Data
            data = conn.recv(1024)
            # If not data
            if not data:
                # Break
                break
            # Print data
            print("Data: " + data.decode('utf-8'))
            # Send data
            conn.sendall(data)

# Main
if __name__ == "__main__":
    # Consume data
    consumeDataRaspBerry()