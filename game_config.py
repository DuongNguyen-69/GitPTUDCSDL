# game_config.py

PUZZLES = [
    {"category": "Thành ngữ", "phrase": "AN QUA NHO KE TRONG CAY"},
    {"category": "Địa danh Việt Nam", "phrase": "HO GUOM"},
    {"category": "Đồ vật", "phrase": "MAY TINH XACH TAY"},
    {"category": "Ca dao - Tục ngữ", "phrase": "CON TRAU LA DAU CO NGHIEP"},
    {"category": "Tên bài hát", "phrase": "DI DE VE NHA"},
    # Thêm nhiều câu đố khác ở đây
    {"category": "Tỉnh thành Việt Nam", "phrase": "HAI PHONG"},
    {"category": "Món ăn", "phrase": "PHO BO"},
    {"category": "Động vật", "phrase": "CON VOI"},
]

# Các giá trị trên vòng quay
WHEEL_SEGMENTS = [
    100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,
    1500, 2000, 50, "MAT LUOT", "NHAN DOI", "BANKRUPT", "MAY MAN" # Thêm ô MAY MAN
]

# Các hằng số khác
SERVER_HOST = '0.0.0.0'  # Server lắng nghe trên tất cả các interface mạng
SERVER_PORT = 12345      # Cổng mặc định cho server
MAX_PLAYERS = 2          # Số lượng người chơi tối đa
BUFFER_SIZE = 4096       # Kích thước bộ đệm nhận dữ liệu (bytes)

# Điểm thưởng thêm
BONUS_POINTS_FOR_SOLVE = 500
LUCKY_SPIN_POINTS = 250 # Điểm cho ô "MAY MAN"