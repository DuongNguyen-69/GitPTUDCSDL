# server.py - Code đã sửa lỗi cú pháp và đơn giản hóa locking trong main
import socket
import threading
import random
import json # Sử dụng JSON để trao đổi dữ liệu có cấu trúc
import time # Dùng cho timeout đoán chữ
import select # Dùng để kiểm tra dữ liệu đến mà không chặn

# Danh sách câu hỏi và câu trả lời
questions = [
    {"question": "Thủ đô của Việt Nam là gì?", "answer": "hanoi"},
    {"question": "Trái cây màu đỏ, nhỏ, có vị chua ngọt là?", "answer": "strawberry"},
    {"question": "Mạng xã hội phổ biến nhất thế giới?", "answer": "facebook"},
    {"question": "Hệ điều hành mã nguồn mở nổi tiếng?", "answer": "linux"},
    {"question": "Ngôn ngữ lập trình phổ biến cho AI?", "answer": "python"},
]

HOST = ''  # Lắng nghe tất cả interface
PORT = 12345

# Cấu trúc dữ liệu lưu trữ thông tin người chơi
# Mỗi phần tử là một dictionary: {"socket": socket_obj, "name": "...", "score": 0, "errors": 0, "is_eliminated": False}
players = []
# Lịch sử trò chơi (có thể lưu các sự kiện chính)
game_history = []

current_question = {}
masked_answer = []
turn_index = 0  # Index của người chơi hiện tại trong danh sách players
wheel_options = ["MISS", "BANKRUPT", "DOUBLE", 100, 200, 300, 400, 500]
game_state = "WAITING_FOR_PLAYERS" # Các trạng thái game: WAITING_FOR_PLAYERS, PLAYING, ROUND_END, GAME_END

players_lock = threading.Lock()
game_state_lock = threading.Lock() # Lock cho trạng thái game và các biến liên quan

def send_message(client_socket, message_type, data=None):
    """Gửi thông điệp có cấu trúc (JSON) đến client"""
    message = {"type": message_type, "data": data}
    try:
        # Chuyển dictionary thành chuỗi JSON và thêm ký tự xuống dòng
        message_str = json.dumps(message, ensure_ascii=False) + "\n" # ensure_ascii=False để hiển thị tiếng Việt
        client_socket.sendall(message_str.encode('utf-8')) # Sử dụng utf-8 để mã hóa tiếng Việt
        # print(f"Sent to {client_socket.getpeername()}: {message_str.strip()}") # Log tin nhắn gửi đi (có thể gây tràn log với tiếng Việt)
    except Exception as e:
        print(f"Lỗi gửi tin nhắn {message_type} đến client: {e}")
        # Xử lý ngắt kết nối tại đây
        remove_player(client_socket)


def broadcast(message_type, data=None):
    """Gửi thông điệp có cấu trúc (JSON) đến tất cả client"""
    message = {"type": message_type, "data": data}
    message_str = json.dumps(message, ensure_ascii=False) + "\n" # ensure_ascii=False để hiển thị tiếng Việt
    with players_lock:
        # Tạo một bản sao danh sách để tránh lỗi khi xóa phần tử trong lúc lặp
        for p in players[:]:
            try:
                # Chuyển dictionary thành chuỗi JSON và thêm ký tự xuống dòng
                p["socket"].sendall(message_str.encode('utf-8')) # Sử dụng utf-8 để mã hóa tiếng Việt
                # print(f"Broadcast to {p.get('name', 'N/A')}: {message_str.strip()}") # Log tin nhắn broadcast
            except Exception as e:
                print(f"Lỗi broadcast tin nhắn {message_type} đến client {p.get('name', 'N/A')}: {e}")
                remove_player(p["socket"])

def remove_player(client_socket):
    """Xóa người chơi khỏi danh sách và xử lý khi có người chơi thoát"""
    with players_lock:
        initial_player_count = len(players)
        # Tìm người chơi bị xóa để lấy tên
        removed_player = next((p for p in players if p["socket"] == client_socket), None)
        if removed_player:
            player_name = removed_player.get('name', 'N/A')
            # Tạo danh sách mới chỉ chứa những người chơi còn lại
            players_to_keep = [p for p in players if p["socket"] != client_socket]
            players[:] = players_to_keep # Cập nhật danh sách players
            try:
                client_socket.close() # Đảm bảo socket được đóng
            except Exception as e:
                 print(f"Error closing socket for {player_name}: {e}")

            print(f"Người chơi {player_name} đã thoát.")
            broadcast("MESSAGE", f"Người chơi {player_name} đã thoát.")
            # Xử lý khi người chơi thoát ảnh hưởng đến game
            if initial_player_count >= 2 and len(players) < 2: # Nếu đang chơi mà số người chơi giảm xuống dưới 2
                 handle_game_end(f"Người chơi {player_name} đã thoát, không đủ người chơi để tiếp tục.")
            elif len(players) > 0: # Nếu vẫn còn người chơi
                 broadcast_game_state() # Cập nhật lại trạng thái game cho các client còn lại
            else: # Nếu không còn ai
                 print("All players disconnected. Server is now empty.")
                 # Server có thể quay lại trạng thái chờ người chơi ban đầu
                 global game_state
                 with game_state_lock:
                     game_state = "WAITING_FOR_PLAYERS"


def mask_answer(answer):
    """Tạo ô chữ bị che"""
    return ['_' if ch.isalpha() else ch for ch in answer.lower()] # Chuyển sang lower để so sánh, nhưng giữ nguyên masked_answer format

def get_masked_answer_string():
    """Trả về chuỗi ô chữ hiện tại"""
    # Chỉ đọc masked_answer. Masked_answer được sửa dưới game_state_lock.
    # Đọc nó ở đây không cần lock riêng nếu chắc chắn không có sửa đổi đồng thời.
    # Để an toàn hơn, nên đọc dưới game_state_lock nếu masked_answer được sửa.
    # get_masked_answer_string được gọi trong broadcast_game_state, mà broadcast_game_state lấy game_state_lock. OK.
    return ' '.join(masked_answer)

