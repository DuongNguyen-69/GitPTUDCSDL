import socket
import threading
import tkinter as tk
import queue
import math

# Server connection settings
tcp_host = '192.168.56.1'  # IP of server machine
tcp_port = 12345

# Wheel configuration
SEGMENT_COLORS = [
    "#FF9999", "#99CCFF", "#FFCC99", "#CCFF99",
    "#99FF99", "#FF99CC", "#99FFFF", "#CC99FF"
]
SEGMENT_TEXT = ["MISS", "BANKRUPT", "DOUBLE", "100", "200", "300", "400", "500"]

class GameClientGUI:
    def __init__(self, root):
        self.root = root
        root.title("🎡 Chiếc nón kỳ diệu 🎡")
        self.queue = queue.Queue()
        self.wheel_offset = 0
        
        # Setup socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((tcp_host, tcp_port))
        threading.Thread(target=self._recv_thread, daemon=True).start()

        self._build_ui()
        root.after(100, self._process_queue)

    def _build_ui(self):
        # Name entry
        self.name_frame = tk.Frame(self.root, pady=10)
        tk.Label(self.name_frame, text="Nhập tên:").pack(side="left")
        self.name_entry = tk.Entry(self.name_frame)
        self.name_entry.pack(side="left", padx=5)
        tk.Button(self.name_frame, text="Tham gia", command=self.send_name).pack(side="left")
        self.name_frame.pack()

        # Main game frame
        self.game_frame = tk.Frame(self.root)

        # Player info
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

        # Question and masked word
        self.question_label = tk.Label(self.game_frame, text="Câu hỏi: ---", font=("Arial",14))
        self.word_label = tk.Label(self.game_frame, text="Từ khóa: ---", font=("Arial",14))
        self.question_label.pack()
        self.word_label.pack()

        # Wheel canvas
        self.canvas = tk.Canvas(self.game_frame, width=300, height=300, bg="#f8f8f8")
        self.canvas.pack(pady=10)
        cx, cy = 150, 150
        # Draw wheel segments
        self.draw_wheel()
        # Pointer at top center
        self.canvas.create_polygon(
            cx-10, 0,
            cx+10, 0,
            cx, 20,
            fill="red", tags="pointer"
        )
        self.canvas.tag_raise("pointer")

        # Spin button and result label
        self.spin_btn = tk.Button(self.game_frame, text="🔄 Quay nón", font=("Arial",12), state="disabled", command=self.request_spin)
        self.spin_btn.pack()
        self.spin_result = tk.Label(self.game_frame, text="", font=("Arial",12,"italic"))
        self.spin_result.pack()

        # Guess entry
        guess_frame = tk.Frame(self.game_frame)
        tk.Label(guess_frame, text="Đoán:").pack(side="left")
        self.guess_entry = tk.Entry(guess_frame, state="disabled")
        self.guess_entry.pack(side="left", padx=5)
        self.guess_btn = tk.Button(guess_frame, text="Gửi", state="disabled", command=self.send_guess)
        self.guess_btn.pack(side="left")
        guess_frame.pack(pady=5)

        # Message log area
        self.log = tk.Text(self.game_frame, height=8, state="disabled", wrap="word")
        self.log.pack(pady=5)

    def send_name(self):
        name = self.name_entry.get().strip()
        if not name:
            return
        self.sock.sendall(name.encode())
        self.name_frame.pack_forget()
        self.game_frame.pack(padx=10, pady=10)
        self._log(f"Bạn đã tham gia với tên: {name}")

    def draw_wheel(self):
        self.canvas.delete("seg")
        cx, cy, r = 150, 150, 130
        for i in range(8):
            start = (self.wheel_offset + i*45) % 360
            color = SEGMENT_COLORS[i]
            self.canvas.create_arc(
                cx-r, cy-r, cx+r, cy+r,
                start=start, extent=45,
                fill=color, outline="white", width=2, tags="seg"
            )
            # text position
            mid = math.radians(start + 22.5)
            tx = cx + (r-50)*math.cos(mid)
            ty = cy - (r-50)*math.sin(mid)
            self.canvas.create_text(
                tx, ty, text=SEGMENT_TEXT[i],
                font=("Arial",10,"bold"), tags="seg"
            )

    def request_spin(self):
        self.sock.sendall(b"\n")
        self.spin_btn.config(state="disabled")
        self.spin_result.config(text="Quay...")
        self.guess_entry.config(state="normal")
        self.guess_btn.config(state="normal")

    def animate_to(self, index):
        pointer_angle = 90
        center_angle = index*45 + 22.5
        target = (pointer_angle - center_angle) % 360
        delta = (target - self.wheel_offset) % 360
        spins = 3*360
        total = spins + delta
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
                line=line.strip()
                if not line: continue
                if line.startswith("Câu hỏi:"):
                    self.question_label.config(text=line)
                elif line.startswith("Từ khóa:") or line.startswith("Từ hiện tại:"):
                    # Cập nhật ô từ khóa cho cả gợi ý và sau đoán
                    self.word_label.config(text=line)
                elif "Lượt của bạn" in line:
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
                elif line.startswith("Đoán sai") or line.startswith("Đoán đúng"):
                    self._log(line)
                elif line.startswith("KẾT THÚC TRÒ CHƠI"):
                    self._log("Game Over!")
        self.root.after(100, self._process_queue)

    def _handle_score(self, line):
        # Ví dụ: 'Điểm Alice: 300'
        self._log(line)
        try:
            _,rest=line.split('Điểm ',1)
            name,sc=rest.split(':',1)
            for i,pl in enumerate(self.player_labels):
                if pl.cget('text')==name.strip() or pl.cget('text')==f'Player {i+1}':
                    pl.config(text=name.strip())
                    self.score_labels[i].config(text=f'Score: {sc.strip()}')
        except:
            pass

    def _log(self, msg):
        self.log.config(state='normal')
        self.log.insert('end', msg + '\n')
        self.log.see('end')
        self.log.config(state='disabled')

if __name__ == '__main__':
    root=tk.Tk()
    GameClientGUI(root)
    root.mainloop()
