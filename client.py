# client.py
import pygame
import socket
import json
import threading
import sys
import time
import math # Thêm thư viện math
import random # Thêm để chọn màu ngẫu nhiên cho segment nếu cần
import game_config # Lấy SERVER_PORT, BUFFER_SIZE, WHEEL_SEGMENTS từ đây

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
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
LIGHT_BLUE = (173, 216, 230)
PINK = (255, 192, 203)

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
    WHEEL_TEXT_FONT = pygame.font.SysFont("tahoma", 16, bold=True) # Font cho chữ trên vòng quay
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
    WHEEL_TEXT_FONT = pygame.font.SysFont("arial", 16, bold=True)


# --- Cấu hình Vòng Quay ---
WHEEL_CENTER_X = SCREEN_WIDTH // 2
WHEEL_CENTER_Y = 220  # Điều chỉnh vị trí Y của vòng quay
WHEEL_RADIUS = 100    # Giảm bán kính để vừa vặn hơn
POINTER_COLOR = DARK_RED
POINTER_SIZE = (20, 10) # (width, height) của tam giác kim chỉ

# Màu cho các ô trên vòng quay (cần đủ màu cho các WHEEL_SEGMENTS)
SEGMENT_COLORS_BASE = [RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN, MAGENTA, LIGHT_BLUE, PINK,
                  (255,105,180), (138,43,226), (0,128,128), (210,105,30), (124,252,0),
                  (255,20,147), (0,250,154)]