def broadcast_game_state():
     """Gửi toàn bộ trạng thái game hiện tại cho tất cả client"""
     # Hàm này cần cả game_state_lock và players_lock để đảm bảo tính nhất quán
     # Lấy game_state_lock trước, rồi players_lock
     with game_state_lock:
          with players_lock:
             current_turn_player_name = None
             # Đảm bảo turn_index hợp lệ trước khi truy cập players[turn_index]
             if players and len(players) > turn_index and not players[turn_index]["is_eliminated"]:
                 current_turn_player_name = players[turn_index]["name"]

             state_data = {
                 "game_state": game_state,
                 "question": current_question.get("question", ""),
                 "masked_answer": get_masked_answer_string(), # get_masked_answer_string được gọi từ đây, trong game_state_lock
                 "players": [{"name": p.get("name", "Chờ..."), "score": p["score"], "errors": p["errors"], "is_eliminated": p["is_eliminated"]} for p in players], # Đọc players (cần players_lock)
                 "current_turn_player": current_turn_player_name # Đọc players (cần players_lock)
             }
             # print(f"Broadcasting game state: {state_data}") # Log trạng thái game gửi đi
             broadcast("STATE", state_data) # Gọi hàm broadcast đã sửa, nó tự lấy players_lock (đang giữ)

def start_new_round():
    """Bắt đầu một vòng chơi mới"""
    global current_question, masked_answer, turn_index, game_state, questions
    with game_state_lock: # <-- Giữ game_state_lock (hàm gọi đã lấy hoặc lấy mới)
        print("Attempting to start new round...") # Log bắt đầu hàm
        # Lọc bỏ các câu hỏi đã dùng trong ván hiện tại
        # Lấy danh sách câu hỏi đã dùng trong game_history
        used_questions_in_game = [item['question'] for item in game_history if 'question' in item]
        available_questions = [q for q in questions if q['question'] not in used_questions_in_game]


        if not available_questions:
            broadcast("MESSAGE", "Không còn câu hỏi nào.") # broadcast lấy players_lock
            handle_game_end("Hết câu hỏi.") # Lấy game_state_lock
            print("No more questions, ending game.") # Log
            return

        # Chỉ bắt đầu vòng mới nếu đang ở trạng thái chờ người chơi hoặc vòng trước đã kết thúc
        if game_state != "WAITING_FOR_PLAYERS" and game_state != "ROUND_END":
             print(f"Cannot start new round. Current state: {game_state}") # Log
             return

        # Đếm số người chơi còn kết nối (cần players_lock)
        with players_lock: # <-- Lấy players_lock khi cần truy cập players
             connected_players_count = len(players)
        if connected_players_count < 2:
             print(f"Cannot start new round. Not enough connected players: {connected_players_count}") # Log
             broadcast("MESSAGE", f"Chờ thêm người chơi ({connected_players_count}/2).") # broadcast lấy players_lock
             return

        current_question = random.choice(available_questions)
        # Thêm câu hỏi đã dùng vào lịch sử để không chọn lại trong cùng một ván
        # Lưu câu hỏi vào history khi vòng mới bắt đầu
        game_history.append({"event": "new_round_question", "question": current_question['question']})

        print(f"Selected question: {current_question['question']}") # Log

        # Che ô chữ (cần game_state_lock)
        masked_answer = mask_answer(current_question['answer']) # Sửa masked_answer (cần game_state_lock)

        # Chọn người chơi bắt đầu (cần players_lock)
        with players_lock: # <-- Lấy players_lock khi cần truy cập players
             turn_index = random.randint(0, len(players) - 1) # Chọn ngẫu nhiên index trong danh sách players hiện tại

        game_state = "PLAYING"
        # Log (cần players_lock để lấy tên)
        with players_lock:
             print(f"Game state set to PLAYING. Initial turn for player index: {turn_index} ({players[turn_index].get('name', 'N/A')})")

        # Reset lỗi và trạng thái bị loại (cần players_lock)
        with players_lock: # <-- Lấy players_lock khi duyệt/sửa players
             for p in players:
                 p["errors"] = 0
                 p["is_eliminated"] = False
                 p["last_spin_points"] = 0

        broadcast("MESSAGE", "Bắt đầu vòng chơi mới!") # broadcast lấy players_lock
        broadcast_game_state() # Cần cả game_state_lock và players_lock (broadcast_game_state lấy)

        # Gửi ACTION_CHOICE cho người chơi đến lượt sau khi bắt đầu vòng chơi
        with players_lock: # Lấy players_lock để truy cập players và gửi tin nhắn
            if turn_index < len(players) and not players[turn_index]["is_eliminated"]: # Đảm bảo người chơi đến lượt hợp lệ và chưa bị loại
                 player_socket = players[turn_index]["socket"]
                 send_message(player_socket, "ACTION_CHOICE", "SPIN_OR_SOLVE") # Gửi tin nhắn ACTION_CHOICE
                 print(f"Sent ACTION_CHOICE SPIN_OR_SOLVE to {players[turn_index].get('name', 'N/A')}")


