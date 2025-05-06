# client.py
import pygame
import socket
import json
import threading
import sys
import time
import game_config # Lấy SERVER_PORT, BUFFER_SIZE từ đây

# --- Cấu hình Pygame ---
pygame.init()
pygame.font.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chiếc Nón Kỳ Diệu - Client")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 200)
RED = (200, 0, 0)
DARK_RED = (150, 0, 0)
GREEN = (0, 180, 0)
DARK_GREEN = (0, 100, 0)
LIGHT_GRAY = (200, 200, 200)
GRAY = (150, 150, 150)
DARK_GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Fonts
try:
    TITLE_FONT = pygame.font.SysFont("tahoma", 50, bold=True)
    CATEGORY_FONT = pygame.font.SysFont("tahoma", 30)
    PUZZLE_FONT = pygame.font.SysFont("consolas", 40, bold=True)
    SCORE_FONT = pygame.font.SysFont("tahoma", 28)
    MSG_FONT = pygame.font.SysFont("tahoma", 22)
    INPUT_FONT = pygame.font.SysFont("tahoma", 30)
    BUTTON_FONT = pygame.font.SysFont("tahoma", 22, bold=True)
    SMALL_MSG_FONT = pygame.font.SysFont("tahoma", 18)
except pygame.error:
    print("Lỗi: Không tìm thấy font 'tahoma' hoặc 'consolas'. Sử dụng font mặc định 'arial'.")
    TITLE_FONT = pygame.font.SysFont("arial", 50, bold=True)
    CATEGORY_FONT = pygame.font.SysFont("arial", 30)
    PUZZLE_FONT = pygame.font.SysFont("monospace", 40, bold=True)
    SCORE_FONT = pygame.font.SysFont("arial", 28)
    MSG_FONT = pygame.font.SysFont("arial", 22)
    INPUT_FONT = pygame.font.SysFont("arial", 30)
    BUTTON_FONT = pygame.font.SysFont("arial", 22, bold=True)
    SMALL_MSG_FONT = pygame.font.SysFont("arial", 18)


# --- Trạng thái Client (sẽ được cập nhật từ server) ---
client_socket = None
my_player_name = "Đang chờ..." # Tên người chơi sau khi đặt
my_player_server_id = "P?" # Server sẽ gửi P1, P2...
current_category = "Đang tải..."
current_puzzle_display = "--- LOADING ---"
player_scores_display = []
is_my_turn = False
game_over_client = False
winner_client_id = None # ID (P1,P2) của người thắng
message_log_client = "Chào mừng đến với Chiếc Nón Kỳ Diệu!"
game_started_client = False
server_requesting_name = False
current_turn_player_name_from_server = "" # Tên người chơi đang có lượt (từ server)

# Input text
input_text = ""
input_active = False
input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 140, 400, 45)
input_placeholder_default = "Nhập chữ cái hoặc cụm từ..."
input_placeholder_name_template = "Nhập tên của bạn ({}) và Enter..."
input_placeholder = input_placeholder_name_template.format(my_player_server_id)

# Buttons
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_Y = SCREEN_HEIGHT - 80
SPACING = 20

