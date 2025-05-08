# client.py - Code đã điều chỉnh xử lý ngắt kết nối và _recv_loop
# combined_client.py
import socket
import threading
import tkinter as tk
import queue
import math
import json # Sử dụng JSON để trao đổi dữ liệu có cấu trúc
import time # Dùng cho animation
import select # Dùng để kiểm tra dữ liệu đến mà không chặn
from tkinter import messagebox # Import messagebox

# Lớp GameClient từ client.py
class GameClient:
    """
    Handles network communication with the game server.
    """
    def __init__(self, host, port, on_message, on_disconnect): # Thêm callback khi ngắt kết nối
        self.sock = None # Khởi tạo sock là None
        self.host = host
        self.port = port
        self.on_message = on_message
        self.on_disconnect = on_disconnect # Lưu callback ngắt kết nối
        self.connected = False # Cờ trạng thái kết nối

        # Attempt to connect
        self._connect()

    def _connect(self):
        """Attempts to connect to the server."""
        print(f"Attempting to connect to server at {self.host}:{self.port}") # Log
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.sock.setblocking(False) # Đặt socket non-blocking
            self.connected = True
            # Start a thread to continuously receive data from the server
            threading.Thread(target=self._recv_loop, daemon=True).start()
            print(f"Connected to server at {self.host}:{self.port}")
            # Thông báo kết nối thành công qua queue của GUI
            self.on_message(json.dumps({"type": "MESSAGE", "data": f"Đã kết nối đến server {self.host}:{self.port}"}))
        except ConnectionRefusedError:
            print(f"Connection refused. Make sure the server is running on {self.host}:{self.port}")
            self.connected = False
            # Gửi tin nhắn lỗi đến queue của GUI để hiển thị cho người dùng
            self.on_message(json.dumps({"type": "ERROR", "data": "Không thể kết nối đến server. Server có đang chạy không?"}))
            # socket không được tạo, không cần đóng hay gán None cho self.sock ở đây.
            self.on_disconnect() # Call disconnect handler on connection failure
        except Exception as e:
            print(f"Error during connection: {e}")
            self.connected = False
            self.on_message(json.dumps({"type": "ERROR", "data": f"Lỗi kết nối: {e}"}))
            if self.sock: # Ensure sock is closed if created but connection failed later
                 try: self.sock.close()
                 except: pass
            self.sock = None # Ensure self.sock is None on failed connection
            self.on_disconnect() # Call disconnect handler on connection failure


    def _recv_loop(self):
        """
        Receives data from the server in a loop.
        Robustly handles socket validity and cleanup.
        This thread is responsible for closing the socket and setting self.sock = None.
        """
        print("_recv_loop started.") # Log start of receive loop
        # Initial check
        if not self.sock:
            print("_recv_loop exiting: self.sock is None at start.")
            self.connected = False # Ensure state consistency
            self.on_disconnect() # Call disconnect handler
            return

        buffer = ""
        # Loop while client is considered connected AND the socket object is not None
        # The loop will exit when self.connected is set to False or self.sock becomes None
        while self.connected and self.sock is not None:
            try:
                 # Use select with exception handling for ValueError and OSError
                 try:
                     # Check sock validity right before select
                     if self.sock is None:
                          print("_recv_loop exiting: self.sock became None unexpectedly before select.")
                          self.connected = False # Ensure state is consistent
                          break # Thoát vòng lặp nếu socket đã bị đóng/invalid

                     # Using select with a timeout to allow checking the loop condition periodically
                     ready_to_read, _, _ = select.select([self.sock], [], [], 0.1)

                 except (ValueError, OSError) as e:
                     # Bắt ValueError từ select (thường do socket bị đóng) và các lỗi OSError khác
                     print(f"Select error in _recv_loop: {e}")
                     self.connected = False # Indicate disconnection
                     # No need to explicitly break here, the while condition will be checked next
                     continue # Continue to check loop condition

                 if ready_to_read:
                    # Check sock validity right before recv
                    if self.sock is None:
                         print("_recv_loop exiting: self.sock became None unexpectedly before recv.")
                         self.connected = False # Ensure state is consistent
                         break # Thoát vòng lặp nếu socket đã bị đóng/invalid

                    # Receive data
                    data = self.sock.recv(4096)
                    if not data:
                        # recv returning empty data means the peer closed the connection gracefully
                        print("Server disconnected (recv returned empty).")
                        self.on_message(json.dumps({"type": "ERROR", "data": "Server đã ngắt kết nối."}))
                        self.connected = False # Indicate disconnection
                        # Loop condition will be false, leading to exit after processing remaining buffer
                        if buffer:
                             print(f"Processing remaining buffer before exit: {buffer}") # Log
                             while "\n" in buffer:
                                 line, buffer = buffer.split("\n", 1)
                                 self.on_message(line)
                             buffer = "" # Clear buffer after processing
                        break # Thoát vòng lặp sau khi xử lý ngắt kết nối


                    buffer += data.decode('utf-8') # Decode dữ liệu nhận được
                    # Xử lý các tin nhắn đầy đủ được phân tách bằng ký tự xuống dòng
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        self.on_message(line) # Đưa tin nhắn hoàn chỉnh vào queue của GUI

            # Xử lý các lỗi kết nối cụ thể xảy ra trong recv
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as e:
                 print(f"Connection error during receive: {e}")
                 self.on_message(json.dumps({"type": "ERROR", "data": f"Kết nối bị lỗi: {e}"}))
                 self.connected = False # Indicate disconnection
            # Bắt các ngoại lệ khác không mong muốn
            except Exception as e:
                print(f"Unexpected error during receive loop: {e}")
                self.on_message(json.dumps({"type": "ERROR", "data": f"Lỗi trong quá trình nhận dữ liệu: {e}"}))
                self.connected = False # Indicate disconnection


        # --- Khối finally: Đảm bảo dọn dẹp socket và gọi callback ngắt kết nối ---
        print("_recv_loop is finishing.") # Log khi vòng lặp kết thúc

        if self.sock is not None:
             print("Attempting to close socket in _recv_loop cleanup.") # Log dọn dẹp
             try:
                  self.sock.close() # Đóng socket resource
                  print("Socket closed successfully in _recv_loop cleanup.")
             except Exception as e:
                  print(f"Error during socket close in _recv_loop cleanup: {e}")
             finally:
                 # Đảm bảo self.sock được đặt về None sau khi cố gắng đóng, bất kể lỗi
                 self.sock = None

        print("Calling on_disconnect handler from _recv_loop.") # Log gọi callback
        self.on_disconnect() # Notify GUI thread
        print("_recv_loop exited.") # Log khi luồng nhận kết thúc


    def send(self, msg_json_string: str):
        """
        Sends a message (JSON string) to the server.
        Called from GUI thread.
        """
        if self.sock is None or not self.connected: 
            print("Cannot send data, socket is not available or not connected.")
            return

        try:
            if not msg_json_string.endswith("\n"):
                msg_json_string += "\n"
            self.sock.sendall(msg_json_string.encode('utf-8'))
        except Exception as e:
            print(f"Error sending data: {e}")
            pass 

    def close(self):
        """
        Signals the receive loop to stop and eventually close the socket connection.
        Called from GUI thread (e.g., on_close).
        """
        print("Client.close() called.") # Log
        # Đặt cờ kết nối thành False để báo hiệu cho luồng nhận dữ liệu dừng lại.
        # Luồng _recv_loop sẽ phát hiện điều này, thoát khỏi vòng lặp của nó,
        # và sau đó đóng socket trong khối finally của nó.
        self.connected = False
        
        print("Client.close() has set self.connected to False. _recv_loop will handle socket closure.")