def handle_spin_result(player_index, result):
    """Xử lý kết quả quay nón"""
    with game_state_lock: # Lock khi xử lý kết quả quay ảnh hưởng đến trạng thái game/người chơi
        with players_lock: # Lấy players_lock khi cần truy cập players
             if player_index >= len(players) or players[player_index]["is_eliminated"]:
                  print(f"Attempted to handle spin for eliminated or invalid player index: {player_index}")
                  broadcast_game_state()
                  return
             player = players[player_index] # Truy cập players (cần players_lock)

        broadcast("SPIN_RESULT", str(result)) # broadcast lấy players_lock
        broadcast("MESSAGE", f"{player['name']} quay nón và được: {result}") # broadcast lấy players_lock
        game_history.append({"event": "spin", "player": player["name"], "result": result})
        print(f"Spin result for {player['name']}: {result}") # Log

        if result == "MISS":
            broadcast("MESSAGE", f"Kết quả quay là MISS! {player['name']} mất lượt.") # broadcast lấy players_lock
            with players_lock: player["errors"] += 1 # Cần players_lock khi sửa players
            print(f"{player['name']} errors: {player['errors']}")
            broadcast_game_state() # Lấy game_state_lock và players_lock
            check_elimination(player_index) # Lấy game_state_lock và players_lock
            next_turn() # Lấy game_state_lock và players_lock
        elif result == "BANKRUPT":
            with players_lock: player["score"] = 0 # Cần players_lock khi sửa players
            broadcast("MESSAGE", f"Kết quả quay là BANKRUPT! {player['name']} phá sản, điểm về 0.") # broadcast lấy players_lock
            print(f"{player['name']} score after BANKRUPT: {player['score']}")
            broadcast_game_state() # Lấy game_state_lock và players_lock
            next_turn() # Lấy game_state_lock và players_lock
        elif result == "DOUBLE":
            with players_lock: player["score"] *= 2 # Cần players_lock khi sửa players
            broadcast("MESSAGE", f"Kết quả quay là DOUBLE! {player['name']} nhân đôi điểm: {player['score']}") # broadcast lấy players_lock
            print(f"{player['name']} score after DOUBLE: {player['score']}")
            broadcast_game_state() # Lấy game_state_lock và players_lock
            send_message(player["socket"], "ACTION_CHOICE", "SPIN_OR_SOLVE")
            print(f"Sent ACTION_CHOICE SPIN_OR_SOLVE to {player['name']}")

        else: # Ô điểm (integer value)
            point_value = int(result)
            with players_lock: players[player_index]["last_spin_points"] = point_value # Cần players_lock khi sửa players
            print(f"{player['name']} spun {point_value} points. Waiting for guess.")
            broadcast("MESSAGE", f"Bạn quay được {point_value} điểm. Hãy đoán một chữ cái hoặc giải ô chữ.") # broadcast lấy players_lock
            send_message(player["socket"], "ACTION_CHOICE", "GUESS_LETTER_OR_SOLVE")
            print(f"Sent ACTION_CHOICE GUESS_LETTER_OR_SOLVE to {player['name']}")


def handle_guess_letter(player_index, letter):
    """Xử lý khi người chơi đoán một chữ cái"""
    with game_state_lock: # Lock khi xử lý đoán chữ
        with players_lock: # Lấy players_lock khi cần truy cập players
            if player_index >= len(players) or players[player_index]["is_eliminated"]:
                 print(f"Attempted to handle guess letter for eliminated or invalid player index: {player_index}")
                 broadcast_game_state()
                 return
            player = players[player_index] # Truy cập players (cần players_lock)
            ans = current_question['answer'].lower() # Truy cập current_question (cần game_state_lock)
            letter = letter.lower()
            count = ans.count(letter)
    game_history.append({"event": "guess_letter", "player": player["name"], "letter": letter, "count": count})
    print(f"{player['name']} guessed letter: {letter}, count: {count}") # Log

    with players_lock: point_value = player.get("last_spin_points", 0) # Cần players_lock
    with players_lock: player["last_spin_points"] = 0 # Reset điểm quay (cần players_lock)


    if letter in get_masked_answer_string().lower().replace(" ", ""):
        broadcast("MESSAGE", f"Chữ '{letter.upper()}' đã xuất hiện rồi, {player['name']} mất lượt.") # broadcast lấy players_lock
        with players_lock: player["errors"] += 1 # Cần players_lock khi sửa players
        print(f"{player['name']} errors: {player['errors']} (letter already revealed)")
        broadcast_game_state() # Lấy game_state_lock và players_lock
        check_elimination(player_index) # Lấy game_state_lock và players_lock
        next_turn() # Lấy game_state_lock và players_lock

    elif count > 0:
        broadcast("MESSAGE", f"Có {count} chữ '{letter.upper()}'.") # broadcast lấy players_lock
        # Cập nhật ô chữ (cần game_state_lock và players_lock vì sửa masked_answer là biến dùng chung)
        with game_state_lock: # Lấy game_state_lock trước
             with players_lock: # Rồi lấy players_lock
                 updated = False
                 ans_list = list(ans) # Chuyển đáp án lower sang list để duyệt
                 for i, ch in enumerate(ans_list):
                     if ch == letter and masked_answer[i] == '_': # Chỉ cập nhật nếu chưa mở
                         masked_answer[i] = current_question['answer'][i] # Giữ nguyên chữ hoa/thường từ đáp án gốc
                         updated = True
        print(f"Masked answer updated: {''.join(masked_answer)}") # Log

        # Cộng điểm (cần players_lock)
        if updated and point_value > 0:
             with players_lock: player["score"] += point_value * count # Cần players_lock
             broadcast("MESSAGE", f"{player['name']} được cộng {point_value * count} điểm.") # broadcast lấy players_lock
             print(f"{player['name']} score after correct guess: {player['score']}") # Log

        # Reset lỗi (cần players_lock)
        with players_lock: player["errors"] = 0 # Cần players_lock
        broadcast("MESSAGE", f"Lỗi của {player['name']} được reset.") # broadcast lấy players_lock
        print(f"{player['name']} errors reset.") # Log

        broadcast_game_state() # Lấy game_state_lock và players_lock

        if '_' not in get_masked_answer_string().replace(" ", ""):
             broadcast("MESSAGE", "Ô chữ đã mở hết! Vui lòng giải ô chữ.") # broadcast lấy players_lock
             send_message(player["socket"], "ACTION_CHOICE", "SOLVE_MANDATORY")
             print("Puzzle fully revealed, requesting mandatory solve.") # Log
        else:
            send_message(player["socket"], "ACTION_CHOICE", "SPIN_OR_SOLVE")
            print(f"Sent ACTION_CHOICE SPIN_OR_SOLVE to {player['name']}")

    else:
        broadcast("MESSAGE", f"Không có chữ '{letter.upper()}'.") # broadcast lấy players_lock
        with players_lock: player["errors"] += 1 # Cần players_lock khi sửa players
        print(f"{player['name']} errors: {player['errors']} (wrong letter)")
        broadcast_game_state() # Lấy game_state_lock và players_lock
        check_elimination(player_index) # Lấy game_state_lock và players_lock
        next_turn() # Lấy game_state_lock và players_lock