# Đảm bảo có đủ màu, lặp lại nếu cần
NUM_SEGMENTS = len(game_config.WHEEL_SEGMENTS)
SEGMENT_COLORS = (SEGMENT_COLORS_BASE * (NUM_SEGMENTS // len(SEGMENT_COLORS_BASE) + 1))[:NUM_SEGMENTS]


wheel_surface = None # Surface chứa hình ảnh vòng quay đã vẽ sẵn
current_wheel_angle = 0.0 # Góc quay hiện tại của vòng quay
is_spinning_animation = False # Trạng thái đang quay hoạt ảnh
spin_animation_end_time = 0
SPIN_ANIMATION_DURATION_MS = 2500 # Thời gian hoạt ảnh quay (ms)
SPIN_SPEED_INITIAL = 25 # Tốc độ quay ban đầu (degrees per frame)
current_spin_speed = 0.0

# --- Trạng thái Client (sẽ được cập nhật từ server) ---
client_socket = None
my_player_name = "Đang chờ..."
my_player_server_id = "P?"
current_category = "Đang tải..."
current_puzzle_display = "--- LOADING ---"
player_scores_display = []
is_my_turn = False
game_over_client = False
winner_client_id = None
message_log_client = "Chào mừng đến với Chiếc Nón Kỳ Diệu!"
game_started_client = False
server_requesting_name = False
waiting_for_game_start_after_name_sent = False # <-- NEW FLAG
current_turn_player_name_from_server = ""

# Input text
input_text = ""
input_active = False
input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 140, 400, 45)
input_placeholder_default = "Nhập chữ cái hoặc cụm từ..."
input_placeholder_name_template = "Nhập tên của bạn ({}) và Enter..."
input_placeholder = input_placeholder_name_template.format(my_player_server_id) # Initial placeholder


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
    global client_socket, is_spinning_animation, waiting_for_game_start_after_name_sent # Thêm biến mới

    while True:
        if not client_socket:
            time.sleep(0.1)
            continue
        try:
            data_chunk = client_socket.recv(game_config.BUFFER_SIZE)
            if not data_chunk:
                print("[CLIENT] Mất kết nối tới server (no data_chunk).")
                message_log_client = "Mất kết nối tới server!"
                if client_socket: client_socket.close()
                client_socket = None
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
                    
                    # my_player_id from server is now name in the server code, but client uses my_player_name for display
                    # Let's update my_player_name from server if the server sends it explicitly in the future
                    # For now, my_player_name is set when sending the name action

                    my_player_server_id = server_data.get("my_player_server_id", my_player_server_id)
                    is_my_turn = server_data.get("is_my_turn", is_my_turn)

                    game_over_client = server_data.get("game_over", game_over_client)
                    winner_client_id = server_data.get("winner", winner_client_id)
                    new_message_log = server_data.get("message_log", message_log_client)
                    
                    # Nếu server gửi thông báo kết quả quay, dừng animation sớm hơn nếu cần
                    # if "quay vào" in new_message_log.lower() and is_spinning_animation:
                    #     # is_spinning_animation = False # Có thể dừng ở đây, nhưng để nó tự hết duration cũng được
                    #     pass
                    message_log_client = new_message_log


                    current_turn_player_name_from_server = server_data.get("current_player_turn_name", "")

                    game_started_client = server_data.get("game_started", game_started_client)

                    # --- NEW LOGIC FOR STATE TRANSITION AFTER NAME ---
                    if game_started_client:
                         waiting_for_game_start_after_name_sent = False # Game started, turn off waiting flag
                         server_requesting_name = False # No longer requesting name

                    # Input active logic based on game state and turn
                    if game_started_client and not game_over_client:
                        if is_my_turn:
                            input_active = True
                            # Update placeholder based on game phase (spin result received or not)
                            if "Hãy đoán một chữ cái" in message_log_client or "Tiếp tục quay hoặc đoán" in message_log_client :
                                input_placeholder = "Nhập 1 chữ cái và Enter/Nút Đoán..."
                            else:
                                input_placeholder = input_placeholder_default # Default like solving puzzle
                        else:
                            input_active = False # Not my turn
                    elif server_requesting_name:
                         input_active = True # Input is active when server requests name
                         input_placeholder = input_placeholder_name_template.format(my_player_server_id)
                    else: # Waiting before game start, or game over
                         input_active = False
                         # Placeholder will be handled in draw_game_screen based on waiting_for_game_start_after_name_sent


                elif msg_type == "error":
                    message_log_client = f"Lỗi từ Server: {server_data.get('message')}"
                
                elif msg_type == "request_name":
                    server_requesting_name = True
                    waiting_for_game_start_after_name_sent = False # Turn off waiting if server requests name again
                    message_log_client = server_data.get("message", "Server yêu cầu bạn đặt tên.")
                    my_player_server_id = server_data.get("player_id", my_player_server_id)
                    # my_player_name can stay as default or previous attempt until set
                    input_placeholder = input_placeholder_name_template.format(my_player_server_id)
                    input_active = True # Input becomes active to enter name
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
def draw_text(text, font, color, surface, x, y, center_x=False, center_y=False, max_width=None, angle=0):
    lines_rendered_texts = []
    if max_width:
        words = text.split(' ')
        current_line_text = ""
        for word in words:
            test_line = current_line_text + word + " "
            # Check width using the original text before rotation
            if font.size(test_line)[0] <= max_width:
                current_line_text = test_line
            else:
                lines_rendered_texts.append(current_line_text.strip())
                current_line_text = word + " "
        lines_rendered_texts.append(current_line_text.strip())
    else:
        lines_rendered_texts.append(text)

    total_height_drawn = 0
    for i, line_to_draw in enumerate(lines_rendered_texts):
        textobj_orig = font.render(line_to_draw, True, color)
        # Handle rotation
        textobj = pygame.transform.rotate(textobj_orig, angle)
        textrect = textobj.get_rect()

        # Calculate positioning based on rotation and desired alignment
        if center_x:
            textrect.centerx = x
        else:
            textrect.x = x

        current_y_pos = y
        if center_y and len(lines_rendered_texts) == 1:
            textrect.centery = y
        else:
            # Adjust y for multiple lines based on the original text height
            # total_height_drawn accumulates the height of previous lines (based on original size)
            current_y_pos = y + total_height_drawn
            if center_y:  # If centering vertically, adjust initial y
                 # This centering for multi-line rotated text is complex. A simpler approach is needed or accept non-perfect centering.
                 # For simplicity, we will position lines relative to the calculated y, adjusting for total height.
                 # The initial y should be adjusted *before* the loop if total height is known.
                 pass # Let's simplify centering for now to avoid bugs. Line-by-line positioning is more reliable.

            textrect.y = current_y_pos # Use the calculated y position

        surface.blit(textobj, textrect)
        # Add height of the original text for the next line's offset
        total_height_drawn += textobj_orig.get_rect().height

    # Return the total height drawn, useful for positioning other elements afterward
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

    # Use the BUTTON_FONT directly here
    draw_text(text, BUTTON_FONT, current_text_color, surface, rect.centerx, rect.centery, center_x=True, center_y=True)

# --- Hàm vẽ Vòng Quay ---

# --- Hàm vẽ Vòng Quay ---
# Define WHEEL_RADIUS globally before initialize_wheel uses it
WHEEL_CENTER_X = SCREEN_WIDTH // 2
WHEEL_CENTER_Y = 220  # Điều chỉnh vị trí Y của vòng quay
WHEEL_RADIUS = 200    # Gán giá trị mặc định cho bán kính vòng quay (Định nghĩa GLOBAL)
POINTER_COLOR = DARK_RED
POINTER_SIZE = (20, 10) # (width, height) của tam giác kim chỉ

# Màu cho các ô trên vòng quay (cần đủ màu cho các WHEEL_SEGMENTS)
SEGMENT_COLORS_BASE = [RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN, MAGENTA, LIGHT_BLUE, PINK,
                  (255,105,180), (138,43,226), (0,128,128), (210,105,30), (124,252,0),
                  (255,20,147), (0,250,154)]
# Đảm bảo có đủ màu, lặp lại nếu cần
NUM_SEGMENTS = len(game_config.WHEEL_SEGMENTS)
SEGMENT_COLORS = (SEGMENT_COLORS_BASE * (NUM_SEGMENTS // len(SEGMENT_COLORS_BASE) + 1))[:NUM_SEGMENTS]


wheel_surface = None # Biến toàn cục để lưu Surface của vòng quay

current_wheel_angle = 0.0 # Góc quay hiện tại của vòng quay
is_spinning_animation = False # Trạng thái đang quay hoạt ảnh
spin_animation_end_time = 0
SPIN_ANIMATION_DURATION_MS = 2500 # Thời gian hoạt ảnh quay (ms)
SPIN_SPEED_INITIAL = 25 # Tốc độ quay ban đầu (degrees per frame)
current_spin_speed = 0.0


# --- Hàm vẽ Vòng Quay ---
def initialize_wheel():
    global wheel_surface, WHEEL_RADIUS  # Sử dụng WHEEL_RADIUS và wheel_surface như biến toàn cục

    # Tạo Surface cho vòng quay và GÁN ngay cho biến toàn cục wheel_surface
    # Dòng này phải được thực thi thành công trước khi vẽ
    try:
        wheel_surface = pygame.Surface((WHEEL_RADIUS * 2, WHEEL_RADIUS * 2), pygame.SRCALPHA)
        print(f"DEBUG: Successfully created wheel_surface: {wheel_surface}") # Debug creation
    except Exception as e:
        print(f"ERROR: Failed to create wheel_surface: {e}") # Debug creation failure
        wheel_surface = None # Ensure it's None if creation fails
        return # Stop initialize if surface creation failed


    num_segments_wheel = len(game_config.WHEEL_SEGMENTS)
    if num_segments_wheel == 0:  # Tránh chia cho 0 nếu không có segment
        print("[CLIENT_ERROR] Không có segment nào trong WHEEL_SEGMENTS!")
        return

    angle_per_segment = 360 / num_segments_wheel

    # Vẽ các segment
    for i in range(num_segments_wheel):
        segment_value = str(game_config.WHEEL_SEGMENTS[i])
        segment_color = SEGMENT_COLORS[i % len(SEGMENT_COLORS)]

        # Vị trí trung tâm vòng quay (trên surface wheel_surface)
        center = (WHEEL_RADIUS, WHEEL_RADIUS)
        points = [center]
        start_angle_math_deg = i * angle_per_segment
        end_angle_math_deg = (i + 1) * angle_per_segment
        
        # Số điểm phân chia segment
        step_count = max(2, int(angle_per_segment * 0.5))  # Ít nhất 2 điểm cho mỗi đoạn

        for step in range(step_count + 1):
            angle_math_deg = start_angle_math_deg + (end_angle_math_deg - start_angle_math_deg) * (step / step_count)
            angle_math_rad = math.radians(angle_math_deg)
            
            # Tính tọa độ điểm trên cung tròn (tọa độ trên surface wheel_surface)
            point_x = center[0] + int(WHEEL_RADIUS * math.cos(angle_math_rad))
            point_y = center[1] - int(WHEEL_RADIUS * math.sin(angle_math_rad)) # Pygame y ngược
            points.append((point_x, point_y))

        # Vẽ segment lên wheel_surface
        if len(points) > 2:  # Cần ít nhất 3 điểm (trung tâm + 2 điểm trên cung)
            print(f"DEBUG: Attempting to draw polygon on wheel_surface. Value: {wheel_surface}") # <-- DEBUG POINT
            if wheel_surface: # Add a check just in case
                pygame.draw.polygon(wheel_surface, segment_color, points) # <-- LỖI TẠI ĐÂY (Dòng ~380)
                pygame.draw.polygon(wheel_surface, BLACK, points, 1)  # Vẽ viền cho segment
            else:
                 print("DEBUG: wheel_surface is None inside drawing loop.") # Should not happen if creation was successful


        # Vẽ văn bản trong mỗi segment (code vẽ text giữ nguyên, nó vẽ lên wheel_surface)
        text_angle_math_deg = start_angle_math_deg + angle_per_segment / 2
        text_radius_offset = WHEEL_RADIUS * 0.65

        text_pos_math_x = text_radius_offset * math.cos(math.radians(text_angle_math_deg))
        text_pos_math_y = text_radius_offset * math.sin(math.radians(text_angle_math_deg))

        text_pos_pygame_x = center[0] + text_pos_math_x
        text_pos_pygame_y = center[1] - text_pos_math_y

        text_rotation_pygame = -text_angle_math_deg
        normalized_angle = text_angle_math_deg % 360
        if 90 < normalized_angle < 270:
            text_rotation_pygame += 180

        text_surf_orig = WHEEL_TEXT_FONT.render(segment_value, True, BLACK)
        rotated_text_surf = pygame.transform.rotate(text_surf_orig, text_rotation_pygame)

        text_rect = rotated_text_surf.get_rect(center=(text_pos_pygame_x, text_pos_pygame_y))
        if wheel_surface: # Add a check just in case
            wheel_surface.blit(rotated_text_surf, text_rect) # BLIT LÊN wheel_surface
        else:
             print("DEBUG: wheel_surface is None when blitting text.") # Should not happen
# --- Hàm vẽ giao diện game ---
# Remove the 'font' parameter from the function definition
def draw_game_screen():
    screen.fill(WHITE)

    # Remove the problematic line that redefines font locally
    font = pygame.font.SysFont('arial', 24) # REMOVE THIS LINE

    # Tiêu đề
    draw_text("CHIẾC NÓN KỲ DIỆU", TITLE_FONT, BLUE, screen, SCREEN_WIDTH // 2, 40, center_x=True)
    display_id_text = my_player_name
    # Only show (Px) if name is different from initial Px AND we know our Px id
    if my_player_server_id != "P?" and my_player_name != my_player_server_id:
         display_id_text = f"{my_player_name} ({my_player_server_id})"
    elif my_player_server_id != "P?" and my_player_name == my_player_server_id : # Show Px if name hasn't been set explicitly
         display_id_text = my_player_server_id

    draw_text(f"Bạn là: {display_id_text}", SMALL_MSG_FONT, BLACK, screen, 15, 15) # Thông tin người chơi góc trên trái

    # Chủ đề và Điểm số (Layout mới)
    category_x = 30
    score_x_start = SCREEN_WIDTH - 320
    shared_y_cat_score = 90 # Cùng một hàng Y

    # Only draw category if game has started or we have category data
    if game_started_client or (current_category and current_category != "Đang tải...") :
        draw_text(f"Chủ đề: {current_category}", CATEGORY_FONT, DARK_GRAY, screen, category_x, shared_y_cat_score)

    draw_text("Điểm số:", SCORE_FONT, BLACK, screen, score_x_start, shared_y_cat_score - 35) # Tiêu đề điểm
    for i, p_score_data in enumerate(player_scores_display):
        p_id = p_score_data.get("id", "N/A")
        p_name = p_score_data.get("name", p_id) # Use ID as default name
        p_s = p_score_data.get("score", 0)
        display_text = f"{p_name} ({p_id}): {p_s}"
        text_color = BLACK
        is_this_client_player = (p_id == my_player_server_id)
        is_current_turn_player = False

        # Determine current turn player for highlighting
        if game_started_client and not game_over_client:
             # Check if the current player data matches the turn info from server
             if player_scores_display and current_turn_player_name_from_server:
                 # Find the score data that matches the current turn player name
                 current_turn_player_data = next((item for item in player_scores_display if item.get("name") == current_turn_player_name_from_server), None)
                 if current_turn_player_data and current_turn_player_data.get("id") == p_id:
                     is_current_turn_player = True

        if is_this_client_player: text_color = DARK_GREEN
        if is_current_turn_player: text_color = GREEN if is_this_client_player else ORANGE # Your turn is bright green, others' turn is orange
        
        prefix = "-> " if is_current_turn_player else "   "
        draw_text(prefix + display_text, SCORE_FONT, text_color, screen, score_x_start, shared_y_cat_score + 35 * i, max_width=310)


    # Vẽ Vòng Quay / Màn hình chờ
    if game_started_client and not game_over_client: # Chỉ vẽ vòng quay khi game đã bắt đầu và chưa kết thúc
        draw_actual_spinning_wheel(screen)
    else: # Màn hình chờ hoặc Game Over (overlay sẽ xử lý Game Over)
         if client_socket and client_socket.fileno() != -1 :
             # Display waiting message based on state
             waiting_msg = message_log_client # Use server message as base
             if server_requesting_name:
                  waiting_msg = message_log_client # Server's specific request_name message
             elif waiting_for_game_start_after_name_sent: # After sending name, before game starts
                  waiting_msg = f"Đã gửi tên '{my_player_name}'. Đang chờ đủ người chơi và game bắt đầu..."
             elif not game_over_client: # Connected but not requesting name and game not started
                  waiting_msg = message_log_client # Usually "Đã kết nối... Đang chờ server..."

             draw_text(waiting_msg, MSG_FONT, BLACK, screen, SCREEN_WIDTH//2, WHEEL_CENTER_Y, center_x=True, center_y=True, max_width=SCREEN_WIDTH-40)
         else: # Not connected or connection lost
             draw_text(message_log_client, MSG_FONT, RED, screen, SCREEN_WIDTH//2, WHEEL_CENTER_Y, center_x=True, center_y=True, max_width=SCREEN_WIDTH-40)


    # Puzzle Display
    # Only draw puzzle if game has started or we have puzzle data
    if game_started_client or (current_puzzle_display and current_puzzle_display != "--- LOADING ---"):
        puzzle_y_start = WHEEL_CENTER_Y + WHEEL_RADIUS + 30 # Dưới vòng quay
        
        # Tính toán không gian còn lại cho puzzle
        log_area_height = 80
        effective_input_rect_top = input_rect.top - log_area_height - 10 # Vị trí Y bắt đầu của message log
        available_puzzle_height = effective_input_rect_top - puzzle_y_start - 10 # -10 để có khoảng đệm

        box_size_w = PUZZLE_FONT.size("X")[0] + 10
        box_size_h = PUZZLE_FONT.get_height() + 10
        padding = 5
        
        max_boxes_per_line = (SCREEN_WIDTH - 100) // (box_size_w + padding)
        puzzle_lines_chars = []
        current_line_chars_temp = []

        # Xử lý wrap puzzle text
        temp_puzzle_words = current_puzzle_display.split(' ')
        
        current_line_chars_temp = [] # Reset cho mỗi lần vẽ
        all_lines_for_puzzle = []

        for word_idx, word_puzzle in enumerate(temp_puzzle_words):
            # Thêm từng ký tự của từ vào dòng hiện tại để kiểm tra độ dài (bao gồm cả dấu cách nếu không phải từ đầu)
            test_line_chars = list(current_line_chars_temp)
            if current_line_chars_temp: # If not the first word on the line, add space
                 test_line_chars.append(' ')
            test_line_chars.extend(list(word_puzzle))

            if len(test_line_chars) <= max_boxes_per_line:
                if current_line_chars_temp: current_line_chars_temp.append(' ') # Add space before the word if not the first word on the line
                current_line_chars_temp.extend(list(word_puzzle))
            else: # Word makes the current line too long, move to next line
                all_lines_for_puzzle.append(list(current_line_chars_temp))
                current_line_chars_temp = []
                current_line_chars_temp.extend(list(word_puzzle)) # Start new line with this word


        if current_line_chars_temp: # Add the last line if anything is left
            all_lines_for_puzzle.append(list(current_line_chars_temp))

        puzzle_lines_chars = all_lines_for_puzzle


        total_puzzle_render_height = len(puzzle_lines_chars) * (box_size_h + padding) - padding # Adjust height calculation
        if not puzzle_lines_chars: total_puzzle_render_height = 0 # Handle empty puzzle

        # Căn giữa puzzle trong không gian cho phép
        # Ensure it doesn't go above puzzle_y_start
        current_render_y = puzzle_y_start + max(0, (available_puzzle_height - total_puzzle_render_height) // 2)
        current_render_y = max(current_render_y, puzzle_y_start) # Don't draw above the designated start


        for line_chars in puzzle_lines_chars:
            # Remove trailing spaces if any (shouldn't happen with the new logic, but as safeguard)
            while line_chars and line_chars[-1] == ' ':
                line_chars.pop()
            if not line_chars: continue # Skip empty lines

            total_line_width = len(line_chars) * (box_size_w + padding) - padding
            start_x = (SCREEN_WIDTH - total_line_width) // 2
            current_render_x = start_x
            for char_render in line_chars:
                box_rect_draw = pygame.Rect(current_render_x, current_render_y, box_size_w, box_size_h)
                if char_render == " ":
                    pass # Draw nothing for space, just advance position
                else:
                    pygame.draw.rect(screen, LIGHT_GRAY, box_rect_draw, border_radius=3)
                    pygame.draw.rect(screen, GRAY, box_rect_draw, 2, border_radius=3)
                    if char_render != '_': # Only draw the letter if it's not masked
                        draw_text(char_render, PUZZLE_FONT, BLACK, screen, box_rect_draw.centerx, box_rect_draw.centery, center_x=True, center_y=True)
                current_render_x += box_size_w + padding
            current_render_y += box_size_h + padding


    # Message Log
    log_area_height_calc = draw_text(message_log_client, MSG_FONT, BLUE, screen, SCREEN_WIDTH // 2, input_rect.top - 10 - (80/2), center_x=True, center_y=True, max_width=SCREEN_WIDTH - 40)
    log_y_pos = input_rect.top - (log_area_height_calc if log_area_height_calc > 0 else 80) - 10 # Use calculated height or a default min

    # The draw_text call for the message log needs to be positioned based on the calculated log_y_pos
    # Let's redraw the message log after calculating log_y_pos more accurately if needed, or just position it relative to input_rect.top
    # Positioning relative to input_rect.top seems safer if log height is variable.
    # The previous draw_text call for message_log_client is fine if we accept its fixed Y position relative to screen center.
    # Let's revert message log drawing to a fixed position for simplicity and avoid complex height calculations affecting other layouts.
    # log_y_pos remains the same as before, positioned relative to input_rect.top

    # draw_text(message_log_client, MSG_FONT, BLUE, screen, SCREEN_WIDTH // 2, log_y_pos + log_area_height // 2, center_x=True, center_y=True, max_width=SCREEN_WIDTH - 40)
    # Keep the original message log drawing:
    log_y_pos = input_rect.top - 80 - 10 # Revert to original fixed position calculation
    draw_text(message_log_client, MSG_FONT, BLUE, screen, SCREEN_WIDTH // 2, log_y_pos + 80 // 2, center_x=True, center_y=True, max_width=SCREEN_WIDTH - 40)


    # Input Box
    pygame.draw.rect(screen, WHITE, input_rect, border_radius=5)
    # Determine border color and text to show based on state
    border_color_input = BLACK
    text_to_show_in_input = ""
    color_for_input_text = BLACK

    if server_requesting_name:
        border_color_input = BLUE if input_active else BLACK
        text_to_show_in_input = input_text if input_text else input_placeholder_name_template.format(my_player_server_id)
        color_for_input_text = BLACK if input_text else GRAY
    elif waiting_for_game_start_after_name_sent:
        border_color_input = BLACK # Not active for input
        text_to_show_in_input = "Đang chờ game bắt đầu..."
        color_for_input_text = GRAY
    elif game_started_client and not game_over_client:
         border_color_input = BLUE if input_active else BLACK
         if is_my_turn:
             text_to_show_in_input = input_text if input_text else input_placeholder # Use dynamic placeholder from receiver thread
             color_for_input_text = BLACK if input_text else GRAY
         else: # Game started, not my turn
              text_to_show_in_input = f"Lượt của {current_turn_player_name_from_server}..." if current_turn_player_name_from_server else "Đang chờ lượt..."
              color_for_input_text = GRAY
    elif game_over_client:
        border_color_input = BLACK # Not active
        text_to_show_in_input = "Game kết thúc."
        color_for_input_text = GRAY
    else: # Initial state, or connection error
        border_color_input = BLACK # Not active
        text_to_show_in_input = message_log_client if not client_socket or client_socket.fileno() == -1 else "Đang kết nối..."
        color_for_input_text = GRAY

    pygame.draw.rect(screen, border_color_input, input_rect, 2, border_radius=5)

    # Draw the calculated text and color
    draw_text(text_to_show_in_input, INPUT_FONT, color_for_input_text, screen, input_rect.x + 10, input_rect.centery, center_y=True)


    # Buttons
    if server_requesting_name:
        # Button for confirming name is only visible when server is requesting name
        draw_button(screen, confirm_name_button_rect, "XÁC NHẬN TÊN", WHITE, GREEN, DARK_GREEN, disabled=not input_text.strip())
        # Hide other buttons in this state
    elif game_started_client and not game_over_client:
        # Game started, show game action buttons
        is_action_disabled = not is_my_turn or is_spinning_animation # Vô hiệu hóa nút khi không phải lượt hoặc đang quay
        can_guess_letter = input_text.strip() and len(input_text.strip()) == 1 and input_text.strip().isalnum()
        can_solve_puzzle = input_text.strip() and len(input_text.strip()) > 1
        
        draw_button(screen, spin_button_rect, "QUAY NÓN", WHITE, GREEN, DARK_GREEN, disabled=is_action_disabled)
        draw_button(screen, guess_letter_button_rect, "ĐOÁN CHỮ", WHITE, ORANGE, (200,120,0), disabled=is_action_disabled or not can_guess_letter)
        draw_button(screen, solve_puzzle_button_rect, "GIẢI Ô CHỮ", WHITE, RED, DARK_RED, disabled=is_action_disabled or not can_solve_puzzle)
    # No buttons drawn in waiting state after sending name or game over state (except ESC to quit handled by event)


    # Game Over Message (Overlay)
    if game_over_client:
        overlay_sfc = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay_sfc.fill((0,0,0, 180)) # Semi-transparent black
        screen.blit(overlay_sfc, (0,0))
        
        winner_name_display = "Không có ai"
        if winner_client_id:
            # Find winner name from the last received scores list
            for p_score in player_scores_display:
                if p_score.get("id") == winner_client_id:
                    winner_name_display = p_score.get("name", winner_client_id)
                    break
        
        winner_text_line = f"NGƯỜI CHIẾN THẮNG: {winner_name_display}!" if winner_client_id and winner_client_id != "Không có ai" else "TRÒ CHƠI KẾT THÚC!"
        draw_text(winner_text_line, TITLE_FONT, YELLOW, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, center_x=True, center_y=True)
        draw_text("Ấn ESC để thoát.", MSG_FONT, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30, center_x=True, center_y=True)
        
        # Display final scores
        final_score_y_pos = SCREEN_HEIGHT // 2 + 80
        if player_scores_display: # Only draw scores if we have them
            draw_text("Điểm cuối:", SCORE_FONT, WHITE, screen, SCREEN_WIDTH // 2, final_score_y_pos - 35, center_x=True)
            for i, p_score in enumerate(player_scores_display):
                p_name_final = p_score.get("name", p_score.get("id", "N/A"))
                p_s_final = p_score.get("score", 0)
                final_display_text = f"{p_name_final} ({p_score.get('id', 'N/A')}): {p_s_final}"
                draw_text(final_display_text, SCORE_FONT, WHITE, screen, SCREEN_WIDTH // 2, final_score_y_pos + 35 * i, center_x=True)


    pygame.display.flip()

# --- Main Game Loop ---
def main_client_loop(server_ip_addr_param, server_port_num_param):
    global input_text, input_active, message_log_client, server_requesting_name
    global input_placeholder, my_player_name, client_socket, waiting_for_game_start_after_name_sent
    global is_spinning_animation, spin_animation_end_time, current_wheel_angle, current_spin_speed

    if not connect_to_server(server_ip_addr_param, server_port_num_param):
        # ... (xử lý lỗi kết nối như cũ)
        error_running_loop = True
        clock_err = pygame.time.Clock()
        while error_running_loop:
            for event_err_loop in pygame.event.get():
                if event_err_loop.type == pygame.QUIT or \
                   (event_err_loop.type == pygame.KEYDOWN and event_err_loop.key == pygame.K_ESCAPE):
                    error_running_loop = False
            # Call draw_game_screen without the 'font' argument
            draw_game_screen() # Vẽ màn hình lỗi (message_log_client sẽ hiển thị lỗi)
            clock_err.tick(30)
        pygame.quit()
        sys.exit()


    if client_socket:
        client_socket.settimeout(1.0) # Giữ timeout để không block vĩnh viễn, nhưng thread vẫn block trên recv

    initialize_wheel() # Khởi tạo vòng quay một lần

    receive_thread = threading.Thread(target=receive_data_thread_func, daemon=True)
    receive_thread.start()

    running_main = True
    clock = pygame.time.Clock()

    while running_main:
        # Check connection status
        if client_socket is None or client_socket.fileno() == -1:
            message_log_client = "Mất kết nối tới server. Thoát game."
            # Hiển thị thông báo này một chút trước khi thoát
            # Call draw_game_screen without the 'font' argument
            draw_game_screen()
            pygame.time.wait(2000) # Wait 2 seconds
            running_main = False
            continue # Skip rest of loop if disconnected

        mouse_was_clicked = False
        for event_game in pygame.event.get():
            if event_game.type == pygame.QUIT:
                running_main = False
            if event_game.type == pygame.KEYDOWN:
                if event_game.key == pygame.K_ESCAPE:
                    running_main = False
                # Only process text input if input_active is True
                if input_active:
                    if event_game.key == pygame.K_RETURN:
                        if server_requesting_name:
                            if input_text.strip():
                                my_player_name = input_text.strip()
                                send_action({"type": "set_name", "name": my_player_name, "player_id": my_player_server_id})
                                # Message log and state flags updated in receive_data_thread_func upon server ack
                                # Set state to waiting after sending name
                                waiting_for_game_start_after_name_sent = True
                                server_requesting_name = False # Client is done requesting name
                                input_active = False # Deactivate input while waiting for game start
                                input_text = "" # Clear input box
                                # Server will eventually send game_update with game_started = True

                            else:
                                message_log_client = "Tên không được để trống! " # Placeholder already shows format
                        
                        elif is_my_turn and not game_over_client and game_started_client and not is_spinning_animation:
                            # Logic for sending guess based on current message log/state
                            if "Hãy đoán một chữ cái" in message_log_client or "Tiếp tục quay hoặc đoán" in message_log_client:
                                if input_text.strip() and len(input_text.strip()) == 1 and input_text.strip().isalnum():
                                    send_action({"type": "guess_letter", "letter": input_text.strip().upper()})
                                    input_text = "" # Clear input after sending
                                else:
                                     message_log_client = "Vui lòng nhập MỘT chữ cái hợp lệ và Enter, hoặc dùng nút."
                            elif "Nhập cụm từ bạn muốn giải" in input_placeholder: # Check placeholder for solve phrase state
                                 if input_text.strip() and len(input_text.strip()) > 1:
                                     send_action({"type": "solve_puzzle", "phrase": input_text.strip().upper()})
                                     input_text = "" # Clear input after sending
                                 else:
                                      message_log_client = "Vui lòng nhập cụm từ cần giải và Enter, hoặc dùng nút."
                            else: # Enter doesn't do a standard action in other states
                                message_log_client = "Sử dụng các nút để thực hiện hành động."

                        # Input text is cleared regardless of validity after pressing Enter in game turn
                        # input_text = "" # Moved clearing logic into specific action blocks

                    elif event_game.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if len(input_text) < 40: # Giới hạn độ dài input
                           input_text += event_game.unicode
            
            if event_game.type == pygame.MOUSEBUTTONDOWN:
                if event_game.button == 1: # Click chuột trái
                    mouse_was_clicked = True
                    # Check if click is inside input box
                    if input_rect.collidepoint(event_game.pos):
                        # Activate input only in specific states
                        if server_requesting_name or (is_my_turn and game_started_client and not game_over_client and not is_spinning_animation):
                            input_active = True
                        else:
                            input_active = False # Deactivate if clicked outside or in non-input state
                            # Provide feedback if clicking input when not allowed
                            if not server_requesting_name and not is_my_turn and game_started_client and not game_over_client:
                                message_log_client = "Không phải lượt của bạn để nhập."
                            elif is_spinning_animation:
                                message_log_client = "Vòng quay đang thực hiện..."
                            elif game_over_client:
                                message_log_client = "Game đã kết thúc."
                            elif not server_requesting_name and not game_started_client and not waiting_for_game_start_after_name_sent:
                                 message_log_client = "Đang chờ kết nối hoặc server yêu cầu tên."
                            elif waiting_for_game_start_after_name_sent:
                                message_log_client = "Đang chờ game bắt đầu, không nhập liệu lúc này."
                    else:
                        # Deactivate input if clicked outside the input box
                        input_active = False


        # Xử lý click nút
        if mouse_was_clicked:
            mouse_pos_now = pygame.mouse.get_pos()
            if server_requesting_name:
                if confirm_name_button_rect.collidepoint(mouse_pos_now) and input_text.strip():
                    my_player_name = input_text.strip()
                    send_action({"type": "set_name", "name": my_player_name, "player_id": my_player_server_id})
                    # State flags updated in receive_data_thread_func upon server ack
                    waiting_for_game_start_after_name_sent = True
                    server_requesting_name = False
                    input_active = False # Deactivate input
                    input_text = "" # Clear input
                # Add feedback if button clicked but input is empty
                elif confirm_name_button_rect.collidepoint(mouse_pos_now) and not input_text.strip():
                     message_log_client = "Tên không được để trống!"

            elif is_my_turn and not game_over_client and game_started_client and not is_spinning_animation:
                # Handle game action button clicks
                if spin_button_rect.collidepoint(mouse_pos_now):
                    is_spinning_animation = True
                    current_spin_speed = SPIN_SPEED_INITIAL
                    # current_wheel_angle = random.uniform(0,360) # Góc bắt đầu ngẫu nhiên cho đẹp
                    spin_animation_end_time = pygame.time.get_ticks() + SPIN_ANIMATION_DURATION_MS
                    send_action({"type": "spin_wheel"})
                    input_text = "" # Clear input after spinning
                    message_log_client = f"{my_player_name} đang quay nón..." # Client-side feedback immediately

                elif guess_letter_button_rect.collidepoint(mouse_pos_now):
                    if input_text.strip() and len(input_text.strip()) == 1 and input_text.strip().isalnum():
                        send_action({"type": "guess_letter", "letter": input_text.strip().upper()})
                        input_text = "" # Clear input after sending
                    else:
                        message_log_client = "Nhập MỘT chữ cái vào ô rồi bấm nút 'ĐOÁN CHỮ'."
                elif solve_puzzle_button_rect.collidepoint(mouse_pos_now):
                    if input_text.strip() and len(input_text.strip()) > 1:
                        send_action({"type": "solve_puzzle", "phrase": input_text.strip().upper()})
                        input_text = "" # Clear input after sending
                    else:
                        message_log_client = "Nhập cụm từ bạn muốn giải vào ô rồi bấm 'GIẢI Ô CHỮ'."

            # Provide feedback if clicking game action buttons when not allowed
            elif game_started_client and not game_over_client: # Game started but not my turn or during animation
                 buttons_to_check_disabled = [spin_button_rect, guess_letter_button_rect, solve_puzzle_button_rect]
                 for btn_r in buttons_to_check_disabled:
                    if btn_r.collidepoint(mouse_pos_now):
                        if not is_my_turn:
                             message_log_client = "Không phải lượt của bạn!"
                        elif is_spinning_animation:
                              message_log_client = "Vòng quay đang thực hiện, vui lòng chờ!"
                        break
            # No feedback needed for clicking where there are no buttons or game over state (ESC handles exit)


        # Cập nhật hoạt ảnh vòng quay
        if is_spinning_animation:
            time_now = pygame.time.get_ticks()
            if time_now < spin_animation_end_time:
                # Giảm tốc độ quay từ từ
                time_elapsed_ratio = (time_now - (spin_animation_end_time - SPIN_ANIMATION_DURATION_MS)) / SPIN_ANIMATION_DURATION_MS
                # current_spin_speed = SPIN_SPEED_INITIAL * (1 - time_elapsed_ratio) # Tuyến tính
                current_spin_speed = SPIN_SPEED_INITIAL * math.pow(max(0, 1 - time_elapsed_ratio), 2) # Giảm dần (ease-out quadratic), max(0,...) prevents negative speed
                current_spin_speed = max(0.1, current_spin_speed) # Tốc độ tối thiểu để tránh đứng yên quá sớm

                current_wheel_angle = (current_wheel_angle + current_spin_speed) % 360
            else:
                is_spinning_animation = False
                current_spin_speed = 0 # Stop rotation completely after animation
                # Server will send game_update with spin result and next turn info

        # Drawing happens every frame
        # Call draw_game_screen without the 'font' argument
        draw_game_screen()

        # Cap the frame rate
        clock.tick(30)

    # --- Clean up before quitting ---
    if client_socket and client_socket.fileno() != -1:
        try:
            send_action({"type": "disconnect"}) # Inform server about disconnection
            time.sleep(0.1) # Give a moment for the message to be sent
        except Exception as e:
            print(f"[CLIENT_ERROR] Lỗi gửi disconnect message: {e}")
        finally:
            client_socket.close()
            print("[CLIENT] Socket đóng.")

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    default_ip_main = "127.0.0.1" #Mặc định là localhost
    default_port_main = game_config.SERVER_PORT

    server_ip_addr_main = default_ip_main
    server_port_val_main = default_port_main

    if len(sys.argv) >= 3:
        server_ip_addr_main = sys.argv[1]
        try:
            server_port_val_main = int(sys.argv[2])
        except ValueError:
            print(f"Port không hợp lệ: '{sys.argv[2]}'. Sử dụng port mặc định {default_port_main}.")
            server_port_val_main = default_port_main
    elif len(sys.argv) == 2: # Nếu chỉ có 1 arg, coi đó là IP
        server_ip_addr_main = sys.argv[1]
        server_port_val_main = default_port_main
        print(f"Sử dụng IP server: {server_ip_addr_main} và port mặc định {default_port_main}.")
    else: # Không có arg nào, hỏi người dùng
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