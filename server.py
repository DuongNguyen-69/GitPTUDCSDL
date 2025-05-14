import os
import socket
import threading
import random
from datetime import datetime

questions = [
    {"question": "Thủ đô của Việt Nam là gì?", "answer": "hanoi"},
    {"question": "Trái cây màu đỏ, nhỏ, có vị chua ngọt là?", "answer": "strawberry"},
    {"question": "Mạng xã hội phổ biến nhất thế giới?", "answer": "facebook"},
    {"question": "Hệ điều hành mã nguồn mở nổi tiếng?", "answer": "linux"},
    {"question": "Ngôn ngữ lập trình phổ biến cho AI?", "answer": "python"},
]

HOST = ''
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
    with clients_lock:
        for c in clients[:]:
            try:
                c.sendall(message.encode())
            except (ConnectionResetError, BrokenPipeError):
                clients.remove(c)


def mask_answer(answer):
    return ['_' if ch.isalpha() else ch for ch in answer]


def send_question():
    global current_question, masked_answer
    current_question = random.choice(questions)
    masked_answer = mask_answer(current_question['answer'])
    broadcast(f"\nCâu hỏi: {current_question['question']}")
    broadcast(f"Từ khóa: {' '.join(masked_answer)}")


def update_turn():
    global turn
    current_player = names[turn]
    broadcast(f"\nĐến lượt {current_player}!")


def log_history(player_name, action, guess, result, score):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("lichsu_game.txt", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {player_name} {action}: '{guess}' - {result} (Điểm: {score})\n")

def update_leaderboard(name, score):
    with open("bangxephang.txt", "a", encoding="utf-8") as f:
        f.write(f"{name}: {score}\n")

def handle_turn(player_id):
    global turn, masked_answer, scores
    client = clients[player_id]
    name = names[player_id]
    try:
        client.sendall(f"\nLượt của bạn ({name}). Nhấn ENTER để quay nón...".encode())
        client.recv(1024)
        result = random.choice(wheel_options)
        broadcast(f"{name} quay nón và được: {result}")

        if result == "MISS":
            broadcast(f"{name} bị mất lượt!")
            log_history(name, "mất lượt", "-", "MISS", scores[player_id])
        elif result == "BANKRUPT":
            scores[player_id] = 0
            broadcast(f"{name} bị phá sản! Điểm về 0.")
            log_history(name, "phá sản", "-", "BANKRUPT", 0)
        elif result == "DOUBLE":
            scores[player_id] *= 2
            broadcast(f"{name} nhân đôi điểm! Tổng điểm: {scores[player_id]}")
            log_history(name, "nhân đôi", "-", "DOUBLE", scores[player_id])
        else:
            client.sendall("Nhập chữ cái hoặc đoán từ: ".encode())
            guess = client.recv(1024).decode().strip().lower()
            answer = current_question['answer']

            if len(guess) == 1:
                count = answer.count(guess)
                if count > 0:
                    for i, ch in enumerate(answer):
                        if ch == guess:
                            masked_answer[i] = guess
                    scores[player_id] += result * count
                    broadcast(f"Có {count} chữ '{guess}' trong từ.")
                    broadcast(f"Từ hiện tại: {' '.join(masked_answer)}")
                    log_history(name, "đoán chữ", guess, "ĐÚNG", scores[player_id])
                else:
                    broadcast(f"Không có chữ '{guess}' nào.")
                    log_history(name, "đoán chữ", guess, "SAI", scores[player_id])
            else:
                if guess == answer:
                    scores[player_id] += 1000
                    broadcast(f"{name} đoán đúng từ và chiến thắng! +1000 điểm (Tổng: {scores[player_id]})")
                    broadcast("KẾT THÚC TRÒ CHƠI!")
                    leaderboard_data = sorted(zip(names, scores), key=lambda x: x[1], reverse=True)
                    rank_text = "HIỂN_THỊ_BXH\n" + "\n".join(f"{i+1}. {n}: {s} điểm" for i, (n, s) in enumerate(leaderboard_data))
                    broadcast(rank_text)


                    log_history(name, "đoán từ", guess, "ĐÚNG", scores[player_id])
                    update_leaderboard(name, scores[player_id])

                    return True

                else:
                    broadcast(f"Đoán sai từ '{guess}'.")
                    log_history(name, "đoán từ", guess, "SAI", scores[player_id])

        for idx, nm in enumerate(names):
            broadcast(f"Điểm {nm}: {scores[idx]}")
    except (ConnectionResetError, BrokenPipeError):
        with clients_lock:
            if client in clients:
                clients.remove(client)
    finally:
        turn = 1 - turn
        update_turn()
    return False


def client_handler(client, player_id):
    try:
        client.sendall("Nhập tên người chơi: ".encode())
        name = client.recv(1024).decode().strip()
        with clients_lock:
            names.append(name)
        broadcast(f"{name} đã tham gia trò chơi.")

        if len(clients) == 2:
            broadcast("Cả 2 người chơi đã kết nối. Bắt đầu trò chơi!")
            send_question()
            update_turn()
            while True:
                if handle_turn(turn):
                    break
    except (ConnectionResetError, BrokenPipeError):
        with clients_lock:
            if client in clients:
                clients.remove(client)
    finally:
        try:
            client.close()
        except:
            pass


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print(f"Server đang chạy tại {HOST or '0.0.0.0'}:{PORT}")

    while True:
        client, addr = server.accept()
        print(f"Client {addr} đã kết nối!")
        with clients_lock:
            clients.append(client)
        threading.Thread(target=client_handler, args=(client, len(clients) - 1), daemon=True).start()


if __name__ == "__main__":
    start_server()
