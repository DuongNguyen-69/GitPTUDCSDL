# server.py
import socket
import threading
import json
import random
import time
from game_config import (
    SERVER_HOST, SERVER_PORT, MAX_PLAYERS,
    PUZZLES, WHEEL_SEGMENTS, BUFFER_SIZE,
    BONUS_POINTS_FOR_SOLVE, LUCKY_SPIN_POINTS
)

clients = [] # List các (connection, address)
player_data = {} # key: conn, value: {"id": "P1", "name": "PlayerName", "score": 0, "current_spin_value": 0}

current_puzzle_data = {}
masked_puzzle = ""
current_turn_idx = 0 # Index của người chơi trong list `clients`
game_started = False
game_over = False
winner_id = None # Sẽ là "P1", "P2", ...

# --- Khóa để đồng bộ hóa truy cập vào tài nguyên dùng chung ---
clients_lock = threading.Lock()
game_state_lock = threading.Lock()

def get_player_id_by_conn(conn):
    with clients_lock:
        for i, (c_conn, _) in enumerate(clients):
            if c_conn == conn:
                return f"P{i+1}"
    return None

def initialize_game():
    global current_puzzle_data, masked_puzzle, current_turn_idx
    global game_started, game_over, winner_id, player_data

    with game_state_lock:
        current_puzzle_data = random.choice(PUZZLES)
        puzzle_phrase = current_puzzle_data["phrase"]
        # Chỉ ẩn các ký tự chữ và số
        masked_puzzle = "".join([char if not char.isalnum() else "_" for char in puzzle_phrase])

        with clients_lock: # Cần lock clients khi duyệt clients
            for conn, _ in clients:
                player_id = get_player_id_by_conn(conn)
                if player_id and conn in player_data: # Chỉ reset score nếu player còn tồn tại
                    player_data[conn]["score"] = 0
                    player_data[conn]["current_spin_value"] = 0
                # Tên người chơi được giữ nguyên từ lần đặt tên đầu tiên

        current_turn_idx = 0
        game_started = True
        game_over = False
        winner_id = None
        print(f"[GAME] Bắt đầu game mới. Câu đố: {current_puzzle_data['phrase']}")
        current_player_name = player_data[clients[current_turn_idx][0]]["name"]
        broadcast_game_state(f"Game bắt đầu! Lượt của {current_player_name} ({player_data[clients[current_turn_idx][0]]['id']}).")


def broadcast_game_state(message_log=""):
    global masked_puzzle, current_turn_idx, game_started, game_over, winner_id, player_data
    if not clients:
        return

    with game_state_lock:
        scores_list = []
        current_player_conn = None
        if game_started and not game_over and clients: # Đảm bảo clients không rỗng
            current_player_conn = clients[current_turn_idx][0]

        with clients_lock: # Cần lock clients khi duyệt
            for conn, _ in clients:
                if conn in player_data:
                    scores_list.append({
                        "id": player_data[conn]["id"],
                        "name": player_data[conn]["name"],
                        "score": player_data[conn]["score"]
                    })

        state = {
            "type": "game_update",
            "puzzle": masked_puzzle,
            "category": current_puzzle_data.get("category", "Không có chủ đề"),
            "scores": scores_list,
            "is_my_turn": False, # Sẽ được client tự xác định dựa trên my_player_id
            "game_over": game_over,
            "winner": winner_id, # Gửi ID của người chiến thắng (P1, P2)
            "message_log": message_log,
            "game_started": game_started
        }
        if current_player_conn and current_player_conn in player_data: # Thêm tên người chơi hiện tại
            state["current_player_turn_name"] = player_data[current_player_conn]["name"]
            state["current_player_turn_id"] = player_data[current_player_conn]["id"]


    with clients_lock:
        active_clients = list(clients) # Tạo bản sao để tránh lỗi thay đổi kích thước khi duyệt
        for conn, _ in active_clients:
            try:
                state_copy = state.copy()
                if conn in player_data: # Chỉ gửi nếu client còn trong player_data
                    state_copy["my_player_id"] = player_data[conn]["name"] # Tên người chơi
                    state_copy["my_player_server_id"] = player_data[conn]["id"] # P1, P2
                    state_copy["is_my_turn"] = (conn == current_player_conn) and not game_over and game_started
                    
                    conn.sendall((json.dumps(state_copy) + "\n").encode('utf-8'))
            except Exception as e:
                print(f"[SERVER_ERROR] Lỗi gửi trạng thái cho {player_data.get(conn, {}).get('name', conn.getpeername())}: {e}")
                # Không remove client ở đây, để client_thread xử lý


