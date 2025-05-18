import socket
import threading
import tkinter as tk
import queue
import math
import datetime
from tkinter import ttk
from tkinter import messagebox

HOST = '192.168.88.169'
PORT = 12345

SEGMENT_COLORS = [
    "#FF9999", "#99CCFF", "#FFCC99", "#CCFF99",
    "#99FF99", "#FF99CC", "#99FFFF", "#CC99FF"
]
SEGMENT_TEXT = ["MISS", "BANKRUPT", "DOUBLE", "100", "200", "300", "400", "500"]

class GameClientGUI:
    def __init__(self, root):
        self.root = root
        self.my_turn = False
        self.selected_mode = None
        root.title("\ud83c\udf21 Chiếc nón kỳ diệu \ud83c\udf21")
        self.queue = queue.Queue()
        self.log_file = open("game_log.txt", "a", encoding="utf-8")
        self.wheel_offset = 0

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        threading.Thread(target=self._recv_thread, daemon=True).start()

        self._build_ui()
        root.after(100, self._process_queue)

    def select_mode(self, mode):
        self.selected_mode = mode
        self.mode_frame.pack_forget()
        self.name_frame.pack()

    def _build_ui(self):
        self.notebook = ttk.Notebook(self.root)

        self.play_tab = tk.Frame(self.notebook)
        self._build_game_tab(self.play_tab)
        self.notebook.add(self.play_tab, text="\ud83c\udfae Trò chơi")

        self.rank_tab = tk.Frame(self.notebook)
        self._build_rank_tab(self.rank_tab)
        self.notebook.add(self.rank_tab, text="\ud83c\udfc6 Bảng xếp hạng")

        self.notebook.pack(expand=1, fill="both")

    def _build_game_tab(self, parent):
        self.name_frame = tk.Frame(parent, pady=10)
        tk.Label(self.name_frame, text="Nhập tên:").pack(side="left")
        self.name_entry = tk.Entry(self.name_frame)
        self.name_entry.pack(side="left", padx=5)
        tk.Button(self.name_frame, text="Tham gia", command=self.send_name).pack(side="left")

        self.mode_frame = tk.Frame(parent, pady=10)
        tk.Label(self.mode_frame, text="Chọn chế độ chơi:").pack()
        tk.Button(self.mode_frame, text="\ud83d\udd01 Tiếp tục game", command=lambda: self.select_mode("2")).pack(side="left", padx=5)
        tk.Button(self.mode_frame, text="\ud83c\udd95 Game mới", command=lambda: self.select_mode("1")).pack(side="left", padx=5)
        self.mode_frame.pack()

        self.name_frame.pack()
        self.game_frame = tk.Frame(parent)

        self.info_frame = tk.Frame(self.game_frame)
        self.player_labels = []
        self.score_labels = []
        for i in range(2):
            name_lbl = tk.Label(self.info_frame, text=f"Player {i+1}", font=("Arial",12))
            score_lbl = tk.Label(self.info_frame, text="Score: 0", font=("Arial",12), fg="green")
            name_lbl.grid(row=i, column=0, padx=5)
            score_lbl.grid(row=i, column=1, padx=5)
            self.player_labels.append(name_lbl)
            self.score_labels.append(score_lbl)
        self.info_frame.pack(pady=5)

        self.turn_label = tk.Label(self.game_frame, text="Tên người chơi: ---", font=("Arial",14))
        self.turn_label.pack()

        self.question_label = tk.Label(self.game_frame, text="Câu hỏi: ---", font=("Arial",14))
        self.word_label = tk.Label(self.game_frame, text="Từ khóa: ---", font=("Arial",14), fg="#333")
        self.question_label.pack()
        self.word_label.pack()

        self.canvas = tk.Canvas(self.game_frame, width=300, height=300, bg="#f8f8f8")
        self.canvas.pack(pady=10)
        self.draw_wheel()
        self.canvas.create_polygon(140,0,160,0,150,20, fill="red", tags="pointer")
        self.canvas.tag_raise("pointer")

        self.spin_btn = tk.Button(self.game_frame, text="\ud83d\udd04 Quay nón", font=("Arial",12), state="disabled", command=self.request_spin)
        self.spin_btn.pack()
        self.spin_result = tk.Label(self.game_frame, text="", font=("Arial",12,"italic"))
        self.spin_result.pack()

        guess_frame = tk.Frame(self.game_frame)
        tk.Label(guess_frame, text="Đoán:").pack(side="left")
        self.guess_entry = tk.Entry(guess_frame, state="disabled")
        self.guess_entry.pack(side="left", padx=5)
        self.guess_btn = tk.Button(guess_frame, text="Gửi", state="disabled", command=self.send_guess)
        self.guess_btn.pack(side="left")
        guess_frame.pack(pady=5)

        self.log = tk.Text(self.game_frame, height=12,width=60, state="disabled", wrap="word")
        self.log.pack(pady=5)

        self.game_frame.pack(padx=10, pady=10)

    def _build_rank_tab(self, parent):
        self.rank_listbox = tk.Listbox(parent, font=("Arial", 12), height=10, width=40)
        self.rank_listbox.pack(pady=10)

        # Add reset button for leaderboard
        reset_btn = tk.Button(parent, text="🔄 Đặt lại bảng xếp hạng", command=self.reset_leaderboard, 
                           font=("Arial", 10, "bold"), bg="#F44336", fg="white")
        reset_btn.pack(pady=10)

    def send_name(self):
        name = self.name_entry.get().strip()
        if not name:
            return
        if not self.selected_mode:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn chế độ chơi trước.")
            return
        self.sock.sendall(self.selected_mode.encode())
        self.sock.sendall(name.encode())

        self.name_frame.pack_forget()
        self.game_frame.pack(padx=10, pady=10)
        self._log(f"Bạn đã tham gia với tên: {name}")
        self.player_name = name

    def draw_wheel(self):
        self.canvas.delete("seg")
        cx, cy, r = 150, 150, 130
        for i in range(8):
            start = (self.wheel_offset + i*45) % 360
            color = SEGMENT_COLORS[i]
            self.canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=start, extent=45, fill=color, outline="white", width=2, tags="seg")
            mid = math.radians(start + 22.5)
            tx = cx + (r-50)*math.cos(mid)
            ty = cy - (r-50)*math.sin(mid)
            self.canvas.create_text(tx, ty, text=SEGMENT_TEXT[i], font=("Arial",10,"bold"), tags="seg")

    def request_spin(self):
        self.sock.sendall(b"\n")
        self.spin_btn.config(state="disabled")
        self.spin_result.config(text="Quay...")
        self.guess_entry.config(state="normal")
        self.guess_btn.config(state="normal")
        self.my_turn = False

    def animate_to(self, index):
        pointer_angle = 90
        center_angle = index*45 + 22.5
        delta = (pointer_angle - center_angle - self.wheel_offset) % 360
        total = 3*360 + delta
        self._anim_step = 0
        self._anim_total = total
        self._animate_spin_step()

    def _animate_spin_step(self):
        if self._anim_step < self._anim_total:
            step = min(20, self._anim_total - self._anim_step)
            self.wheel_offset = (self.wheel_offset + step) % 360
            self.draw_wheel()
            self.canvas.tag_raise("pointer")
            self._anim_step += step
            self.root.after(20, self._animate_spin_step)

    def send_guess(self):
        guess = self.guess_entry.get().strip().lower()
        guess = guess.replace(" ", "")  # loại bỏ khoảng trắng giữa từ (phòng trường hợp sai)
        if guess:
            self.sock.sendall(guess.encode())
            self.guess_entry.delete(0, tk.END)
            self.guess_entry.config(state="disabled")
            self.guess_btn.config(state="disabled")


    def _recv_thread(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                self.queue.put(data.decode())
            except:
                break

    def _process_queue(self):
        while not self.queue.empty():
            msg = self.queue.get()
            for line in msg.splitlines():
                line = line.strip()
                if not line: continue
                if line.startswith("Câu hỏi:"):
                    self.question_label.config(text=line)
                elif line.startswith("Từ khóa:") or line.startswith("Từ hiện tại:"):
                    self.word_label.config(text=line)
                elif "Lượt của bạn" in line:
                    if hasattr(self, "player_name") and self.player_name in line:
                        self.my_turn = True
                        self.spin_btn.config(state="normal")
                        self.turn_label.config(text=f"Tên người chơi: {self.player_name}")
                        self._log(line)
                elif "quay nón và được:" in line:
                    self.spin_result.config(text=line)
                    self._log(line)
                    res = line.split(":",1)[1].strip()
                    if res in SEGMENT_TEXT:
                        self.animate_to(SEGMENT_TEXT.index(res))
                elif line.startswith("Có ") or line.startswith("Không có "):
                    self._log(line)
                elif line.startswith("Điểm") or line.startswith("Diểm") or "SCORE_UPDATE:" in line:
                    self._handle_score(line)
                elif line.startswith("KẾt thúc trò chơi") or line.startswith("KẾT THÚC TRÒ CHƠI"):
                    self._show_victory_message(line)
                elif "Đoán đúng" in line:
                    self._log(f"🎉 Bạn đã đoán đúng! {line}")
                    self._show_victory_message("🎉 Chúc mừng, bạn đã đoán đúng!")
                elif line.startswith("Trò chơi đã kết thúc") or line.startswith("TR CHƠI Đ KẾT THÚC"):
                    # Automatically send ENTER to start a new game
                    try:
                        self._log("Nhận thông báo kết thúc trò chơi. Tự động bắt đầu trò chơi mới...")
                        self.sock.sendall(b"\n")  # Send ENTER key
                    except Exception as e:
                        self._log(f"Lỗi khi bắt đầu trò chơi mới: {e}")
                elif line.startswith("HIỂN_THỊ_BXH"):
                    ranks = msg.split("\n")[1:]
                    self.rank_listbox.delete(0, tk.END)
                    for r in ranks:
                        self.rank_listbox.insert(tk.END, r.strip())
                else:
                    self._log(line)
        self.root.after(100, self._process_queue)

    def _handle_score(self, line):
        try:
            # Check if this is a score update message
            if "SCORE_UPDATE:" in line:
                # Parse the new score format: [marker]SCORE_UPDATE:name:score
                parts = line.split("SCORE_UPDATE:", 1)[1].split(":")
                if len(parts) != 2:
                    return

                name = parts[0].strip()
                score = parts[1].strip()

                # Check if this is the current player's turn
                is_current_player = "➡️" in line

                for i, lbl in enumerate(self.player_labels):
                    lbl_name = lbl.cget("text")
                    if lbl_name.lower() == name.lower() or lbl_name.lower().startswith("player"):
                        # Update player name
                        self.player_labels[i].config(text=name)

                        # Update score with visual indicator for current player
                        if is_current_player:
                            self.score_labels[i].config(text=f"Score: {score} ➡️", fg="blue", font=("Arial", 12, "bold"))
                        else:
                            self.score_labels[i].config(text=f"Score: {score}", fg="green", font=("Arial", 12))

                        break
            # For backward compatibility, also try the old format
            elif "Điểm" in line or "Diểm" in line:
                try:
                    # Try both accent variants
                    if "Điểm" in line:
                        parts = line.split("Điểm ", 1)[1].split(":", 1)
                    else:
                        parts = line.split("Diểm ", 1)[1].split(":", 1)

                    if len(parts) != 2:
                        return

                    name = parts[0].strip()
                    score = parts[1].strip()

                    for i, lbl in enumerate(self.player_labels):
                        lbl_name = lbl.cget("text")
                        if lbl_name.lower() == name.lower() or lbl_name.lower().startswith("player"):
                            self.player_labels[i].config(text=name)
                            self.score_labels[i].config(text=f"Score: {score}")
                            break
                except:
                    pass
        except Exception as e:
            print("Lỗi xử lý điểm:", e)

    def _log(self, msg):
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        full_msg = f"{timestamp} {msg}"
        self.log.config(state='normal')
        self.log.insert('end', full_msg + '\n')
        self.log.see('end')
        self.log.config(state='disabled')
        with open("game_log.txt", "a", encoding="utf-8") as f:
            f.write(full_msg + '\n')

    def _show_victory_message(self, message):
        self._show_game_end_dialog("🎉 Chúc mừng!", message)

    def reset_leaderboard(self):
        # Send a reset leaderboard request to the server
        try:
            self.sock.sendall("RESET_LEADERBOARD".encode())
            self._log("Đã gửi yêu cầu đặt lại bảng xếp hạng")
        except Exception as e:
            self._log(f"Lỗi khi đặt lại bảng xếp hạng: {e}")

    def _show_game_end_dialog(self, title, message):
        # Disable game buttons
        self.spin_btn.config(state="disabled")
        self.guess_entry.config(state="disabled")
        self.guess_btn.config(state="disabled")

        # Create a custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("450x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)  # Make dialog modal
        dialog.grab_set()  # Make dialog modal

        # Configure dialog style
        dialog.configure(bg="#f0f0f0")

        # Add message
        header_frame = tk.Frame(dialog, bg="#f0f0f0")
        header_frame.pack(fill="x", pady=10)

        tk.Label(header_frame, text="🏆 KẾT THÚC TRÒ CHƠI 🏆", 
                font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#1E88E5").pack(pady=10)

        message_frame = tk.Frame(dialog, bg="#f0f0f0")
        message_frame.pack(fill="x", padx=20)

        tk.Label(message_frame, text=message, font=("Arial", 12), 
                bg="#f0f0f0", wraplength=400, justify="center").pack(pady=10)

        # Add buttons
        button_frame = tk.Frame(dialog, bg="#f0f0f0")
        button_frame.pack(pady=20)

        def new_game():
            dialog.destroy()

            # Reset the game state by simulating a new connection
            if hasattr(self, "player_name"):
                # Send code for new game and re-send player name
                try:
                    self.sock.sendall(b"1")  # Send code for new game
                    self.sock.sendall(self.player_name.encode())  # Re-send player name
                    self._log("Bắt đầu trò chơi mới...")

                    # Reset UI elements
                    self.question_label.config(text="Câu hỏi: ---")
                    self.word_label.config(text="Từ khóa: ---")
                    self.spin_result.config(text="")

                    # Reset scores
                    for i in range(len(self.score_labels)):
                        self.score_labels[i].config(text="Score: 0", fg="green", font=("Arial", 12))
                except:
                    self._log("Lỗi khi khởi động trò chơi mới. Vui lòng khởi động lại ứng dụng.")

        def end_game():
            dialog.destroy()
            # Re-enable buttons if it's the player's turn
            if self.my_turn:
                self.spin_btn.config(state="normal")

        # Style the buttons
        new_game_btn = tk.Button(button_frame, text="🎮 Game mới", command=new_game, 
                              width=12, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white")
        new_game_btn.pack(side="left", padx=10)

        end_game_btn = tk.Button(button_frame, text="❌ Kết thúc", command=end_game, 
                              width=12, font=("Arial", 10, "bold"), bg="#F44336", fg="white")
        end_game_btn.pack(side="left", padx=10)

        # Center the dialog on the screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))

if __name__ == '__main__':
    root = tk.Tk()
    app = GameClientGUI(root)

    def on_close():
        app.log_file.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