spin_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_WIDTH * 1.5 - SPACING, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
guess_letter_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_WIDTH * 0.5, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
solve_puzzle_button_rect = pygame.Rect(SCREEN_WIDTH // 2 + BUTTON_WIDTH * 0.5 + SPACING, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
confirm_name_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_WIDTH //2 , BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)

# --- Kết nối mạng ---
def connect_to_server(server_ip, server_port):
    global client_socket, message_log_client
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        print(f"[CLIENT] Đã kết nối tới server {server_ip}:{server_port}")
        message_log_client = f"Đã kết nối tới {server_ip}:{server_port}. Đang chờ server..."
        return True
    except socket.error as e:
        print(f"[CLIENT_ERROR] Lỗi kết nối: {e}")
        message_log_client = f"Lỗi kết nối: {e}. Kiểm tra IP/Port và server."
        return False

def send_action(action_data):
    if client_socket:
        try:
            client_socket.sendall((json.dumps(action_data) + "\n").encode('utf-8'))
        except socket.error as e:
            print(f"[CLIENT_ERROR] Lỗi gửi dữ liệu: {e}")
            global message_log_client
            message_log_client = "Lỗi gửi dữ liệu tới server."

receive_buffer = ""

def receive_data_thread_func():
    global current_category, current_puzzle_display, player_scores_display, is_my_turn
    global game_over_client, winner_client_id, message_log_client, my_player_name
    global game_started_client, input_active, input_placeholder, server_requesting_name
    global my_player_server_id, receive_buffer, current_turn_player_name_from_server

    while True:
        if not client_socket:
            time.sleep(0.1)
            continue
        try:
            data_chunk = client_socket.recv(game_config.BUFFER_SIZE)
            if not data_chunk:
                print("[CLIENT] Mất kết nối tới server (no data_chunk).")
                message_log_client = "Mất kết nối tới server!"
                if client_socket: client_socket.close() # Đóng socket ở đây
                client_socket = None # Đặt là None để vòng lặp chính biết
                break

            receive_buffer += data_chunk.decode('utf-8')
            
            while '\n' in receive_buffer:
                message_str, receive_buffer = receive_buffer.split('\n', 1)
                if not message_str.strip():
                    continue
                
                try:
                    server_data = json.loads(message_str)
                except json.JSONDecodeError:
                    print(f"[CLIENT_ERROR] Dữ liệu JSON không hợp lệ từ server: {message_str[:200]}")
                    continue

                msg_type = server_data.get("type")

                if msg_type == "game_update":
                    current_category = server_data.get("category", current_category)
                    current_puzzle_display = server_data.get("puzzle", current_puzzle_display)
                    player_scores_display = server_data.get("scores", player_scores_display)
                    
                    # my_player_name là tên người chơi, my_player_server_id là P1/P2...
                    my_player_name = server_data.get("my_player_id", my_player_name)
                    my_player_server_id = server_data.get("my_player_server_id", my_player_server_id)
                    is_my_turn = server_data.get("is_my_turn", is_my_turn) # Server tính toán và gửi trực tiếp

                    game_over_client = server_data.get("game_over", game_over_client)
                    winner_client_id = server_data.get("winner", winner_client_id) # Server gửi ID người thắng
                    message_log_client = server_data.get("message_log", message_log_client)
                    current_turn_player_name_from_server = server_data.get("current_player_turn_name", "")


                    game_started_client = server_data.get("game_started", game_started_client)
                    if game_started_client and server_requesting_name: # Nếu game bắt đầu thì không yêu cầu tên nữa
                        server_requesting_name = False
                        input_placeholder = input_placeholder_default
                        input_active = is_my_turn # Kích hoạt input nếu đến lượt
                    
                    if is_my_turn and not game_over_client and game_started_client:
                        input_active = True
                        if "Hãy đoán một chữ cái" in message_log_client or "Tiếp tục quay hoặc đoán" in message_log_client :
                            input_placeholder = "Nhập 1 chữ cái và Enter/Nút Đoán"
                        else:
                             input_placeholder = input_placeholder_default
                    elif not is_my_turn and game_started_client : # Không phải lượt mình thì tắt input
                        input_active = False


                elif msg_type == "error":
                    message_log_client = f"Lỗi từ Server: {server_data.get('message')}"
                
                elif msg_type == "request_name":
                    server_requesting_name = True
                    message_log_client = server_data.get("message", "Server yêu cầu bạn đặt tên.")
                    my_player_server_id = server_data.get("player_id", my_player_server_id) # Server gửi P1, P2
                    input_placeholder = input_placeholder_name_template.format(my_player_server_id)
                    input_active = True
                    input_text = ""

        except socket.timeout:
            continue
        except socket.error as e:
            print(f"[CLIENT_ERROR] Lỗi nhận dữ liệu socket: {e}")
            message_log_client = "Lỗi kết nối khi nhận dữ liệu!"
            if client_socket: client_socket.close()
            client_socket = None
            break 
        except Exception as e:
            print(f"[CLIENT_ERROR] Lỗi xử lý dữ liệu từ server: {e}, data: '{message_str[:200]}'")

# --- Hàm vẽ ---
def draw_text(text, font, color, surface, x, y, center_x=False, center_y=False, max_width=None):
    lines_rendered = []
    if max_width:
        words = text.split(' ')
        current_line_text = ""
        for word in words:
            test_line = current_line_text + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line_text = test_line
            else:
                lines_rendered.append(current_line_text.strip())
                current_line_text = word + " "
        lines_rendered.append(current_line_text.strip())
    else:
        lines_rendered.append(text)
        
    total_height_drawn = 0
    for i, line_to_draw in enumerate(lines_rendered):
        textobj = font.render(line_to_draw, True, color)
        textrect = textobj.get_rect()
        if center_x: textrect.centerx = x
        else: textrect.x = x
        
        if center_y and len(lines_rendered) == 1: # Chỉ căn giữa y nếu là 1 dòng
             textrect.centery = y
        else: # Nếu nhiều dòng hoặc không căn giữa y, y là vị trí dòng đầu
            textrect.y = y + i * font.get_linesize()

        surface.blit(textobj, textrect)
        total_height_drawn += font.get_linesize()
    return total_height_drawn


def draw_button(surface, rect, text, text_color, button_color, hover_color=None, border_color=BLACK, disabled=False):
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos) and not disabled
    
    current_color = button_color
    current_text_color = text_color
    if disabled:
        current_color = GRAY
        current_text_color = LIGHT_GRAY
    elif is_hovered and hover_color:
        current_color = hover_color

    pygame.draw.rect(surface, current_color, rect, border_radius=5)
    if border_color:
        pygame.draw.rect(surface, border_color if not disabled else DARK_GRAY, rect, 2, border_radius=5)
    
    draw_text(text, BUTTON_FONT, current_text_color, surface, rect.centerx, rect.centery, center_x=True, center_y=True)