def handle_guess_word(player_index, word):
    """Xử lý khi người chơi đoán cả từ"""
    with game_state_lock: # Lock khi xử lý đoán từ
         with players_lock: # Rồi lấy players_lock
            if player_index >= len(players) or players[player_index]["is_eliminated"]:
                 print(f"Attempted to handle guess word for eliminated or invalid player index: {player_index}")
                 broadcast_game_state() # Lấy game_state_lock và players_lock
                 return
            player = players[player_index] # Truy cập players (cần players_lock)
            ans = current_question['answer'].lower() # Truy cập current_question (cần game_state_lock)
            word = word.lower()
    game_history.append({"event": "guess_word", "player": player["name"], "word": word})
    print(f"{player['name']} guessed word: {word}") # Log

    with players_lock: player["last_spin_points"] = 0 # Reset điểm quay (cần players_lock)

    if word == ans:
       broadcast("MESSAGE", f"{player['name']} đoán đúng ô chữ: {current_question['answer']}") # broadcast lấy players_lock
       with players_lock: player["score"] += 1000 # Cộng điểm thưởng (cần players_lock)
       broadcast("MESSAGE", f"{player['name']} được cộng 1000 điểm thưởng khi giải đúng.") # broadcast lấy players_lock
       print(f"{player['name']} score after correct word guess: {player['score']}")
       broadcast_game_state() # Lấy game_state_lock và players_lock
       handle_round_end(f"{player['name']} đã giải đúng ô chữ.") # Lấy game_state_lock

    else:
       broadcast("MESSAGE", f"{player['name']} đoán sai ô chữ: {word}") # broadcast lấy players_lock
       with players_lock: player["errors"] += 1 # Cần players_lock
       print(f"{player['name']} errors: {player['errors']} (wrong word)")
       broadcast_game_state() # Lấy game_state_lock và players_lock
       check_elimination(player_index) # Lấy game_state_lock và players_lock
       next_turn() # Lấy game_state_lock và players_lock


def check_elimination(player_index):
    """Kiểm tra và xử lý khi người chơi bị loại do quá 3 lỗi liên tục"""
    with game_state_lock: # Lock khi kiểm tra loại người chơi
        with players_lock: # Lấy players_lock khi cần truy cập players
            if player_index >= len(players):
                 print(f"Attempted to check elimination for invalid player index: {player_index}")
                 return
            player = players[player_index]
            if player["errors"] >= 3 and not player["is_eliminated"]:
                player["is_eliminated"] = True
                # Mất hết điểm của vòng đó khi bị loại (hiện tại không trừ điểm tổng)

        if player["errors"] >= 3 and not player["is_eliminated"]: # Kiểm tra lại điều kiện sau khi nhả players_lock (có thể trạng thái thay đổi)
             broadcast("MESSAGE", f"{player.get('name', 'N/A')} đã bị loại khỏi vòng chơi do 3 lỗi liên tục!") # broadcast lấy players_lock
             print(f"{player.get('name', 'N/A')} eliminated.")
             broadcast_game_state() # Lấy game_state_lock và players_lock
             game_history.append({"event": "eliminated", "player": player.get('name', 'N/A')})
             check_round_end_condition() # Lấy game_state_lock và players_lock


def check_round_end_condition():
    """Kiểm tra xem vòng đấu đã kết thúc chưa (tất cả người chơi còn hoạt động bị loại hoặc ô chữ đã giải)"""
    with game_state_lock: # Lock khi kiểm tra điều kiện kết thúc vòng
        if game_state != "PLAYING":
            print(f"Cannot check round end condition. Game state is {game_state}")
            return False

        with players_lock: # Lấy players_lock để đọc danh sách players
             active_players = [p for p in players if not p["is_eliminated"]]
             print(f"Checking round end condition. Active players: {len(active_players)} / {len(players)}") # Log

        if not active_players and len(players) > 0:
            broadcast("MESSAGE", "Tất cả người chơi đã bị loại khỏi vòng chơi.") # broadcast lấy players_lock
            handle_round_end("Tất cả người chơi bị loại.") # Lấy game_state_lock
            print("All active players eliminated, ending round.") # Log
            return True

        return False


def handle_round_end(reason):
    """Kết thúc vòng chơi"""
    global game_state, masked_answer
    with game_state_lock: # <-- Giữ game_state_lock (hàm gọi đã lấy hoặc lấy mới)
        if game_state == "ROUND_END": # Tránh gọi đúp nếu đã ở trạng thái ROUND_END
            return

        game_state = "ROUND_END"
        # Mở toàn bộ ô chữ khi kết thúc vòng
        if current_question:
            masked_answer = list(current_question['answer'])
            # broadcast("MESSAGE", f"Ô chữ đã mở hoàn chỉnh: {' '.join(masked_answer)}") # broadcast lấy players_lock - sẽ broadcast trong broadcast_game_state

        broadcast_game_state() # Gửi trạng thái cuối vòng (lấy cả 2 lock)

        broadcast("MESSAGE", f"Vòng chơi kết thúc: {reason}") # broadcast lấy players_lock
        game_history.append({"event": "round_end", "reason": reason})
        print(f"Round ended: {reason}") # Log

        # Kiểm tra điều kiện kết thúc game (hết câu hỏi)
        used_questions_in_game = [item['question'] for item in game_history if 'question' in item]
        remaining_questions = [q for q in questions if q['question'] not in used_questions_in_game]

        if not remaining_questions:
             handle_game_end("Đã hết câu hỏi cho ván chơi này.") # Lấy game_state_lock
        else:
             # Nếu còn câu hỏi, chuẩn bị cho vòng mới sau một khoảng thời gian
             broadcast("MESSAGE", "Chuẩn bị cho vòng chơi tiếp theo...") # broadcast lấy players_lock
             print("Starting new round timer...") # Log
             # Hủy bỏ các Timer cũ trước khi tạo Timer mới để tránh tích tụ
             # Tạm thời không quản lý Timer phức tạp, chỉ tạo mới
             threading.Timer(5, start_new_round).start() # start_new_round lấy game_state_lock


