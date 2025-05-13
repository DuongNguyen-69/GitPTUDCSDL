import socket
import threading
import tkinter as tk
import queue
import math
import datetime
from tkinter import ttk
from tkinter import messagebox

HOST = '192.168.56.1'
PORT = 12345

SEGMENT_COLORS = [
    "#FF9999", "#99CCFF", "#FFCC99", "#CCFF99",
    "#99FF99", "#FF99CC", "#99FFFF", "#CC99FF"
]
SEGMENT_TEXT = ["MISS", "BANKRUPT", "DOUBLE", "100", "200", "300", "400", "500"]

class GameClientGUI:
    def __init__(self, root):
        self.root = root
        root.title("🌡 Chiếc nón kỳ diệu 🌡")
        self.queue = queue.Queue()
        self.log_file = open("game_log.txt", "a", encoding="utf-8")  # Tạo hoặc mở file log
        self.wheel_offset = 0

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        threading.Thread(target=self._recv_thread, daemon=True).start()

        self._build_ui()
        root.after(100, self._process_queue)

    def _build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        
        self.play_tab = tk.Frame(self.notebook)
        self._build_game_tab(self.play_tab)
        self.notebook.add(self.play_tab, text="🎮 Trò chơi")

        self.rank_tab = tk.Frame(self.notebook)
        self._build_rank_tab(self.rank_tab)
        self.notebook.add(self.rank_tab, text="🏆 Bảng xếp hạng")

        self.notebook.pack(expand=1, fill="both")

    def _build_game_tab(self, parent):
        self.name_frame = tk.Frame(parent, pady=10)
        tk.Label(self.name_frame, text="Nhập tên:").pack(side="left")
        self.name_entry = tk.Entry(self.name_frame)
        self.name_entry.pack(side="left", padx=5)
        tk.Button(self.name_frame, text="Tham gia", command=self.send_name).pack(side="left")
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

        self.turn_label = tk.Label(self.game_frame, text="Đến lượt: ---", font=("Arial",14))
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

        self.spin_btn = tk.Button(self.game_frame, text="🔄 Quay nón", font=("Arial",12), state="disabled", command=self.request_spin)
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

        self.log = tk.Text(self.game_frame, height=8, state="disabled", wrap="word")
        self.log.pack(pady=5)

        self.game_frame.pack(padx=10, pady=10)

    def _build_rank_tab(self, parent):
        self.rank_listbox = tk.Listbox(parent, font=("Arial", 12), height=10, width=40)
        self.rank_listbox.pack(pady=20)

    def send_name(self):
        name = self.name_entry.get().strip()
        if not name:
            return
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
        guess = self.guess_entry.get().strip()
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
                    self.turn_label.config(text=f"Đến lượt: {self.player_name}")
                    self.spin_btn.config(state="normal")
                    self._log(line)
                elif "quay nón và được:" in line:
                    self.spin_result.config(text=line)
                    self._log(line)
                    res = line.split(":",1)[1].strip()
                    if res in SEGMENT_TEXT:
                        self.animate_to(SEGMENT_TEXT.index(res))
                elif line.startswith("Có ") or line.startswith("Không có "):
                    self._log(line)
                elif line.startswith("Điểm"):
                    self._handle_score(line)
                elif line.startswith("KẾT THÚC TRÒ CHƠI"):
                    self._show_victory_message(line)
                elif "Đoán đúng" in line:
                    self._log(f"🎉 Bạn đã đoán đúng! {line}")
                    self._show_victory_message("🎉 Chúc mừng, bạn đã đoán đúng!")
                else:
                    self._log(line)
        self.root.after(100, self._process_queue)

    def _handle_score(self, line):
        try:
            _, rest = line.split('Điểm ', 1)
            name, sc = rest.split(':', 1)
            for i, pl in enumerate(self.player_labels):
                if pl.cget('text') == name.strip() or pl.cget('text') == f'Player {i+1}':
                    pl.config(text=name.strip())
                    self.score_labels[i].config(text=f'Score: {sc.strip()}')
        except:
            pass

    def _update_rankings(self, line):
        self.rank_listbox.delete(0, tk.END)
        rankings = ["Player 1: 1000 điểm", "Player 2: 900 điểm"]
        for rank in rankings:
            self.rank_listbox.insert(tk.END, rank)

    def _log(self, msg):
        self.log.config(state='normal')
        self.log.insert('end', msg + '\n')
        self.log.see('end')
        self.log.config(state='disabled')

    def _show_victory_message(self, message):
        messagebox.showinfo("🎉 Chúc mừng!", message)
    def _log(self, msg):
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")  # định dạng thời gian
        full_msg = f"{timestamp} {msg}"
    
        # Hiển thị trên giao diện
        self.log.config(state='normal')
        self.log.insert('end', full_msg + '\n')
        self.log.see('end')
        self.log.config(state='disabled')

    # Ghi ra file log
        with open("game_log.txt", "a", encoding="utf-8") as f:
            f.write(full_msg + '\n')


if __name__ == '__main__':
    root = tk.Tk()
    app = GameClientGUI(root)

    def on_close():
        app.log_file.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()