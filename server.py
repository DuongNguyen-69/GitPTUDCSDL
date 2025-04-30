# server.py
import socket
import threading
import random

# Danh sách câu hỏi và câu trả lời
questions = [
    {"question": "Thủ đô của Việt Nam là gì?", "answer": "hanoi"},
    {"question": "Trái cây màu đỏ, nhỏ, có vị chua ngọt là?", "answer": "strawberry"},
    {"question": "Mạng xã hội phổ biến nhất thế giới?", "answer": "facebook"},
    {"question": "Hệ điều hành mã nguồn mở nổi tiếng?", "answer": "linux"},
    {"question": "Ngôn ngữ lập trình phổ biến cho AI?", "answer": "python"},
]

HOST = ''  # Lắng nghe trên mọi interface
PORT = 12345

clients = []
names = []
scores = [0, 0]
current_question = {}
masked_answer = []
turn = 0
wheel_options = ["MISS", "BANKRUPT", "DOUBLE", 100, 200, 300, 400, 500]
clients_lock = threading.Lock()


def broadcast(message):
    """Gửi thông điệp đến tất cả các client."""
    with clients_lock:
        for c in clients[:]:
            try:
                c.sendall((message + '\n').encode())
            except:
                clients.remove(c)


def mask_answer(answer):
    return ['_' if ch.isalpha() else ch for ch in answer]


def send_question():
    global current_question, masked_answer
    current_question = random.choice(questions)
    masked_answer = mask_answer(current_question['answer'])
    broadcast(f"Câu hỏi: {current_question['question']}")
    broadcast(f"Từ khóa: {' '.join(masked_answer)}")


def handle_turn(player_id):
    global turn, masked_answer, scores
    client = clients[player_id]
    name = names[player_id]
    try:
        client.sendall("Lượt của bạn. Nhấn ENTER để quay nón...\n".encode())
        client.recv(1024)
        result = random.choice(wheel_options)
        broadcast(f"{name} quay nón và được: {result}")

        if result == "MISS":
            broadcast(f"{name} bị mất lượt!")
        elif result == "BANKRUPT":
            scores[player_id] = 0
            broadcast(f"{name} bị phá sản! Điểm về 0.")
            for idx, nm in enumerate(names):
                broadcast(f"Điểm {nm}: {scores[idx]}")
        elif result == "DOUBLE":
            scores[player_id] *= 2
            broadcast(f"{name} nhân đôi điểm! Tổng: {scores[player_id]}")
            for idx, nm in enumerate(names):
                broadcast(f"Điểm {nm}: {scores[idx]}")
        else:
            client.sendall("Nhập chữ cái hoặc đoán từ: \n".encode())
            guess = client.recv(1024).decode().strip().lower()
            answer = current_question['answer']
            if len(guess) == 1:
                count = answer.count(guess)
                if count:
                    for i, ch in enumerate(answer):
                        if ch == guess:
                            masked_answer[i] = guess
                    scores[player_id] += result * count
                    broadcast(f"Có {count} chữ '{guess}'")
                    broadcast(f"Từ hiện tại: {' '.join(masked_answer)}")
                    for idx, nm in enumerate(names):
                        broadcast(f"Điểm {nm}: {scores[idx]}")
                else:
                    broadcast(f"Không có chữ '{guess}' nào.")
            else:
                if guess == answer:
                    scores[player_id] += 1000
                    broadcast(f"{name} đoán đúng và chiến thắng! +1000 điểm")
                    broadcast("KẾT THÚC TRÒ CHƠI!")
                    return True
                else:
                    broadcast(f"Đoán sai từ '{guess}'.")
    except:
        with clients_lock:
            if client in clients: clients.remove(client)
    finally:
        turn = 1 - turn
    return False


def client_handler(client, player_id):
    try:
        client.sendall("Nhập tên người chơi: \n".encode())
        name = client.recv(1024).decode().strip()
        with clients_lock:
            names.append(name)
        broadcast(f"{name} đã tham gia.")

        if len(clients) == 2:
            broadcast("Bắt đầu trò chơi!")
            send_question()
            while True:
                if handle_turn(turn): break
    except:
        with clients_lock:
            if client in clients: clients.remove(client)
    finally:
        try: client.close()
        except: pass


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print(f"Server chạy tại {HOST or '0.0.0.0'}:{PORT}")
    while True:
        client, addr = server.accept()
        print(f"Client {addr} kết nối")
        with clients_lock:
            clients.append(client)
        threading.Thread(target=client_handler, args=(client, len(clients)-1), daemon=True).start()

if __name__ == '__main__':
    start_server()