# Các hằng số cho GUI
HOST = '127.0.0.1' 
PORT = 12345
SEGMENT_COLORS = [
    "#FF9999", "#99CCFF", "#FFCC99", "#CCFF99",
    "#99FF99", "#FF99CC", "#99FFFF", "#CC99FF"
]
SEGMENT_TEXT = ["MISS", "BANKRUPT", "DOUBLE", "100", "200", "300", "400", "500"]
SEGMENT_VALUES = [0, 0, 0, 100, 200, 300, 400, 500] 


# Lớp GameClientGUI từ client_gui.py, tích hợp GameClient
class GameClientGUI:
    """
    GUI for the game client.
    """
    def __init__(self, root):
        self.root = root
        root.title("🎡 Chiếc nón kỳ diệu 🎡")
        root.geometry("600x650") 
        root.resizable(True, True) 

        self.queue = queue.Queue()
        self.client = None 

        self.wheel_offset = 0
        self.spinning = False 
        self.player_name = "" 
        self.can_solve = False
        
        self._build_ui() 

        root.after(100, self._process_queue)
        self._connect_client()


    def _build_ui(self):
        """
        Builds the main user interface.
        """
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(expand=True, fill="both")

        self.name_frame = tk.Frame(main_frame)
        tk.Label(self.name_frame, text="Nhập tên:", font=("Arial", 12)).pack(side="left")
        self.name_entry = tk.Entry(self.name_frame, font=("Arial", 12))
        self.name_entry.pack(side="left", padx=5)
        tk.Button(self.name_frame, text="Tham gia", command=self.send_name, font=("Arial", 12)).pack(side="left")
        self.connect_btn = tk.Button(self.name_frame, text="Kết nối", command=self._connect_client, font=("Arial", 12))
        self.connect_btn.pack(side="left", padx=5)
        self.name_frame.pack(pady=10)

        self.game_frame = tk.Frame(main_frame)

        self.info_frame = tk.Frame(self.game_frame)
        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_columnconfigure(1, weight=1)

        self.player_labels, self.score_labels, self.error_labels = [], [], [] 
        for i in range(2):
            player_info_frame = tk.LabelFrame(self.info_frame, text=f"Người chơi {i+1}", font=("Arial", 12, "bold"), padx=10, pady=10)
            lbl = tk.Label(player_info_frame, text=f"Tên: Chờ...", font=("Arial", 12))
            sc = tk.Label(player_info_frame, text="Điểm: 0", font=("Arial", 12), fg="green")
            err = tk.Label(player_info_frame, text="Lỗi: 0", font=("Arial", 12), fg="red") 
            lbl.pack(anchor="w")
            sc.pack(anchor="w")
            err.pack(anchor="w") 
            player_info_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self.player_labels.append(lbl)
            self.score_labels.append(sc)
            self.error_labels.append(err) 
        self.info_frame.pack(pady=5, fill="x") 

        puzzle_frame = tk.Frame(self.game_frame)
        self.question_label = tk.Label(puzzle_frame, text="Câu hỏi: ---", font=("Arial", 12, "bold"), wraplength=550, justify="center") 
        self.word_label = tk.Label(puzzle_frame, text="Từ khóa: ---", font=("Arial", 16, "bold"), fg="blue") 
        self.question_label.pack(pady=5); self.word_label.pack(pady=5)
        puzzle_frame.pack(pady=10)

        self.canvas = tk.Canvas(self.game_frame, width=300, height=300, bg="#f8f8f8", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.draw_wheel(); 


        self.canvas.create_polygon(140, 10, 160, 10, 150, 30, fill="red", tags="pointer")
        self.canvas.tag_raise("pointer")

        control_frame = tk.Frame(self.game_frame)
        self.spin_btn = tk.Button(control_frame, text="🔄 Quay nón", state="disabled", command=self.request_spin, font=("Arial", 12), bg="lightblue", fg="black", activebackground="cyan") 
        self.spin_btn.pack(side="left", padx=5) 

        guess_input_frame = tk.Frame(control_frame)
        tk.Label(guess_input_frame, text="Đoán:", font=("Arial", 12)).pack(side="left")
        self.guess_entry = tk.Entry(guess_input_frame, state="disabled", font=("Arial", 12), width=15) 
        self.guess_entry.pack(side="left", padx=5)
        self.guess_btn = tk.Button(guess_input_frame, text="Gửi", state="disabled", command=self.send_guess, font=("Arial", 12), activebackground="lightgreen")
        self.guess_btn.pack(side="left")
        guess_input_frame.pack(side="left", padx=5) 

        self.solve_btn = tk.Button(control_frame, text="✅ Giải ô chữ", state="disabled", command=self.request_solve, font=("Arial", 12), bg="lightgreen", fg="black", activebackground="lime") 
        self.solve_btn.pack(side="left", padx=5) 

        control_frame.pack(pady=10)

        self.spin_result = tk.Label(self.game_frame, text="", font=("Arial", 12,"italic"), fg="purple"); self.spin_result.pack() 

        self.log = tk.Text(self.game_frame, height=8, state="disabled", wrap="word", font=("Arial", 10), bg="#e0e0e0"); self.log.pack(pady=10, fill="x", expand=True)

        self.name_entry.bind("<Return>", lambda event=None: self.send_name())
        self.guess_entry.bind("<Return>", lambda event=None: self.send_guess())

        self._update_button_states()


    def _connect_client(self):
        """Creates and attempts to connect the GameClient."""
        if self.client and self.client.connected:
             self._log("Đã kết nối đến server rồi.")
             return
        if self.client and (not self.client.connected or self.client.sock is None):
             print("Client object exists but not connected or sock is None. Cleaning up before reconnect.") 
             self.client = None 

        print("Creating new GameClient instance.") 
        self.client = GameClient(HOST, PORT, self.queue.put, self.handle_disconnect)
        self._update_button_states() 


    def _update_button_states(self):
        """Updates the state of UI buttons based on connection status."""
        is_connected = self.client and self.client.connected
        self.name_entry.config(state="normal" if is_connected and not self.player_name else "disabled")
        if self.name_frame.winfo_children(): 
            self.name_frame.winfo_children()[2].config(state="normal" if is_connected and not self.player_name else "disabled") 
        self.connect_btn.config(state="normal" if not is_connected else "disabled") 

        game_frame_is_mapped = False
        try:
            if self.game_frame and self.game_frame.winfo_exists(): 
                 game_frame_is_mapped = self.game_frame.winfo_ismapped()
        except:
             pass

        if not is_connected or not game_frame_is_mapped:
             self.spin_btn.config(state="disabled")
             self.guess_entry.config(state="disabled")
             self.guess_btn.config(state="disabled")
             self.solve_btn.config(state="disabled")
             self.can_solve = False


    def send_name(self):
        """
        Sends the player's name to the server.
        """
        name = self.name_entry.get().strip()
        if not self.client or not self.client.connected:
             self._show_error("Không kết nối đến server. Vui lòng thử kết nối lại.")
             self._log("Không thể gửi tên. Server không kết nối.")
             return
        if self.player_name: 
             self._log("Bạn đã tham gia trò chơi rồi.")
             return

        if name:
            self.player_name = name 
            message = {"type": "NAME", "data": name}
            self.client.send(json.dumps(message))
            self.name_frame.pack_forget() 
            self.game_frame.pack(padx=10, pady=10, expand=True, fill="both") 
            self._log(f"Đã gửi tên '{name}'. Đang chờ người chơi khác và bắt đầu game...")
            self._update_button_states() 
        else:
             self._log("Vui lòng nhập tên của bạn.")


    def draw_wheel(self):
        """
        Draws the spinning wheel on the canvas.
        """
        if not hasattr(self, 'canvas') or not self.canvas or not self.canvas.winfo_exists():
            print("Warning: canvas not available for drawing wheel.")
            return

        self.canvas.delete("seg") 
        cx,cy,r = 150,150,130 
        num_segments = len(SEGMENT_COLORS)
        angle_per_segment = 360 / num_segments
        for i in range(num_segments):
            start_angle = (90 - (i * angle_per_segment) - self.wheel_offset) % 360
            extent_angle = angle_per_segment

            self.canvas.create_arc(cx-r, cy-r, cx+r, cy+r,
                                    start=start_angle, extent=extent_angle,
                                    fill=SEGMENT_COLORS[i], outline="white", width=2, tags="seg")

            text_angle_deg = (self.wheel_offset + i * angle_per_segment + angle_per_segment / 2) % 360
            text_angle_rad = math.radians(text_angle_deg)

            text_radius = r - 30 
            tx = cx + text_radius * math.cos(text_angle_rad)
            ty = cy - text_radius * math.sin(text_angle_rad) 
            rotation_angle = -(text_angle_deg - 90) 

            if self.canvas.winfo_exists():
                 self.canvas.create_text(tx, ty, text=SEGMENT_TEXT[i], font=("Arial", 9, "bold"), tags="seg", angle=rotation_angle) 

        if self.canvas.winfo_exists():
            self.canvas.tag_raise("pointer") 


    def request_spin(self):
        """
        Sends a spin action request to the server.
        """
        if not self.client or not self.client.connected or self.spinning:
             if not self.client or not self.client.connected:
                  self._show_error("Không kết nối đến server.")
                  self._log("Không thể gửi yêu cầu quay. Mất kết nối.")
             elif self.spinning:
                  self._log("Bánh xe đang quay, vui lòng chờ.")
             return 

        message = {"type": "ACTION", "data": "SPIN"}
        self.client.send(json.dumps(message))
        self.spin_btn.config(state="disabled")
        self.guess_entry.config(state="disabled")
        self.guess_btn.config(state="disabled")
        self.solve_btn.config(state="disabled")
        self.can_solve = False 
        self.spin_result.config(text="Đang quay...")
        self.spinning = True 
        self._log("Đã gửi yêu cầu quay nón.")


    def request_solve(self):
        """
        Sends a solve action request to the server.
        """
        solve_guess = self.guess_entry.get().strip()
        if not solve_guess:
             self._log("Vui lòng nhập từ khóa để giải.")
             return
        if not self.client or not self.client.connected:
             self._show_error("Không kết nối đến server.")
             self._log("Không thể gửi yêu cầu giải. Mất kết nối.")
             return
        if not self.can_solve:
             self._log("Bạn không có quyền giải ô chữ lúc này.") 
             return

        message = {"type": "ACTION", "data": f"SOLVE:{solve_guess}"}
        self.client.send(json.dumps(message))
        self.guess_entry.delete(0, 'end')
        self.spin_btn.config(state="disabled")
        self.guess_entry.config(state="disabled")
        self.guess_btn.config(state="disabled")
        self.solve_btn.config(state="disabled")
        self.can_solve = False 
        self._log(f"Đã gửi giải ô chữ: {solve_guess}")


    def send_guess(self):
        """
        Sends a guess (letter or word) action request to the server.
        """
        g = self.guess_entry.get().strip()
        if not g:
             self._log("Vui lòng nhập chữ cái hoặc từ khóa để đoán.")
             return
        if not self.client or not self.client.connected:
             self._show_error("Không kết nối đến server.")
             self._log("Không thể gửi yêu cầu đoán. Mất kết nối.")
             return

        if len(g) == 1 and g.isalpha():
             message = {"type": "ACTION", "data": f"GUESS_LETTER:{g.lower()}"}
             self.client.send(json.dumps(message))
             self._log(f"Đã gửi đoán chữ cái: {g.upper()}")
        else:
             message = {"type": "ACTION", "data": f"GUESS_WORD:{g.lower()}"}
             self.client.send(json.dumps(message))
             self._log(f"Đã gửi đoán từ khóa: {g}")


        self.guess_entry.delete(0, 'end')
        self.spin_btn.config(state="disabled")
        self.guess_entry.config(state="disabled")
        self.guess_btn.config(state="disabled")
        self.solve_btn.config(state="disabled") 
        self.can_solve = False 


    def _process_queue(self):
        """
        Processes messages received from the server via the queue.
        """
        while not self.queue.empty():
            line = self.queue.get()
            try:
                message = json.loads(line)
                msg_type = message.get("type")
                msg_data = message.get("data")

                if msg_type == "STATE":
                    game_state_data = msg_data
                    self._update_game_state(game_state_data)

                elif msg_type == "MESSAGE":
                    self._log(msg_data)

                elif msg_type == "ERROR":
                     self._show_error(msg_data)
                     self._log(f"Lỗi từ server: {msg_data}") 

                elif msg_type == "REQUEST_NAME":
                    # Server is ready for the name.
                    # The GUI allows the user to send their name via the "Tham gia" button.
                    # No specific action needed here other than logging,
                    # and definitely DO NOT close the connection.
                    self._log("Server đã sẵn sàng. Vui lòng nhập tên của bạn và nhấn 'Tham gia'.")
                    # The _update_button_states method, called upon connection and disconnection,
                    # should ensure the name entry field and "Tham gia" button are correctly
                    # enabled when the client is connected and a name has not yet been sent.

                elif msg_type == "ACTION_CHOICE":
                    choice = msg_data
                    self._log(f"Server yêu cầu hành động: {choice}") 

                    self.spin_btn.config(state="disabled")
                    self.guess_entry.config(state="disabled")
                    self.guess_btn.config(state="disabled")
                    self.solve_btn.config(state="disabled")
                    self.can_solve = False 

                    if choice == "SPIN_OR_SOLVE":
                        self._log("Đến lượt bạn: Quay nón hoặc giải ô chữ.")
                        self.spin_btn.config(state="normal")
                        self.guess_entry.config(state="normal") 
                        self.guess_btn.config(state="normal")   
                        self.solve_btn.config(state="normal") 
                        self.can_solve = True 

                    elif choice == "GUESS_LETTER_OR_SOLVE":
                         self._log("Đến lượt bạn: Đoán một chữ cái hoặc giải ô chữ.")
                         self.guess_entry.config(state="normal") 
                         self.guess_btn.config(state="normal") 
                         self.solve_btn.config(state="normal") 
                         self.can_solve = True 

                    elif choice == "SOLVE_MANDATORY":
                         self._log("Ô chữ đã mở hết hoặc gần hết. Vui lòng giải ô chữ.")
                         self.guess_entry.config(state="normal") 
                         self.guess_btn.config(state="disabled") 
                         self.solve_btn.config(state="normal") 
                         self.can_solve = True 

                elif msg_type == "SPIN_RESULT":
                    result_text = str(msg_data) 
                    self.spin_result.config(text=f"Kết quả quay: {result_text}")
                    try:
                        result_index = SEGMENT_TEXT.index(result_text)
                        self.animate_to(result_index) 
                    except ValueError:
                        self._log(f"Kết quả quay không tìm thấy trong danh sách segment: {result_text}")
                        self.spinning = False 
            except json.JSONDecodeError:
                self._log(f"Received non-JSON message: {line}")
            except Exception as e:
                self._log(f"Error processing message in _process_queue: {e} - Message: {line}")

        self.root.after(100, self._process_queue)

    def _update_game_state(self, state_data):
        """
        Updates GUI elements based on the received game state data.
        """
        question = state_data.get("question", "---")
        self.question_label.config(text=f"Câu hỏi: {question}")

        masked_answer_str = state_data.get("masked_answer", "---")
        self.word_label.config(text=f"Từ khóa: {masked_answer_str}")

        players_data = state_data.get("players", [])
        current_turn_player_name = state_data.get("current_turn_player")
        current_game_state = state_data.get("game_state")


        for i in range(len(self.player_labels)):
            if i < len(players_data):
                player_info = players_data[i]
                self.player_labels[i].config(text=f"Tên: {player_info.get('name', 'Chờ...')}")
                self.score_labels[i].config(text=f"Điểm: {player_info.get('score', 0)}")
                self.error_labels[i].config(text=f"Lỗi: {player_info.get('errors', 0)}")

                if player_info.get('name') == current_turn_player_name and current_game_state == "PLAYING": 
                    self.player_labels[i].master.config(relief="solid", borderwidth=2, highlightbackground="blue", highlightcolor="blue")
                else:
                    self.player_labels[i].master.config(relief="flat", borderwidth=1, highlightthickness=0)
            else: 
                 self.player_labels[i].config(text=f"Tên: Chờ...")
                 self.score_labels[i].config(text=f"Điểm: 0")
                 self.error_labels[i].config(text=f"Lỗi: 0")
                 self.player_labels[i].master.config(relief="flat", borderwidth=1, highlightthickness=0) 

        if current_game_state == "WAITING_FOR_PLAYERS":
             self.spin_result.config(text="Chờ người chơi khác...") 
             self._update_button_states() 

        elif current_game_state == "PLAYING":
            self.spin_result.config(text="") 
            pass 

        elif current_game_state == "ROUND_END":
             reason = state_data.get('reason', '')
             self._log(f"Vòng chơi kết thúc: {reason}")
             self.spin_result.config(text="Vòng kết thúc") 
             self.spin_btn.config(state="disabled")
             self.guess_entry.config(state="disabled")
             self.guess_btn.config(state="disabled")
             self.solve_btn.config(state="disabled")
             self.can_solve = False
             final_answer = state_data.get("masked_answer", "") 
             if final_answer:
                  self.word_label.config(text=f"Đáp án: {final_answer}")
                  self._log(f"Đáp án của vòng là: {final_answer}")


        elif current_game_state == "GAME_END":
             reason = state_data.get('reason', '')
             self._log(f"Trò chơi kết thúc: {reason}")
             self.spin_result.config(text="Trò chơi kết thúc") 
             self.spin_btn.config(state="disabled")
             self.guess_entry.config(state="disabled")
             self.guess_btn.config(state="disabled")
             self.solve_btn.config(state="disabled")
             self.can_solve = False
             self._update_button_states() 

        if self.spinning:
             self.spin_btn.config(state="disabled")
             self.guess_entry.config(state="disabled")
             self.guess_btn.config(state="disabled")
             self.solve_btn.config(state="disabled")
             self.can_solve = False


    def animate_to(self, index):
        """
        Animates the wheel to point to the segment at the given index.
        """
        if self.spinning: 
            num_segments = len(SEGMENT_COLORS)
            angle_per_segment = 360 / num_segments
            pointer_angle = 90
            target_segment_center_angle = index * angle_per_segment + angle_per_segment / 2

            target_offset = (90 - target_segment_center_angle) % 360
            if target_offset < 0:
                target_offset += 360

            num_full_spins = 5 
            delta_to_target = (target_offset - self.wheel_offset + 360) % 360
            total_delta = num_full_spins * 360 + delta_to_target

            duration = 3000 
            start_time = time.time()
            start_offset = self.wheel_offset

            def easing_step():
                nonlocal start_time, start_offset, total_delta
                if not self.client or not self.client.connected: 
                     self.spinning = False
                     self._log("Animation dừng do mất kết nối.")
                     return
                if not hasattr(self, 'canvas') or not self.canvas or not self.canvas.winfo_exists():
                     self.spinning = False
                     print("Animation dừng: canvas không tồn tại.")
                     return


                elapsed_time = (time.time() - start_time) * 1000 
                if elapsed_time < duration:
                    t = elapsed_time / duration
                    current_delta = total_delta * (1 - (1 - t)**3)

                    self.wheel_offset = (start_offset + current_delta) % 360
                    self.draw_wheel()
                    if self.canvas.winfo_exists():
                         self.canvas.tag_raise("pointer")
                    self.root.after(20, easing_step) 
                else:
                    self.wheel_offset = target_offset
                    self.draw_wheel()
                    if self.canvas.winfo_exists():
                         self.canvas.tag_raise("pointer")
                    self.spinning = False 
                    self._log("Quay nón hoàn tất.")
            easing_step()

    def handle_disconnect(self):
        """
        Handles actions to perform when the client is disconnected from the server.
        """
        print("handle_disconnect called.") 
        # self.connected = False # This flag is managed by GameClient instance
        self.player_name = "" 

        if hasattr(self, 'game_frame') and self.game_frame:
             self.game_frame.pack_forget()
        if hasattr(self, 'name_frame') and self.name_frame:
             self.name_frame.pack(pady=10)

        self._update_button_states()


    def _log(self, msg):
        """
        Adds a message to the log text box.
        """
        if hasattr(self, 'log') and self.log and self.log.winfo_exists():
             self.log.config(state="normal")
             self.log.insert("end", msg + "\n")
             self.log.see("end") 
             self.log.config(state="disabled")
        else:
             print(f"LOG (GUI not ready): {msg}") 


    def _show_error(self, msg):
        """
        Displays an error message box.
        """
        messagebox.showerror("Lỗi", msg) 


    def on_close(self):
        """
        Handles window closing event.
        """
        print("on_close called.") # Log
        if self.client:
            self.client.close()
        self.root.destroy() 


if __name__ == '__main__':
    root = tk.Tk()
    app = GameClientGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