# --- Hàm vẽ giao diện game ---
def draw_game_screen():
    screen.fill(WHITE)

    draw_text("CHIẾC NÓN KỲ DIỆU", TITLE_FONT, BLUE, screen, SCREEN_WIDTH // 2, 40, center_x=True)
    display_id_text = my_player_name
    if my_player_name != my_player_server_id and "P" in my_player_server_id :
         display_id_text = f"{my_player_name} ({my_player_server_id})"
    draw_text(f"Bạn là: {display_id_text}", SMALL_MSG_FONT, BLACK, screen, 15, 15)

    if not game_started_client and not server_requesting_name and not game_over_client:
        if client_socket and client_socket.fileno() != -1 : # Kiểm tra socket còn hợp lệ
             draw_text("Đang chờ server và người chơi khác...", MSG_FONT, BLACK, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50, center_x=True, center_y=True)
        else:
             draw_text(message_log_client, MSG_FONT, RED, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50, center_x=True, center_y=True, max_width=SCREEN_WIDTH-40)


    if game_started_client or (current_category != "Đang tải..." and current_category): # Chỉ vẽ nếu có category
        draw_text(f"Chủ đề: {current_category}", CATEGORY_FONT, DARK_GRAY, screen, SCREEN_WIDTH // 2, 90, center_x=True)

    # Puzzle Display
    puzzle_y_start = 150
    box_size_w = PUZZLE_FONT.size("X")[0] + 10
    box_size_h = PUZZLE_FONT.get_height() + 10
    padding = 5 
    
    max_boxes_per_line = (SCREEN_WIDTH - 100) // (box_size_w + padding)
    puzzle_lines_chars = []
    current_line_chars_temp = []
    for char_puzzle in current_puzzle_display:
        current_line_chars_temp.append(char_puzzle)
        if len(current_line_chars_temp) >= max_boxes_per_line:
            puzzle_lines_chars.append(list(current_line_chars_temp))
            current_line_chars_temp = []
    if current_line_chars_temp:
        puzzle_lines_chars.append(list(current_line_chars_temp))

    total_puzzle_height = len(puzzle_lines_chars) * (box_size_h + padding)
    current_render_y = puzzle_y_start + ( (SCREEN_HEIGHT * 0.4 - total_puzzle_height) / 2) 
    current_render_y = max(current_render_y, puzzle_y_start) # Đảm bảo không vẽ quá cao

    for line_chars in puzzle_lines_chars:
        total_line_width = len(line_chars) * (box_size_w + padding) - padding
        start_x = (SCREEN_WIDTH - total_line_width) // 2
        current_render_x = start_x
        for char_render in line_chars:
            box_rect_draw = pygame.Rect(current_render_x, current_render_y, box_size_w, box_size_h)
            if char_render == " ":
                pass # Không vẽ ô cho dấu cách
            else:
                pygame.draw.rect(screen, LIGHT_GRAY, box_rect_draw, border_radius=3)
                pygame.draw.rect(screen, GRAY, box_rect_draw, 2, border_radius=3)
                if char_render != '_':
                    draw_text(char_render, PUZZLE_FONT, BLACK, screen, box_rect_draw.centerx, box_rect_draw.centery, center_x=True, center_y=True)
            current_render_x += box_size_w + padding
        current_render_y += box_size_h + padding

    # Scores
    score_x_start = SCREEN_WIDTH - 320 # Dịch sang trái một chút
    score_y_start = 90
    draw_text("Điểm số:", SCORE_FONT, BLACK, screen, score_x_start, score_y_start - 35)
    for i, p_score_data in enumerate(player_scores_display):
        p_id = p_score_data.get("id", "N/A")
        p_name = p_score_data.get("name", p_id)
        p_s = p_score_data.get("score", 0)
        
        display_text = f"{p_name} ({p_id}): {p_s}"
        text_color = BLACK
        
        is_this_client_player = (p_id == my_player_server_id)

        is_current_turn_player = False
        if game_started_client and not game_over_client:
             if is_my_turn and is_this_client_player:
                 is_current_turn_player = True
             elif not is_my_turn and not is_this_client_player and current_turn_player_name_from_server == p_name : # Server báo người này đang chơi
                 is_current_turn_player = True


        if is_this_client_player:
            text_color = DARK_GREEN
            if is_current_turn_player: # Lượt của client này
                 text_color = GREEN 
        elif is_current_turn_player: # Lượt của người chơi khác
            text_color = ORANGE

        prefix = "-> " if is_current_turn_player else "   "
        draw_text(prefix + display_text, SCORE_FONT, text_color, screen, score_x_start, score_y_start + 35 * i, max_width=310)

    # Message Log
    log_area_height = 80
    log_y_pos = input_rect.top - log_area_height - 10
    draw_text(message_log_client, MSG_FONT, BLUE, screen, SCREEN_WIDTH // 2, log_y_pos + log_area_height // 2, center_x=True, center_y=True, max_width=SCREEN_WIDTH - 40)

    # Input Box
    pygame.draw.rect(screen, WHITE, input_rect, border_radius=5)
    border_color_input = BLUE if input_active else BLACK
    pygame.draw.rect(screen, border_color_input, input_rect, 2, border_radius=5) 
    
    text_to_show_in_input = input_text
    color_for_input_text = BLACK
    current_placeholder = input_placeholder_name_template.format(my_player_server_id) if server_requesting_name else input_placeholder
    
    if not input_text and (not input_active or (input_active and not server_requesting_name and not is_my_turn and game_started_client)):
        text_to_show_in_input = current_placeholder
        color_for_input_text = GRAY
    
    draw_text(text_to_show_in_input, INPUT_FONT, color_for_input_text, screen, input_rect.x + 10, input_rect.centery, center_y=True)

    # Buttons
    if server_requesting_name:
        draw_button(screen, confirm_name_button_rect, "XÁC NHẬN TÊN", WHITE, GREEN, DARK_GREEN, disabled=not input_text.strip())
    elif game_started_client and not game_over_client:
        is_action_disabled = not is_my_turn
        can_guess_letter = input_text.strip() and len(input_text.strip()) == 1 and input_text.strip().isalnum()
        can_solve_puzzle = input_text.strip() and len(input_text.strip()) > 1
        
        draw_button(screen, spin_button_rect, "QUAY NÓN", WHITE, GREEN, DARK_GREEN, disabled=is_action_disabled)
        draw_button(screen, guess_letter_button_rect, "ĐOÁN CHỮ", WHITE, ORANGE, (200,120,0), disabled=is_action_disabled or not can_guess_letter)
        draw_button(screen, solve_puzzle_button_rect, "GIẢI Ô CHỮ", WHITE, RED, DARK_RED, disabled=is_action_disabled or not can_solve_puzzle)

    # Game Over Message
    if game_over_client:
        overlay_sfc = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay_sfc.fill((0,0,0, 180))
        screen.blit(overlay_sfc, (0,0))
        
        winner_name_display = "Không có ai"
        if winner_client_id: # Tìm tên người thắng từ ID
            for p_score in player_scores_display:
                if p_score.get("id") == winner_client_id:
                    winner_name_display = p_score.get("name", winner_client_id)
                    break
        
        winner_text_line = f"NGƯỜI CHIẾN THẮNG: {winner_name_display}!" if winner_client_id else "TRÒ CHƠI KẾT THÚC!"
        draw_text(winner_text_line, TITLE_FONT, YELLOW, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, center_x=True, center_y=True)
        draw_text("Ấn ESC để thoát.", MSG_FONT, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30, center_x=True, center_y=True)
        
        final_score_y_pos = SCREEN_HEIGHT // 2 + 80
        for i, p_score in enumerate(player_scores_display):
            p_name_final = p_score.get("name", p_score.get("id", "N/A"))
            p_s_final = p_score.get("score", 0)
            final_display_text = f"{p_name_final}: {p_s_final}"
            draw_text(final_display_text, SCORE_FONT, WHITE, screen, SCREEN_WIDTH // 2, final_score_y_pos + 35 * i, center_x=True)

    pygame.display.flip()

# --- Main Game Loop ---
def main_client_loop(server_ip_addr_param, server_port_num_param):
    global input_text, input_active, message_log_client, server_requesting_name
    global input_placeholder, my_player_name, client_socket

    if not connect_to_server(server_ip_addr_param, server_port_num_param):
        error_running_loop = True
        clock = pygame.time.Clock()
        while error_running_loop:
            for event_err in pygame.event.get():
                if event_err.type == pygame.QUIT or \
                   (event_err.type == pygame.KEYDOWN and event_err.key == pygame.K_ESCAPE):
                    error_running_loop = False
            draw_game_screen()
            clock.tick(30)
        pygame.quit()
        sys.exit()

    if client_socket:
        client_socket.settimeout(1.0)

    receive_thread = threading.Thread(target=receive_data_thread_func, daemon=True)
    receive_thread.start()

    running_main = True
    clock = pygame.time.Clock()

    while running_main:
        if client_socket is None or client_socket.fileno() == -1: # Kiểm tra nếu socket đã bị đóng bởi thread nhận
            message_log_client = "Mất kết nối tới server. Thoát game."
            # Có thể thêm 1 vòng lặp nhỏ ở đây để hiển thị thông báo này trước khi thoát hẳn
            time.sleep(2)
            running_main = False # Thoát vòng lặp chính
            continue


        mouse_was_clicked = False
        for event_game in pygame.event.get():
            if event_game.type == pygame.QUIT:
                running_main = False
            if event_game.type == pygame.KEYDOWN:
                if event_game.key == pygame.K_ESCAPE:
                    running_main = False
                if input_active: # Chỉ xử lý phím nếu ô input đang active
                    if event_game.key == pygame.K_RETURN:
                        if server_requesting_name:
                            if input_text.strip():
                                my_player_name = input_text.strip() # Cập nhật tên client ngay
                                send_action({"type": "set_name", "name": my_player_name, "player_id": my_player_server_id}) # Gửi cả Px id
                                message_log_client = f"Đã gửi tên '{my_player_name}'. Đang chờ server..."
                                # server_requesting_name = False # Để server xác nhận
                                input_active = False # Chờ server update
                            else:
                                message_log_client = "Tên không được để trống! " + input_placeholder_name_template.format(my_player_server_id)
                        
                        elif is_my_turn and not game_over_client and game_started_client:
                            # Enter để đoán chữ nếu có yêu cầu
                            if "Hãy đoán một chữ cái" in message_log_client or "Tiếp tục quay hoặc đoán" in message_log_client:
                                if input_text.strip() and len(input_text.strip()) == 1 and input_text.strip().isalnum():
                                    send_action({"type": "guess_letter", "letter": input_text.strip().upper()})
                                else:
                                     message_log_client = "Vui lòng nhập MỘT chữ cái hợp lệ và Enter, hoặc dùng nút."
                            else:
                                message_log_client = "Sử dụng các nút để thực hiện hành động."
                        input_text = "" # Luôn xóa input sau Enter

                    elif event_game.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if len(input_text) < 40:
                           input_text += event_game.unicode
            
            if event_game.type == pygame.MOUSEBUTTONDOWN:
                if event_game.button == 1:
                    mouse_was_clicked = True
                    # Click vào ô input
                    if input_rect.collidepoint(event_game.pos):
                        # Chỉ active nếu đang yêu cầu tên HOẶC đến lượt VÀ game đã bắt đầu
                        if (server_requesting_name or (is_my_turn and game_started_client)) and not game_over_client :
                            input_active = True
                        else: # Ngược lại thì không cho active
                            input_active = False
                            if not server_requesting_name and not is_my_turn and game_started_client:
                                message_log_client = "Không phải lượt của bạn để nhập."
                            elif not server_requesting_name and not game_started_client:
                                 message_log_client = "Đang chờ game bắt đầu hoặc server yêu cầu tên."

                    else: # Click ra ngoài ô input
                        input_active = False
        
        # Xử lý click nút
        if mouse_was_clicked:
            mouse_pos_now = pygame.mouse.get_pos()
            if server_requesting_name:
                if confirm_name_button_rect.collidepoint(mouse_pos_now) and input_text.strip():
                    my_player_name = input_text.strip()
                    send_action({"type": "set_name", "name": my_player_name, "player_id": my_player_server_id})
                    message_log_client = f"Đã gửi tên '{my_player_name}'. Đang chờ server..."
                    input_active = False
                    input_text = ""
            elif is_my_turn and not game_over_client and game_started_client:
                if spin_button_rect.collidepoint(mouse_pos_now):
                    send_action({"type": "spin_wheel"})
                    input_text = "" 
                elif guess_letter_button_rect.collidepoint(mouse_pos_now):
                    if input_text.strip() and len(input_text.strip()) == 1 and input_text.strip().isalnum():
                        send_action({"type": "guess_letter", "letter": input_text.strip().upper()})
                        input_text = ""
                    else:
                        message_log_client = "Nhập MỘT chữ cái vào ô rồi bấm nút 'ĐOÁN CHỮ'."
                elif solve_puzzle_button_rect.collidepoint(mouse_pos_now):
                    if input_text.strip() and len(input_text.strip()) > 1:
                        send_action({"type": "solve_puzzle", "phrase": input_text.strip().upper()})
                        input_text = ""
                    else:
                        message_log_client = "Nhập cụm từ bạn muốn giải vào ô rồi bấm 'GIẢI Ô CHỮ'."
            
            elif not is_my_turn and game_started_client and not game_over_client and not server_requesting_name:
                buttons_to_check_disabled = [spin_button_rect, guess_letter_button_rect, solve_puzzle_button_rect]
                for btn_r in buttons_to_check_disabled:
                    if btn_r.collidepoint(mouse_pos_now):
                        message_log_client = "Không phải lượt của bạn!"
                        break
        
        draw_game_screen()
        clock.tick(60)

    if client_socket and client_socket.fileno() != -1: # Kiểm tra socket còn mở trước khi gửi disconnect
        send_action({"type": "disconnect"})
        time.sleep(0.1) # Chờ chút để action được gửi đi
        client_socket.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    default_ip_main = "127.0.0.1"
    default_port_main = game_config.SERVER_PORT

    if len(sys.argv) >= 3:
        server_ip_addr_main = sys.argv[1]
        try:
            server_port_val_main = int(sys.argv[2])
        except ValueError:
            print(f"Port không hợp lệ: '{sys.argv[2]}'. Sử dụng port mặc định {default_port_main}.")
            server_port_val_main = default_port_main
    elif len(sys.argv) == 2:
        server_ip_addr_main = sys.argv[1]
        server_port_val_main = default_port_main
        print(f"Sử dụng IP server: {server_ip_addr_main} và port mặc định {default_port_main}.")
    else:
        print("--- Chiếc Nón Kỳ Diệu Client ---")
        server_ip_addr_input_main = input(f"Nhập địa chỉ IP của Server (mặc định '{default_ip_main}'): ")
        server_ip_addr_main = server_ip_addr_input_main.strip() or default_ip_main
        
        server_port_input_main = input(f"Nhập cổng của Server (mặc định '{default_port_main}'): ")
        try:
            server_port_val_main = int(server_port_input_main.strip()) if server_port_input_main.strip() else default_port_main
        except ValueError:
            print(f"Cổng không hợp lệ. Sử dụng cổng mặc định {default_port_main}.")
            server_port_val_main = default_port_main
        
    main_client_loop(server_ip_addr_main, server_port_val_main)