def handle_client_action(client_conn, action_data):
    global masked_puzzle, current_turn_idx, game_over, winner_id, player_data, game_started

    action_type = action_data.get("type")
    player_info = player_data.get(client_conn)

    if not player_info:
        print(f"[SERVER_WARNING] Nhận action từ client không xác định: {client_conn.getpeername()}")
        return

    player_log_name = f"{player_info['name']} ({player_info['id']})"
    message_log = ""

    with game_state_lock:
        if game_over or not game_started:
            if action_type != "set_name":  # Cho phép đặt tên ngay cả khi game chưa bắt đầu
                return

        if action_type != "set_name" and clients[current_turn_idx][0] != client_conn:
            try:
                error_msg = {"type": "error", "message": "Không phải lượt của bạn!"}
                client_conn.sendall((json.dumps(error_msg) + "\n").encode('utf-8'))
            except Exception as e:
                print(f"[SERVER_ERROR] Gửi lỗi 'không phải lượt': {e}")
            return

        if action_type == "set_name":
            name = action_data.get("name", f"Player_{player_info['id'][1:]}").strip()
            if not name: name = f"Player_{player_info['id'][1:]}"  # Tên mặc định nếu rỗng
            player_info["name"] = name
            print(f"[SERVER] {client_conn.getpeername()} ({player_info['id']}) đặt tên là: {name}")
            
            # Kiểm tra nếu tất cả client đã đặt tên và đủ người chơi thì bắt đầu game
            all_names_set = True
            with clients_lock:
                if len(clients) < MAX_PLAYERS:
                    all_names_set = False  # Chưa đủ người chơi
                else:
                    for conn_c, _ in clients:
                        if conn_c not in player_data or not player_data[conn_c].get("name") or "Người chơi" in player_data[conn_c].get("name"):
                            if player_data[conn_c].get("name") == player_data[conn_c].get("id"):
                                all_names_set = False
                                break
            
            if all_names_set and len(clients) == MAX_PLAYERS and not game_started:
                print("[SERVER] Tất cả người chơi đã sẵn sàng. Bắt đầu game...")
                game_started = True  # Đánh dấu game đã bắt đầu
                time.sleep(0.5)
                initialize_game()
                # Gửi thông báo game bắt đầu
                broadcast_game_state({
                    "type": "game_update",
                    "game_started": True,
                    "message": "Game bắt đầu..."
                })
            else:
                broadcast_game_state({
                    "type": "game_update",
                    "game_started": False,
                    "message": f"{player_log_name} đã tham gia."
                })
            return  # Xử lý set_name xong thì return luôn

        if game_started:
            # Tiếp tục xử lý các hành động khi game đã bắt đầu
            if action_type == "spin_wheel":
                result = random.choice(WHEEL_SEGMENTS)
                player_info["current_spin_value"] = 0  # Reset trước khi quay mới
                message_log = f"{player_log_name} quay vào: {result}."
                print(f"[GAME] {player_log_name} quay vào: {result}")

                if isinstance(result, int):
                    player_info["current_spin_value"] = result
                    message_log += " Hãy đoán một chữ cái."
                elif result == "MAT LUOT":
                    message_log += " Mất lượt!"
                    current_turn_idx = (current_turn_idx + 1) % len(clients)
                elif result == "BANKRUPT":
                    player_info["score"] = 0
                    message_log += " Mất toàn bộ điểm! Mất lượt!"
                    current_turn_idx = (current_turn_idx + 1) % len(clients)
                elif result == "NHAN DOI":
                    player_info["score"] *= 2
                    message_log += " Điểm hiện tại được nhân đôi! Tiếp tục quay hoặc đoán."
                elif result == "MAY MAN":
                    player_info["score"] += LUCKY_SPIN_POINTS
                    message_log += f" Thật may mắn! +{LUCKY_SPIN_POINTS} điểm. Tiếp tục lượt."

                next_player_info = player_data[clients[current_turn_idx][0]]
                message_log += f" Lượt của {next_player_info['name']} ({next_player_info['id']})."
                broadcast_game_state(message_log)


            elif action_type == "guess_letter":
                letter = action_data.get("letter", "").upper()
                spin_value = player_info.get("current_spin_value", 0)

                if not letter or len(letter) != 1 or not letter.isalnum():
                    message_log = f"{player_log_name}: Dữ liệu đoán chữ '{letter}' không hợp lệ. Vẫn là lượt của bạn."
                    broadcast_game_state(message_log)  # Không chuyển lượt
                    return

                found_count = 0
                new_masked_puzzle_list = list(masked_puzzle)
                phrase_to_check = current_puzzle_data["phrase"]

                already_revealed_or_guessed = False
                for i, char_in_puzzle in enumerate(phrase_to_check):
                    if char_in_puzzle.upper() == letter:
                        if new_masked_puzzle_list[i] == '_':  # Chỉ tính điểm nếu chưa được mở
                            new_masked_puzzle_list[i] = phrase_to_check[i]  # Giữ nguyên hoa thường
                            found_count += 1
                        else:  # Chữ này đã được mở trước đó rồi
                            already_revealed_or_guessed = True

                if found_count > 0:
                    masked_puzzle = "".join(new_masked_puzzle_list)
                    player_info["score"] += found_count * spin_value
                    message_log = f"{player_log_name} đoán đúng chữ '{letter}'! +{found_count * spin_value} điểm."
                    if "_" not in masked_puzzle:
                        game_over = True
                        winner_id = player_info["id"]
                        player_info["score"] += BONUS_POINTS_FOR_SOLVE  # Thưởng thêm khi hoàn thành ô chữ
                        message_log += f" Ô chữ đã được giải! {player_info['name']} ({winner_id}) chiến thắng với {player_info['score']} điểm!"
                    else:  # Vẫn còn chữ cái để đoán, tiếp tục lượt
                        message_log += f" Tiếp tục lượt của {player_log_name}."
                else:
                    if already_revealed_or_guessed:
                        message_log = f"{player_log_name}: Chữ '{letter}' đã được đoán hoặc không có. Mất lượt."
                    else:
                        message_log = f"{player_log_name} đoán chữ '{letter}' không có. Mất lượt."
                    current_turn_idx = (current_turn_idx + 1) % len(clients)

                player_info["current_spin_value"] = 0  # Reset giá trị quay sau khi đoán

                if not game_over:
                    next_player_info = player_data[clients[current_turn_idx][0]]
                    message_log += f" Lượt của {next_player_info['name']} ({next_player_info['id']})."
                broadcast_game_state(message_log)

            elif action_type == "solve_puzzle":
                attempt = action_data.get("phrase", "").upper()
                if attempt == current_puzzle_data["phrase"].upper():
                    masked_puzzle = current_puzzle_data["phrase"]
                    player_info["score"] += BONUS_POINTS_FOR_SOLVE
                    game_over = True
                    winner_id = player_info["id"]
                    message_log = f"{player_log_name} đã giải thành công ô chữ! {player_info['name']} ({winner_id}) chiến thắng với {player_info['score']} điểm!"
                else:
                    message_log = f"{player_log_name} giải ô chữ không đúng. Mất lượt."
                    current_turn_idx = (current_turn_idx + 1) % len(clients)
                    if not game_over:  # Chỉ thêm log lượt của người tiếp theo nếu game chưa kết thúc
                        next_player_info = player_data[clients[current_turn_idx][0]]
                        message_log += f" Lượt của {next_player_info['name']} ({next_player_info['id']})."

                player_info["current_spin_value"] = 0  # Reset
                broadcast_game_state(message_log)

        elif action_type == "disconnect":
            print(f"[SERVER] {player_log_name} yêu cầu ngắt kết nối.")
            # Việc remove client sẽ do client_thread xử lý khi recv trả về rỗng hoặc lỗi
            pass  # client_thread sẽ tự xử lý khi socket đóng

