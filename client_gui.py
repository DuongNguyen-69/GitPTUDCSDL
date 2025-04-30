# client_gui.py
import tkinter as tk
import queue
import math
from client import GameClient

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
        root.title("🎡 Chiếc nón kỳ diệu 🎡")
        self.queue = queue.Queue()
        self.client = GameClient(HOST, PORT, self.queue.put)
        self.wheel_offset = 0
        self._build_ui()
        root.after(100, self._process_queue)

    def _build_ui(self):
        self.name_frame = tk.Frame(self.root, pady=10)
        tk.Label(self.name_frame, text="Nhập tên:").pack(side="left")
        self.name_entry = tk.Entry(self.name_frame)
        self.name_entry.pack(side="left", padx=5)
        tk.Button(self.name_frame, text="Tham gia", command=self.send_name).pack(side="left")
        self.name_frame.pack()

        self.game_frame = tk.Frame(self.root)
        self.info_frame = tk.Frame(self.game_frame)
        self.player_labels, self.score_labels = [], []
        for i in range(2):
            lbl = tk.Label(self.info_frame, text=f"Player {i+1}", font=("Arial",12))
            sc = tk.Label(self.info_frame, text="Score: 0", font=("Arial",12), fg="green")
            lbl.grid(row=i, column=0, padx=5); sc.grid(row=i, column=1, padx=5)
            self.player_labels.append(lbl); self.score_labels.append(sc)
        self.info_frame.pack(pady=5)

        self.question_label = tk.Label(self.game_frame, text="Câu hỏi: ---", font=("Arial",14))
        self.word_label = tk.Label(self.game_frame, text="Từ khóa: ---", font=("Arial",14))
        self.question_label.pack(); self.word_label.pack()

        self.canvas = tk.Canvas(self.game_frame, width=300, height=300, bg="#f8f8f8")
        self.canvas.pack(pady=10)
        self.draw_wheel(); self.canvas.create_polygon(140,0,160,0,150,20, fill="red", tags="pointer"); self.canvas.tag_raise("pointer")

        self.spin_btn = tk.Button(self.game_frame, text="🔄 Quay nón", state="disabled", command=self.request_spin)
        self.spin_btn.pack(); self.spin_result = tk.Label(self.game_frame, text="", font=("Arial",12,"italic")); self.spin_result.pack()

        frame = tk.Frame(self.game_frame)
        tk.Label(frame, text="Đoán:").pack(side="left")
        self.guess_entry = tk.Entry(frame, state="disabled"); self.guess_entry.pack(side="left", padx=5)
        self.guess_btn = tk.Button(frame, text="Gửi", state="disabled", command=self.send_guess); self.guess_btn.pack(side="left")
        frame.pack(pady=5)

        self.log = tk.Text(self.game_frame, height=8, state="disabled", wrap="word"); self.log.pack(pady=5)

    def send_name(self):
        name = self.name_entry.get().strip()
        if name:
            self.client.send(name)
            self.name_frame.pack_forget(); self.game_frame.pack(padx=10, pady=10)
            self._log(f"Bạn đã tham gia với tên: {name}")

    def draw_wheel(self):
        self.canvas.delete("seg")
        cx,cy,r = 150,150,130
        for i in range(8):
            start = (self.wheel_offset + i*45)%360
            self.canvas.create_arc(cx-r,cy-r,cx+r,cy+r, start=start, extent=45, fill=SEGMENT_COLORS[i], outline="white", width=2, tags="seg")
            ang = math.radians(start+22.5); tx,ty = cx+(r-50)*math.cos(ang), cy-(r-50)*math.sin(ang)
            self.canvas.create_text(tx,ty, text=SEGMENT_TEXT[i], font=("Arial",10,"bold"), tags="seg")

    def request_spin(self):
        self.client.send("")
        self.spin_btn.config(state="disabled"); self.spin_result.config(text="Quay...")
        self.guess_entry.config(state="normal"); self.guess_btn.config(state="normal")

    def send_guess(self):
        g=self.guess_entry.get().strip()
        if g:
            self.client.send(g); self.guess_entry.delete(0,'end'); self.guess_entry.config(state="disabled"); self.guess_btn.config(state="disabled")

    def _process_queue(self):
        while not self.queue.empty():
            line=self.queue.get().strip()
            if line.startswith("Câu hỏi:"): self.question_label.config(text=line)
            elif line.startswith("Từ khóa:") or line.startswith("Từ hiện tại:"): self.word_label.config(text=line)
            elif "Lượt của bạn" in line: self.spin_btn.config(state="normal"); self._log(line)
            elif "quay nón và được:" in line: self.spin_result.config(text=line); self._log(line); res=line.split(":",1)[1].strip(); self.animate_to(SEGMENT_TEXT.index(res))
            elif line.startswith("Có ") or line.startswith("Không có "): self._log(line)
            elif line.startswith("Điểm"): self._log(line)
            else: self._log(line)
        self.root.after(100,self._process_queue)

    def animate_to(self,index):
        pointer=90; center=index*45+22.5; delta=(pointer-center-self.wheel_offset)%360; total=3*360+delta; step=0
        def step_anim():
            nonlocal step
            if step<total:
                inc=min(20,total-step); step+=inc; self.wheel_offset=(self.wheel_offset+inc)%360; self.draw_wheel(); self.canvas.tag_raise("pointer"); self.root.after(20,step_anim)
        step_anim()

    def _log(self,msg):
        self.log.config(state="normal"); self.log.insert("end",msg+"\n"); self.log.see("end"); self.log.config(state="disabled")

    def on_close(self):
        self.client.close(); self.root.destroy()

if __name__ == '__main__':
    root=tk.Tk(); app=GameClientGUI(root); root.protocol("WM_DELETE_WINDOW",app.on_close); root.mainloop()
