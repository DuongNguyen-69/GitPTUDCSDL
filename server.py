import os
import socket
import threading
import random
import json
from datetime import datetime

SAVE_FILE = "savegame.json"

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
game_ended = False

def broadcast(message):
    with clients_lock:
        for c in clients[:]:
            try:
                c.sendall(message.encode())
            except (ConnectionResetError, BrokenPipeError, OSError) as e:
                # Handle "not a socket" error (10038) and other socket errors
                if isinstance(e, OSError) and e.winerror != 10038:
                    print(f"Socket error: {e}")
                if c in clients:
                    clients.remove(c)
                try:
                    c.close()
                except:
                    pass

def mask_answer(answer):
    return ['_' if ch.isalpha() else ch for ch in answer]

def send_question():
    global current_question, masked_answer
    current_question = random.choice(questions)
    masked_answer = mask_answer(current_question['answer'])
    broadcast(f"\nCâu hỏi: {current_question['question']}")
    broadcast(f"Từ khóa: {' '.join(masked_answer)}")
    save_game_state()

def update_turn():
    global turn

    # Validate turn before accessing names list
    if turn >= len(names):
        print(f"Invalid turn: {turn}, names length: {len(names)}")
        return

    current_player = names[turn]
    broadcast(f"\nĐến lượt {current_player}!")
    save_game_state()