def client_thread(conn, addr):
    global game_started, player_data, clients

    player_id_str = "" # Sẽ là P1, P2
    with clients_lock:
        # Gán ID dạng Px cho client mới và lưu vào player_data
        player_id_str = f"P{len(clients)}" # ID dựa trên số lượng client hiện tại khi kết nối
        player_data[conn] = {"id": player_id_str, "name": player_id_str, "score": 0, "current_spin_value": 0} # Tên ban đầu là Px
    
    print(f"[NEW CONNECTION] {addr} connected as {player_id_str}.")

    try:
        # Yêu cầu client đặt tên
        initial_message = {
            "type": "request_name",
            "player_id": player_id_str, # Gửi ID dạng Px
            "message": f"Chào mừng {player_id_str}! Vui lòng đặt tên của bạn."
        }
        conn.sendall((json.dumps(initial_message) + "\n").encode('utf-8'))
        broadcast_game_state(f"{player_id_str} đã kết nối. Đang chờ đặt tên...")

    except Exception as e:
        print(f"[SERVER_ERROR] Lỗi gửi yêu cầu tên cho {addr}: {e}")
        remove_client(conn, addr)
        return

    buffer = ""
    while True:
        try:
            data_chunk = conn.recv(BUFFER_SIZE)
            if not data_chunk: # Client ngắt kết nối
                print(f"[DISCONNECTED] {player_data.get(conn, {}).get('name', addr)} (no data).")
                break
            
            buffer += data_chunk.decode('utf-8')

            while '\n' in buffer:
                message_str, buffer = buffer.split('\n', 1)
                if not message_str.strip():
                    continue
                
                action_data = json.loads(message_str)
                # print(f"[RECEIVED] Từ {player_data.get(conn, {}).get('name', addr)}: {action_data}") # Debug
                handle_client_action(conn, action_data)

        except json.JSONDecodeError:
            print(f"[ERROR] Dữ liệu JSON không hợp lệ từ {player_data.get(conn, {}).get('name', addr)}")
        except ConnectionResetError:
            print(f"[DISCONNECTED] {player_data.get(conn, {}).get('name', addr)} (reset).")
            break
        except socket.error as e: # Bắt các lỗi socket khác
            print(f"[SOCKET_ERROR] Với {player_data.get(conn, {}).get('name', addr)}: {e}")
            break
        except Exception as e:
            print(f"[ERROR] Lỗi xử lý client {player_data.get(conn, {}).get('name', addr)}: {e}, Data: '{message_str[:100]}'")
            # break # Có thể cân nhắc break hoặc không tùy mức độ lỗi
    
    remove_client(conn, addr)