def handle_game_end(reason):
    """Kết thúc toàn bộ trò chơi"""
    global game_state
    with game_state_lock: # <-- Giữ game_state_lock (hàm gọi đã lấy hoặc lấy mới)
        if game_state == "GAME_END": # Tránh gọi đúp
            return

        game_state = "GAME_END"
        broadcast("STATE:GAME_END", reason) # broadcast lấy players_lock
        broadcast("MESSAGE", "Trò chơi kết thúc!") # broadcast lấy players_lock
        broadcast("MESSAGE", "Kết quả cuối cùng:") # broadcast lấy players_lock
        # Sắp xếp người chơi theo điểm để xác định người thắng (cần players_lock)
        with players_lock: # Lấy players_lock để đọc players
             sorted_players = sorted(players, key=lambda p: p.get("score", 0), reverse=True)
             for i, p in enumerate(sorted_players):
                 broadcast("MESSAGE", f"{i+1}. {p.get('name', 'N/A')}: {p.get('score', 0)} điểm") # broadcast lấy players_lock

        game_history.append({"event": "game_end", "reason": reason, "final_scores": [{"name": p.get("name", "N/A"), "score": p.get("score", 0)} for p in sorted_players]})
        print(f"Game ended: {reason}") # Log

# (Hàm shutdown_server không có trong code gốc, giữ nguyên)


def next_turn():
    """Chuyển sang lượt chơi của người chơi tiếp theo còn hoạt động"""
    global turn_index # <-- Khai báo global ở đầu hàm
    with game_state_lock: # Lock khi chuyển lượt
        if game_state != "PLAYING":
            print(f"Cannot proceed to next turn. Game state is {game_state}") # Log
            return

        with players_lock: # Lấy players_lock khi truy cập players
             # Tìm người chơi tiếp theo chưa bị loại
             start_index = turn_index # <-- Sử dụng sau khai báo global
             print(f"Current turn index: {start_index}") # Log

             active_player_indices = [i for i, p in enumerate(players) if not p["is_eliminated"]]

             if not active_player_indices:
                  print("No active players left. Checking round end condition.")
                  # check_round_end_condition() # Gọi check_round_end_condition sau khi nhả locks
                  pass # Logic kết thúc vòng khi hết người chơi sẽ được check ở check_elimination hoặc nơi khác

             else:
                 # Tìm index của người chơi hiện tại trong danh sách active_player_indices
                 try:
                     current_active_index_in_list = active_player_indices.index(start_index)
                 except ValueError: # Người chơi hiện tại đã bị loại, tìm người đầu tiên trong danh sách hoạt động
                      current_active_index_in_list = -1 # Sẽ tăng lên 0 ở bước tiếp theo

                 # Tìm index của người chơi tiếp theo trong danh sách active_player_indices
                 next_active_index_in_list = (current_active_index_in_list + 1) % len(active_player_indices)
                 turn_index = active_player_indices[next_active_index_in_list] # <-- Gán sau khai báo global

             if active_player_indices: # Chỉ broadcast lượt chơi nếu còn người hoạt động
                 broadcast("MESSAGE", f"Đến lượt của {players[turn_index]['name']}") # broadcast lấy players_lock
                 print(f"Next turn for player index: {turn_index} ({players[turn_index].get('name', 'N/A')})") # Log (cần players_lock để lấy tên)

        # Gửi ACTION_CHOICE cho người chơi đến lượt
        if active_players and turn_index < len(players): # Đảm bảo còn người chơi hoạt động và turn_index hợp lệ
            player_socket = players[turn_index]["socket"]
            send_message(player_socket, "ACTION_CHOICE", "SPIN_OR_SOLVE") # Gửi tin nhắn ACTION_CHOICE cho người đến lượt
            print(f"Sent ACTION_CHOICE SPIN_OR_SOLVE to {players[turn_index].get('name', 'N/A')}")

        if active_players: # Chỉ broadcast state nếu còn người hoạt động
            broadcast_game_state() # Lấy game_state_lock và players_lock
        else: # Nếu hết người hoạt động, check kết thúc vòng
             check_round_end_condition() # Lấy game_state_lock và players_lock


