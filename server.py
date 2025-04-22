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

HOST = '192.168.56.1'  # Địa chỉ IP của máy chủ trong mạng LAN
PORT = 12345

clients = []
names = []
scores = [0, 0]
current_question = {}
masked_answer = []
turn = 0  # 0 hoặc 1

wheel_options = ["MISS", "BANKRUPT", "DOUBLE", 100, 200, 300, 400, 500]

def broadcast(message):
    """Gửi thông điệp đến tất cả các client."""
    for client in clients:
        client.sendall(message.encode())

def mask_answer(answer):
    """Che giấu các ký tự của câu trả lời bằng dấu gạch dưới."""
    return ['_' if c.isalpha() else c for c in answer]

def send_question():
    """Gửi câu hỏi ngẫu nhiên và từ khóa (đã che giấu)."""
    global current_question, masked_answer
    current_question = random.choice(questions)
    masked_answer = mask_answer(current_question["answer"])
    broadcast(f"\nCâu hỏi: {current_question['question']}")
    broadcast(f"Từ khóa: {' '.join(masked_answer)}")

def handle_turn(player_id):
    """Quản lý lượt chơi của một người chơi."""
    global turn, masked_answer, scores

    client = clients[player_id]
    client.sendall(f"\nLượt của bạn ({names[player_id]}). Nhấn ENTER để quay nón...".encode())
    client.recv(1024)  # Đợi người chơi nhấn Enter

    result = random.choice(wheel_options)
    broadcast(f"{names[player_id]} quay nón và được: {result}")

    if result == "MISS":
        broadcast(f"{names[player_id]} bị mất lượt!")
    elif result == "BANKRUPT":
        scores[player_id] = 0
        broadcast(f"{names[player_id]} bị phá sản! Điểm hiện tại: 0")
    elif result == "DOUBLE":
        scores[player_id] *= 2
        broadcast(f"{names[player_id]} nhân đôi điểm! Tổng điểm: {scores[player_id]}")
    else:
        client.sendall("Nhập chữ cái hoặc đoán từ: ".encode())  # ✅ ĐÚNG

        guess = client.recv(1024).decode().strip().lower()

        if len(guess) == 1:  # Người chơi đoán 1 ký tự
            if guess in current_question["answer"]:
                for i, c in enumerate(current_question["answer"]):
                    if c == guess:
                        masked_answer[i] = guess
                scores[player_id] += result
                broadcast(f"Đúng rồi! Từ hiện tại: {' '.join(masked_answer)}")
                broadcast(f"Điểm {names[player_id]}: {scores[player_id]}")
            else:
                broadcast(f"Sai rồi! '{guess}' không có trong từ.")
        else:  # Người chơi đoán cả từ
            if guess == current_question["answer"]:
                broadcast(f"{names[player_id]} đoán đúng từ và chiến thắng!")
                scores[player_id] += 1000
                broadcast(f"Tổng điểm: {scores[player_id]}")
                broadcast("KẾT THÚC TRÒ CHƠI!")
                for c in clients:
                    c.close()
                exit()
            else:
                broadcast("Đoán sai rồi!")

    turn = 1 - turn  # Đổi lượt

def client_handler(client, player_id):
    """Quản lý quá trình xử lý mỗi client khi tham gia trò chơi."""
    client.sendall("Nhập tên người chơi: ".encode())  # ✅ ĐÚNG
    name = client.recv(1024).decode().strip()
    names.append(name)
    broadcast(f"{name} đã tham gia trò chơi.")

    if len(clients) == 2:
        broadcast("Cả 2 người chơi đã kết nối. Bắt đầu trò chơi!")
        send_question()

        while True:
            handle_turn(turn)

def start_server():
    """Khởi động server và lắng nghe kết nối từ client."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print(f"Server đang chạy tại {HOST}:{PORT}")

    while len(clients) < 2:
        client, addr = server.accept()
        clients.append(client)
        threading.Thread(target=client_handler, args=(client, len(clients)-1)).start()

if __name__ == "__main__":
    start_server()