def remove_client(conn_to_remove, addr_to_remove):
    global game_started, game_over, winner_id, current_turn_idx, clients, player_data

    with clients_lock:
        player_info_removed = player_data.pop(conn_to_remove, None)
        player_name_left = player_info_removed['name'] if player_info_removed else str(addr_to_remove)
        
        original_clients_list = list(clients) # Sao chép để tìm index
        idx_removed = -1
        for i, (c, a) in enumerate(original_clients_list):
            if c == conn_to_remove:
                idx_removed = i
                break
        
        # Tạo list mới không chứa client đã xóa
        new_clients_list = [(c, a) for (c, a) in clients if c != conn_to_remove]
        clients = new_clients_list # Gán lại clients

        print(f"[GAME] Người chơi {player_name_left} đã rời khỏi game.")

        if not clients: # Không còn client nào
            print("[GAME] Không còn người chơi nào. Reset game.")
            game_started = False
            game_over = True # Coi như game kết thúc
            winner_id = "Không có ai"
            return # Không cần broadcast

        if game_started and not game_over:
            if len(clients) < MAX_PLAYERS:
                game_over = True
                # Người chơi còn lại là người chiến thắng
                if clients: # Nếu vẫn còn người chơi
                    remaining_player_conn = clients[0][0]
                    winner_id = player_data[remaining_player_conn]["id"]
                    message = f"Trò chơi kết thúc do {player_name_left} thoát. {player_data[remaining_player_conn]['name']} ({winner_id}) chiến thắng!"
                else: # Trường hợp hy hữu không còn ai
                    winner_id = "Không có ai"
                    message = f"Trò chơi kết thúc do {player_name_left} thoát."
                
                print(f"[GAME] {message}")
                broadcast_game_state(message)
            else: # Vẫn đủ MAX_PLAYERS (trường hợp này ít xảy ra nếu MAX_PLAYERS > 1)
                  # hoặc còn nhiều hơn 1 người chơi và chưa đủ MAX_PLAYERS để bắt đầu lại
                if idx_removed != -1:
                    if idx_removed < current_turn_idx:
                        current_turn_idx -= 1
                    # Đảm bảo current_turn_idx nằm trong phạm vi của list client mới
                    current_turn_idx %= len(clients)

                next_player_info = player_data[clients[current_turn_idx][0]]
                broadcast_game_state(f"{player_name_left} đã thoát. Lượt của {next_player_info['name']} ({next_player_info['id']}).")
        elif not game_started and clients: # Nếu đang chờ người chơi mà có người thoát
             broadcast_game_state(f"{player_name_left} đã thoát trong khi chờ.")