def client_thread(c, player_index):
    """Luồng xử lý riêng cho mỗi client"""
    # Biến để theo dõi thời gian bắt đầu lượt đoán (cho timeout 5 giây)
    guess_start_time = None
    # Biến để lưu trạng thái chờ input (GUESS_LETTER_OR_SOLVE, SPIN_OR_SOLVE)
    waiting_for_action_choice = None

    # Sử dụng tên tạm thời cho log ban đầu
    player_name_for_log = f"Người chơi {player_index+1}"

    try:
        print(f"Client thread started for player index {player_index} ({player_name_for_log})") # Log start of thread

        # Chờ nhận tên từ client (tin nhắn JSON {"type": "NAME", "data": "..."})
        send_message(c, "REQUEST_NAME")
        # Sử dụng select để chờ dữ liệu đến với timeout
        NAME_INPUT_TIMEOUT = 30
        print(f"Waiting for name from player index {player_index} ({player_name_for_log}) for {NAME_INPUT_TIMEOUT} seconds.") # Log
        ready_to_read, _, _ = select.select([c], [], [], NAME_INPUT_TIMEOUT)

        if not ready_to_read:
             send_message(c, "MESSAGE", f"Hết thời gian nhập tên ({NAME_INPUT_TIMEOUT}s), kết nối sẽ đóng.")
             print(f"Player index {player_index} ({player_name_for_log}) timed out waiting for name.")
             return # Kết thúc luồng nếu hết thời gian

        data = b""
        while True:
             try:
                  chunk = c.recv(4096)
                  if not chunk:
                       print(f"Client {player_name_for_log} disconnected while waiting for name.")
                       return
                  data += chunk
                  if b"\n" in data:
                       line, buffer = data.split(b"\n", 1)
                       data = line
                       break
             except Exception as e:
                  print(f"Error receiving name data from {player_name_for_log}: {e}")
                  return

        data_str = data.decode('utf-8').strip()

        if not data_str:
             print(f"Client {player_name_for_log} sent empty data after timeout.")
             send_message(c, "MESSAGE", "Đã nhận dữ liệu rỗng khi chờ tên.")
             return

        try:
            message = json.loads(data_str)
            if message.get("type") == "NAME" and isinstance(message.get("data"), str):
                name = message["data"].strip()
                if not name:
                     send_message(c, "MESSAGE", "Tên không được để trống.")
                     print(f"Player index {player_index} ({player_name_for_log}) sent empty name.")
                     return
            else:
                 send_message(c, "MESSAGE", "Sai định dạng tin nhắn tên.")
                 print(f"Player index {player_index} ({player_name_for_log}) sent invalid name message type: {message.get('type')}")
                 return
        except json.JSONDecodeError:
            send_message(c, "MESSAGE", "Không nhận được tin nhắn tên hợp lệ (không phải JSON).")
            print(f"Player index {player_index} ({player_name_for_log}) sent non-JSON name message: {data_str}")
            return
        except Exception as e:
             print(f"Error parsing name message from {player_name_for_log}: {e}")
             send_message(c, "MESSAGE", f"Lỗi xử lý tên của bạn: {e}")
             return

        # --- Xử lý nhận tên và kiểm tra/bắt đầu game theo giải pháp của bạn ---
        start_round = False
        player_name_for_log = name # Cập nhật tên dùng cho log ngay sau khi có tên thật

        with players_lock: # Lấy players_lock
            # Cập nhật tên vào cấu trúc players
            if player_index >= len(players) or players[player_index]["socket"] != c:
                 print(f"Player index {player_index} no longer valid for socket {c.getpeername()} when setting name. Disconnecting.")
                 send_message(c, "MESSAGE", "Có lỗi xảy ra khi đăng ký tên, vui lòng thử lại.")
                 return

            players[player_index]["name"] = name
            print(f"Player index {player_index} name set to: {name}") # Log
            broadcast("MESSAGE", f"{name} đã tham gia trò chơi.") # broadcast lấy players_lock (đang giữ)

            # Kiểm tra nếu đủ 2 người chơi
            if len(players) == 2:
                start_round = True # Set cờ để kiểm tra trạng thái game sau khi thoát players_lock

        # players_lock released here. Main thread can now acquire it.

        # Kiểm tra cờ và trạng thái game dưới game_state_lock để bắt đầu game
        game_did_start = False # Cờ để theo dõi xem game có bắt đầu từ đây không
        if start_round: # Chỉ vào đây nếu có đủ 2 người chơi khi players_lock được giữ
            with game_state_lock: # Lấy game_state_lock
                if game_state == "WAITING_FOR_PLAYERS":
                    print("Two players joined and game is waiting. Starting new round.") # Log
                    start_new_round() # start_new_round lấy game_state_lock (đang giữ) và players_lock (qua broadcast)
                    game_did_start = True # Đặt cờ là True vì game đã bắt đầu
                else:
                     print(f"Player count was 2 but game state is {game_state}. Not starting game from here.")

        # game_state_lock released here (if acquired).

        # Broadcast trạng thái game cập nhật (với tên mới).
        # Chỉ broadcast state nếu game KHÔNG chuyển sang PLAYING ngay lập tức (game_did_start False)
        # start_new_round đã broadcast state PLAYING.
        if not game_did_start:
             broadcast_game_state() # broadcast_game_state lấy game_state_lock và players_lock


        # --- Kết thúc xử lý nhận tên và kiểm tra/bắt đầu game ---


        # Vòng lặp nhận tin nhắn ACTION từ client trong suốt quá trình chơi
        buffer = b""
        while True:
            timeout = 0.1

            # Kiểm tra timeout hành động (cần game_state_lock và players_lock)
            # Chỉ thực hiện timeout nếu đến lượt mình và đang chờ hành động cụ thể
            is_my_turn_and_waiting = False
            current_game_state_local = None # Biến local để đọc game_state an toàn

            with game_state_lock: # Lấy game_state_lock trước
                 current_game_state_local = game_state
                 if current_game_state_local == "PLAYING": # Chỉ kiểm tra lượt nếu game đang chơi
                     with players_lock: # Lấy players_lock
                         if player_index < len(players) and players[player_index]["socket"] == c:
                             if turn_index < len(players):
                                 is_my_turn_and_waiting = (players[turn_index]["socket"] == c and waiting_for_action_choice is not None)


            if is_my_turn_and_waiting:
                 ACTION_TIMEOUT = 15 # Thời gian chờ hành động/đoán
                 if guess_start_time is not None:
                      elapsed = time.time() - guess_start_time
                      timeout = max(0.1, ACTION_TIMEOUT - elapsed) # Thời gian chờ còn lại, tối thiểu 0.1s
                      if timeout <= 0.1: # Nếu hết thời gian
                           print(f"Người chơi {player_name_for_log} hết thời gian cho hành động {waiting_for_action_choice}.")
                           broadcast("MESSAGE", f"{player_name_for_log} hết thời gian. Mất lượt.") # broadcast lấy players_lock
                           with players_lock: players[player_index]["errors"] += 1 # Cần players_lock
                           broadcast_game_state() # Lấy game_state_lock và players_lock
                           check_elimination(player_index) # Lấy game_state_lock và players_lock
                           waiting_for_action_choice = None # Reset trạng thái chờ
                           guess_start_time = None
                           next_turn() # Lấy game_state_lock và players_lock
                           continue # Bỏ qua phần xử lý data trong vòng lặp này


            # Sử dụng select để chờ dữ liệu hoặc timeout
            try:
                ready_to_read, _, _ = select.select([c], [], [], timeout)
            except ValueError:
                 print(f"Select error for client {player_name_for_log}. Disconnecting.")
                 break

            if ready_to_read:
                try:
                    chunk = c.recv(4096)
                    if not chunk:
                        print(f"Client {player_name_for_log} disconnected during game.")
                        break
                    buffer += chunk

                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        data_str = line.decode('utf-8').strip()
                        print(f"Received from {player_name_for_log}: {data_str}")

                        if not data_str: continue

                        try:
                            message = json.loads(data_str)
                            msg_type = message.get("type")
                            msg_data = message.get("data")

                            # Xử lý tin nhắn ACTION từ client
                            if msg_type == "ACTION":
                                action_parts = msg_data.split(":", 1)
                                action_type = action_parts[0]
                                action_value = action_parts[1] if len(action_parts) > 1 else None

                                # Cần game_state_lock và players_lock để kiểm tra điều kiện thực hiện action và sửa state/players
                                with game_state_lock:
                                     with players_lock:
                                        # Kiểm tra xem có đúng lượt của người chơi này không và game đang PLAYING
                                        is_players_list_valid = (player_index < len(players) and players[player_index]["socket"] == c)
                                        is_my_turn = (turn_index < len(players) and players[turn_index]["socket"] == c)
                                        current_game_state_local_action = game_state # Đọc game_state dưới lock

                                     if not is_players_list_valid or current_game_state_local_action != "PLAYING" or not is_my_turn:
                                          if is_players_list_valid and current_game_state_local_action == "PLAYING":
                                               send_message(c, "MESSAGE", "Chưa đến lượt của bạn.")
                                          elif is_players_list_valid:
                                               send_message(c, "MESSAGE", f"Không thể thực hiện hành động lúc này. Trạng thái game: {current_game_state_local_action}")

                                          print(f"Received {action_type} from {player_name_for_log} but conditions not met.")
                                          continue

                                     # Kiểm tra hành động có hợp lệ với trạng thái chờ hiện tại không
                                     is_valid_action_for_choice = False
                                     # Cần game_state_lock để đọc waiting_for_action_choice an toàn
                                     # waiting_for_action_choice được sửa trong cùng khối game_state_lock này, nên đọc ở đây là an toàn.
                                     if action_type == "SPIN" and (waiting_for_action_choice == "SPIN_OR_SOLVE"): # Chỉ cho phép SPIN khi server yêu cầu SPIN_OR_SOLVE
                                          is_valid_action_for_choice = True
                                     elif action_type in ["GUESS_LETTER"] and waiting_for_action_choice in ["GUESS_LETTER_OR_SOLVE"]: # Chỉ đoán chữ khi server yêu cầu GUESS_LETTER_OR_SOLVE
                                          is_valid_action_for_choice = True
                                     elif action_type in ["GUESS_WORD", "SOLVE"] and waiting_for_action_choice in ["GUESS_LETTER_OR_SOLVE", "SPIN_OR_SOLVE", "SOLVE_MANDATORY"]: # Đoán từ/Giải khi server cho phép
                                          is_valid_action_for_choice = True


                                     if not is_valid_action_for_choice:
                                          send_message(c, "MESSAGE", f"Hành động {action_type} không hợp lệ vào lúc này. Bạn đang chờ: {waiting_for_action_choice}")
                                          print(f"Received invalid action {action_type} from {player_name_for_log}. Waiting for {waiting_for_action_choice}")
                                          # Gửi lại ACTION_CHOICE hiện tại để client biết nó nên làm gì
                                          send_message(c, "ACTION_CHOICE", waiting_for_action_choice)
                                          continue


                                     # Xử lý hành động hợp lệ (gọi các hàm handle_...)
                                     # Reset trạng thái chờ và timeout trước khi gọi hàm xử lý hành động
                                     waiting_for_action_choice = None
                                     guess_start_time = None

                                     if action_type == "SPIN":
                                         print(f"Processing SPIN action from {player_name_for_log}")
                                         result = random.choice(wheel_options)
                                         handle_spin_result(player_index, result) # Lấy game_state_lock và players_lock bên trong

                                     elif action_type == "GUESS_LETTER":
                                         print(f"Processing GUESS_LETTER action from {player_name_for_log} with value {action_value}")
                                         if action_value and len(action_value) == 1 and action_value.isalpha():
                                             handle_guess_letter(player_index, action_value) # Lấy game_state_lock và players_lock bên trong
                                         else:
                                             send_message(c, "MESSAGE", "Định dạng đoán chữ cái không hợp lệ. Chỉ gửi 1 chữ cái.")
                                             print(f"Invalid letter guess format from {player_name_for_log}: {action_value}")
                                             # Nếu đoán sai định dạng, gửi lại ACTION_CHOICE ban đầu
                                             send_message(c, "ACTION_CHOICE", waiting_for_action_choice)


                                     elif action_type == "GUESS_WORD" or action_type == "SOLVE":
                                          action_name = "GUESS_WORD" if action_type == "GUESS_WORD" else "SOLVE"
                                          print(f"Processing {action_name} action from {player_name_for_log} with value {action_value}")
                                          if action_value:
                                              # Server sẽ kiểm tra xem guess_word/solve có đúng không trong handle_guess_word
                                              handle_guess_word(player_index, action_value) # Lấy game_state_lock và players_lock bên trong
                                              # Sau khi đoán từ/giải, nếu không kết thúc vòng, lượt sẽ chuyển
                                          else:
                                              send_message(c, "MESSAGE", f"Thiếu từ cần {action_name.lower()}.")
                                              print(f"Missing {action_name.lower()} value from {player_name_for_log}.")
                                              # Nếu thiếu giá trị, gửi lại ACTION_CHOICE ban đầu
                                              # Xác định ACTION_CHOICE ban đầu dựa vào waiting_for_action_choice
                                              send_message(c, "ACTION_CHOICE", waiting_for_action_choice)


                            # Client không nên gửi ACTION_CHOICE hoặc STATE, server mới gửi.
                            # Bỏ qua nếu nhận được từ client.
                            elif msg_type in ["ACTION_CHOICE", "STATE"]:
                                 print(f"Received unexpected message type {msg_type} from client {player_name_for_log}. Ignoring.")


                        except json.JSONDecodeError:
                            print(f"Received non-JSON message from {player_name_for_log}: {data_str}")
                            send_message(c, "MESSAGE", "Server nhận được tin nhắn không hợp lệ (không phải JSON).")
                        except Exception as e:
                            print(f"Lỗi xử lý tin nhắn ACTION từ {player_name_for_log}: {e}")
                            send_message(c, "MESSAGE", f"Lỗi xử lý hành động của bạn: {e}")

                except Exception as e:
                     print(f"Error receiving data from {player_name_for_log}: {e}")
                     break # Thoát vòng lặp nhận dữ liệu nếu có lỗi socket khác


    except Exception as e:
        # Xử lý các lỗi không mong muốn trong luồng client trước khi nó kết thúc
        print(f"Lỗi không xác định trong client thread cho người chơi {player_name_for_log}: {e}")
        # send_message(c, "MESSAGE", f"Đã xảy ra lỗi nghiêm trọng, kết nối sẽ đóng: {e}") # Không thể gửi vì socket có thể đã invalid
        pass # Luồng sẽ kết thúc và cuối cùng remove_player sẽ được gọi


    finally:
        # Khối finally này sẽ chạy khi client_thread kết thúc (do return, break, hoặc exception không được bắt)
        print(f"Client thread finishing for player index {player_index} ({player_name_for_log}).") # Log
        # remove_player cần lấy players_lock. Gọi remove_player để dọn dẹp ở phía server.
        # remove_player(c) # remove_player sẽ đóng socket và xóa khỏi danh sách players.
        # Remove player sẽ được gọi tự động khi socket bị đóng và nhận data rỗng ở recv loop
        # hoặc khi có lỗi gửi tin nhắn trong send_message/broadcast.