def log_history(player_name, action, guess, result, score):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("lichsu_game.txt", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {player_name} {action}: '{guess}' - {result} (Điểm: {score})\n")

def load_leaderboard():
    leaderboard = []
    try:
        with open("bangxephang.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        name = parts[0].strip()
                        try:
                            score = int(parts[1].strip())
                            leaderboard.append((name, score))
                        except ValueError:
                            pass
    except FileNotFoundError:
        # If file doesn't exist, create an empty one
        with open("bangxephang.txt", "w", encoding="utf-8") as f:
            pass

    # Sort leaderboard by score (highest first)
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    return leaderboard

def update_leaderboard(name, score):
    # Add the new score
    with open("bangxephang.txt", "a", encoding="utf-8") as f:
        f.write(f"{name}: {score}\n")

    # Send updated leaderboard to all clients
    send_leaderboard_to_all()

def reset_leaderboard():
    # Clear the leaderboard file
    with open("bangxephang.txt", "w", encoding="utf-8") as f:
        pass
    print("Leaderboard has been reset")
    # Send the empty leaderboard to all clients
    send_leaderboard_to_all()

def send_leaderboard_to_all():
    leaderboard = load_leaderboard()
    # Format the leaderboard data for display
    rank_text = "HIỂN_THỊ_BXH\n" + "\n".join(f"{i+1}. {n}: {s} điểm" for i, (n, s) in enumerate(leaderboard))
    broadcast(rank_text)

def save_game_state():
    if len(names) < 2 or not current_question:
        return
    data = {
        "names": names,
        "scores": scores,
        "turn": turn,
        "current_question": current_question,
        "masked_answer": masked_answer
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_game_state():
    global names, scores, turn, current_question, masked_answer
    if not os.path.exists(SAVE_FILE):
        return False
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            names[:] = data["names"]
            scores[:] = data["scores"]
            turn = data["turn"]
            current_question = data["current_question"]
            masked_answer[:] = data["masked_answer"]
        return True
    except:
        return False

def clear_game_state():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

def reset_game():
    global scores, turn, game_ended
    # Reset scores to 0
    for i in range(len(scores)):
        scores[i] = 0
    # Reset turn to 0
    turn = 0
    # Reset game_ended flag
    game_ended = False
    # Clear saved game state
    clear_game_state()
    # Send a new question
    send_question()
    # Broadcast game restart message
    broadcast("\n🎮 TRÒ CHƠI MỚI BẮT ĐẦU! 🎮")
    # Send leaderboard to all clients
    send_leaderboard_to_all()
    # Show current scores (all zeros)
    show_scores()
    # Update turn
    update_turn()

def show_scores():
    score_text = "\n--- Điểm hiện tại ---\n"
    for idx, nm in enumerate(names):
        # Add a marker for the current player's turn
        current_marker = "➡️ " if idx == turn else ""
        # Format the score message in a consistent way that's easy for the client to parse
        score_text += f"{current_marker}SCORE_UPDATE:{nm}:{scores[idx]}\n"
    broadcast(score_text.strip())

def handle_turn(player_id):
    global turn, masked_answer, scores, game_ended
    landed_on_double = False

    # Check if player_id is valid before accessing clients list
    with clients_lock:
        if player_id >= len(clients):
            print(f"Invalid player_id: {player_id}, clients length: {len(clients)}")
            return False
        client = clients[player_id]

    # Check if player_id is valid for names list
    if player_id >= len(names):
        print(f"Invalid player_id for names: {player_id}, names length: {len(names)}")
        return False
    name = names[player_id]

    # Check if player_id is valid for scores list
    if player_id >= len(scores):
        print(f"Invalid player_id for scores: {player_id}, scores length: {len(scores)}")
        return False

    # Check if the game has already ended
    if game_ended:
        # If game has ended, check if this player wants to start a new game
        try:
            client.sendall("\nTR CHƠI Đ KẾT THÚC.......".encode())
            response = client.recv(1024)

            # If we received any response, treat it as a new game request
            print(f"New game request from {name}")
            with clients_lock:
                # Only reset the game if both players are still connected
                if len(clients) == 2:
                    reset_game()
                    return False  # Continue with the new game
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            print(f"Error waiting for new game request: {e}")
            return False

    # Track the initial score to calculate points earned in this turn
    initial_score = scores[player_id]
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
            landed_on_double = True
            scores[player_id] *= 2
            broadcast(f"{name} nhân đôi điểm! Tổng điểm: {scores[player_id]}")

            # Log the DOUBLE result first
            log_history(name, "nhân đôi", "-", "DOUBLE", scores[player_id])

            # Allow player to guess a character when they land on DOUBLE
            client.sendall("Nhập chữ cái hoặc đoán từ: ".encode())
            guess = client.recv(1024).decode().strip().lower()
            guess = guess.strip()
            answer = current_question['answer']

            if len(guess) == 1 and guess.isalpha():
                count = answer.count(guess)
                if count > 0:
                    # Check if the letter is already revealed
                    already_revealed = guess in masked_answer

                    # Update masked_answer regardless
                    for i, ch in enumerate(answer):
                        if ch == guess:
                            masked_answer[i] = guess

                    # Only award points if the letter wasn't already revealed
                    if not already_revealed:
                        # No points for guessing after DOUBLE, just the guess opportunity
                        broadcast(f"Có {count} chữ '{guess}' trong từ.")
                    else:
                        broadcast(f"Chữ '{guess}' đã được hiện trước đó. Không được tính điểm!")

                    broadcast(f"Từ hiện tại: {' '.join(masked_answer)}")
                    log_history(name, "đoán chữ sau DOUBLE", guess, "ĐÚNG" if not already_revealed else "ĐÃ HIỆN", scores[player_id])

                    # Check if all letters have been revealed
                    if '_' not in masked_answer:
                        scores[player_id] += 500  # Bonus for completing the word
                        broadcast(f"{name} đã hoàn thành từ và chiến thắng! +500 điểm (Tổng: {scores[player_id]})")
                        broadcast("KẾT THÚC TRÒ CHƠI!")
                        leaderboard_data = sorted(zip(names, scores), key=lambda x: x[1], reverse=True)
                        rank_text = "HIỂN_THỊ_BXH\n" + "\n".join(f"{i+1}. {n}: {s} điểm" for i, (n, s) in enumerate(leaderboard_data))
                        broadcast(rank_text)

                        log_history(name, "hoàn thành từ", "".join(masked_answer), "ĐÚNG", scores[player_id])
                        update_leaderboard(name, scores[player_id])
                        clear_game_state()

                        # Set the game_ended flag to true
                        game_ended = True

                        # Broadcast a message to all clients that they can start a new game
                        broadcast("\nTrò chơi đã kết thúc. Nhấn ENTER để bắt đầu trò chơi mới...")

                        return True
                else:
                    broadcast(f"Không có chữ '{guess}' nào.")
                    log_history(name, "đoán chữ sau DOUBLE", guess, "SAI", scores[player_id])
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
                    clear_game_state()

                    # Set the game_ended flag to true
                    game_ended = True

                    # Broadcast a message to all clients that they can start a new game
                    broadcast("\nTrò chơi đã kết thúc. Nhấn ENTER để bắt đầu trò chơi mới...")

                    return True
                else:
                    broadcast(f"Đoán sai từ '{guess}'.")
                    log_history(name, "đoán từ sau DOUBLE", guess, "SAI", scores[player_id])

            # Player gets an extra turn after DOUBLE
            return False
        else:
            client.sendall("Nhập chữ cái hoặc đoán từ: ".encode())
            guess = client.recv(1024).decode().strip().lower()
            guess = guess.strip()
            answer = current_question['answer']

            if len(guess) == 1 and guess.isalpha():
                count = answer.count(guess)
                if count > 0:
                    # Check if the letter is already revealed
                    already_revealed = guess in masked_answer

                    # Update masked_answer regardless
                    for i, ch in enumerate(answer):
                        if ch == guess:
                            masked_answer[i] = guess

                    # Only award points if the letter wasn't already revealed
                    if not already_revealed:
                        scores[player_id] += result * count
                        broadcast(f"Có {count} chữ '{guess}' trong từ.")
                    else:
                        broadcast(f"Chữ '{guess}' đã được hiện trước đó. Không được tính điểm!")

                    broadcast(f"Từ hiện tại: {' '.join(masked_answer)}")
                    log_history(name, "đoán chữ", guess, "ĐÚNG" if not already_revealed else "ĐÃ HIỆN", scores[player_id])

                    # Check if all letters have been revealed
                    if '_' not in masked_answer:
                        scores[player_id] += 500  # Bonus for completing the word
                        broadcast(f"{name} đã hoàn thành từ và chiến thắng! +500 điểm (Tổng: {scores[player_id]})")
                        broadcast("KẾT THÚC TRÒ CHƠI!")
                        leaderboard_data = sorted(zip(names, scores), key=lambda x: x[1], reverse=True)
                        rank_text = "HIỂN_THỊ_BXH\n" + "\n".join(f"{i+1}. {n}: {s} điểm" for i, (n, s) in enumerate(leaderboard_data))
                        broadcast(rank_text)

                        log_history(name, "hoàn thành từ", "".join(masked_answer), "ĐÚNG", scores[player_id])
                        update_leaderboard(name, scores[player_id])
                        clear_game_state()

                        # Set the game_ended flag to true
                        game_ended = True

                        # Broadcast a message to all clients that they can start a new game
                        broadcast("\nTrò chơi đã kết thúc. Nhấn ENTER để bắt đầu trò chơi mới...")

                        return True
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
                    clear_game_state()

                    # Set the game_ended flag to true
                    game_ended = True

                    # Broadcast a message to all clients that they can start a new game
                    broadcast("\nTrò chơi đã kết thúc. Nhấn ENTER để bắt đầu trò chơi mới...")

                    return True
                else:
                    broadcast(f"Đoán sai từ '{guess}'.")
                    log_history(name, "đoán từ", guess, "SAI", scores[player_id])

        # Calculate points earned in this turn
        points_earned = scores[player_id] - initial_score
        if points_earned > 0:
            broadcast(f"{name} đã kiếm được {points_earned} điểm trong lượt này!")
        elif points_earned < 0:
            broadcast(f"{name} đã mất {abs(points_earned)} điểm trong lượt này!")

        show_scores()
    except (ConnectionResetError, BrokenPipeError, OSError) as e:
        with clients_lock:
            if client in clients:
                clients.remove(client)
        try:
            client.close()
        except:
            pass
    finally:
        # Only update turn if the player didn't land on DOUBLE
        if not landed_on_double:
            with clients_lock:
                # If there are no clients left, reset turn to 0
                if not clients:
                    turn = 0
                # If there's only one client left, set turn to its index
                elif len(clients) == 1:
                    turn = 0
                # Otherwise, toggle between 0 and 1
                else:
                    turn = 1 - turn

            # Only update turn if there are clients connected
            if clients:
                update_turn()
        else:
            # If player landed on DOUBLE, broadcast that they get an extra turn
            broadcast(f"{name} quay được DOUBLE nên được chơi thêm lượt nữa!")
    return False

def client_handler(client, player_id):
    try:
        mode = client.recv(1024).decode().strip()
        name = client.recv(1024).decode().strip()

        # Ensure player_id is still valid
        with clients_lock:
            if player_id >= len(clients) or clients[player_id] != client:
                print(f"Client mismatch or invalid player_id: {player_id}")
                return

            # Add name to the names list, ensuring it has enough elements
            while len(names) <= player_id:
                names.append("")
            names[player_id] = name

            # Ensure scores list has enough elements
            while len(scores) <= player_id:
                scores.append(0)

        broadcast(f"{name} đã tham gia trò chơi.")

        # Send leaderboard to the new client
        send_leaderboard_to_all()

        # Main client handling loop - runs for all clients regardless of game state
        while True:
            # Check if player_id is still valid
            with clients_lock:
                if player_id >= len(clients):
                    print(f"Client disconnected, player_id {player_id} is no longer valid")
                    break

            # Check for special commands from client
            try:
                # Use select to check if there's data to read without blocking
                import select
                readable, _, _ = select.select([client], [], [], 0.1)
                if readable:
                    data = client.recv(1024).decode().strip()
                    if data == "RESET_LEADERBOARD":
                        print(f"Reset leaderboard request from {name}")
                        reset_leaderboard()
                        broadcast(f"{name} đã đặt lại bảng xếp hạng.")
                        continue
            except Exception as e:
                print(f"Error checking for commands: {e}")

            # Game logic - only runs when there are 2 players
            if len(clients) == 2:
                # Initialize game if not already done
                if not current_question:
                    if mode == "2" and load_game_state():
                        broadcast("\n👉 Khôi phục game từ lần chơi trước...")
                        broadcast(f"Câu hỏi: {current_question['question']}")
                        broadcast(f"Từ hiện tại: {' '.join(masked_answer)}")
                        show_scores()
                        broadcast("Bắt đầu trò chơi!")
                        update_turn()
                    else:
                        clear_game_state()
                        send_question()
                        broadcast("Bắt đầu trò chơi!")
                        update_turn()

                # If it's this player's turn, handle it
                if player_id == turn:
                    # Handle the turn, which returns True if game ended
                    # The handle_turn function now handles new game requests internally
                    handle_turn(player_id)

    except (ConnectionResetError, BrokenPipeError, OSError) as e:
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
            # Add the client to the list and get its index
            clients.append(client)
            player_id = len(clients) - 1

            # Limit to 2 players maximum
            if len(clients) > 2:
                print(f"Too many clients, rejecting client {addr}")
                try:
                    client.sendall("Server is full. Please try again later.".encode())
                    client.close()
                except:
                    pass
                clients.pop()  # Remove the client we just added
                continue

        # Start a new thread to handle this client
        threading.Thread(target=client_handler, args=(client, player_id), daemon=True).start()

if __name__ == "__main__":
    start_server()