def start_server():
    global game_started # Cho phép thay đổi game_started
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
    except socket.error as e:
        print(f"Lỗi bind socket: {e}. Server không thể khởi động.")
        return

    server_socket.listen(MAX_PLAYERS)
    print(f"[SERVER] Đang lắng nghe trên {SERVER_HOST}:{SERVER_PORT}")

    try:
        while True:
            # Chỉ chấp nhận kết nối mới nếu chưa đủ người chơi
            # Hoặc nếu game đã kết thúc và muốn cho phép người mới vào cho game mới (cần logic reset)
            if len(clients) < MAX_PLAYERS:
                try:
                    conn, addr = server_socket.accept()
                except OSError: # Bắt lỗi khi socket đã đóng (ví dụ server tắt)
                    print("[SERVER] Socket đã đóng. Ngừng chấp nhận kết nối.")
                    break
                
                with clients_lock:
                    clients.append((conn, addr))
                
                thread = threading.Thread(target=client_thread, args=(conn, addr))
                thread.daemon = True
                thread.start()

                # Nếu đủ người và game chưa bắt đầu, thì chờ client đặt tên xong mới initialize_game
                # Việc initialize_game sẽ được gọi từ handle_client_action("set_name")

            elif game_over and len(clients) > 0 :
                # Logic chơi lại có thể được thêm ở đây
                # Ví dụ: chờ 1 khoảng thời gian rồi reset game nếu tất cả client đồng ý chơi lại
                print("[SERVER] Game đã kết thúc. Server đang chờ.")
                # Hiện tại, để đơn giản, server sẽ không tự động bắt đầu game mới.
                # Bạn có thể thêm lệnh để admin server gõ vào để reset game.
                # Hoặc client có thể gửi action "play_again".
                # Nếu muốn server tự thoát sau 1 game:
                # print("[SERVER] Game kết thúc. Server sẽ đóng sau 10 giây.")
                # time.sleep(10)
                # break
                time.sleep(5) # Chờ, không làm gì cả

            time.sleep(0.1) # Giảm tải CPU
    
    except KeyboardInterrupt:
        print("[SERVER] Server đang tắt do KeyboardInterrupt...")
    finally:
        print("[SERVER] Server đã dừng.")
        for conn, _ in clients:
            conn.close()
        server_socket.close()


if __name__ == "__main__":
    start_server()