def main():
    global srv
    global game_state

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Cho phép tái sử dụng địa chỉ
    try:
        srv.bind((HOST, PORT))
        srv.listen(2) # Chỉ cho phép 2 kết nối đồng thời cho 2 người chơi
        print(f"Server chạy {HOST or '0.0.0.0'}:{PORT}")
    except Exception as e:
        print(f"Không thể khởi động server: {e}")
        return

    players.clear()
    game_history.clear()
    print("Players list and game history cleared on server startup.")

    with game_state_lock:
        game_state = "WAITING_FOR_PLAYERS"
        print(f"Initial game state set to: {game_state}")

    while True:
        try:
            # Sử dụng select với một small timeout để tránh vòng lặp chặn hoàn toàn
            ready_to_read, _, _ = select.select([srv], [], [], 0.1)

            if ready_to_read: # Nếu socket server sẵn sàng chấp nhận kết nối
                 # Chấp nhận kết nối trước
                 try:
                     c, addr = srv.accept()
                     print(f"Client kết nối từ {addr}")
                 except Exception as e:
                     print(f"Lỗi chấp nhận kết nối từ {addr}: {e}")
                     continue # Bỏ qua kết nối lỗi và tiếp tục vòng lặp

                 # Sau khi chấp nhận thành công, lấy lock để kiểm tra số lượng và thêm người chơi
                 print(f"Attempting to acquire players_lock for adding new player from main thread...")
                 with players_lock: # <-- Lấy players_lock ở đây CHỈ MỘT LẦN
                      print("players_lock acquired by main thread.")
                      # Kiểm tra số lượng người chơi *dưới lock* trước khi thêm
                      if len(players) < 2:
                          player_id = len(players)
                          print(f"Main thread calculated player_id: {player_id}")
                          players.append({"socket": c, "name": f"Người chơi {player_id+1}", "score": 0, "errors": 0, "is_eliminated": False, "last_spin_points": 0})
                          print(f"Main thread appended player {player_id+1}. Players list length now: {len(players)}")
                          print(f"Đã thêm Người chơi {player_id+1}. Tổng số người chơi: {len(players)}")
                          print(f"Main thread attempting to start client thread for index {player_id}...")
                          # Khởi động luồng xử lý cho client này
                          thread = threading.Thread(target=client_thread, args=(c, player_id), daemon=True)
                          thread.start()
                          print(f"Main thread started client thread for index {player_id}.")
                          print("players_lock released by main thread (player added).") # Log nhả lock
                      else:
                           # Nếu server đã đủ 2 người, đóng kết nối mới
                           print(f"Server already has 2 players. Closing connection from {addr}.")
                           # Gửi tin nhắn thông báo cho client trước khi đóng
                           try:
                               send_message(c, "MESSAGE", "Server đã đủ người chơi. Vui lòng thử lại sau.")
                           except:
                               pass # Bỏ qua nếu không gửi được
                           try:
                               c.close() # Đóng socket của client mới
                           except:
                               pass
                           print("players_lock released by main thread (connection rejected).") # Log nhả lock

                 # players_lock được giải phóng ở đây.

        except Exception as e:
            print(f"Lỗi trong vòng lặp chính server (ngoài accept): {e}")


if __name__ == '__main__':
    main()