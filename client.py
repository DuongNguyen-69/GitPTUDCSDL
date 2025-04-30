# client.py
import socket
import threading

class GameClient:
    def __init__(self, host, port, on_message):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.on_message = on_message
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def _recv_loop(self):
        while True:
            data = self.sock.recv(4096)
            if not data:
                break
            self.on_message(data.decode())

    def send(self, msg: str):
        if not msg.endswith("\n"):
            msg += "\n"
        self.sock.sendall(msg.encode())

    def close(self):
        try:
            self.sock.close()
        except:
            pass


if __name__ == '__main__':
    # Simple console client
    def print_msg(msg):
        print(msg, end='')

    client = GameClient('127.0.0.1', 12345, print_msg)
    try:
        while True:
            line = input()
            client.send(line)
    except KeyboardInterrupt:
        client.close()