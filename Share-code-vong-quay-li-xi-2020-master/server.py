import http.server
import socketserver
import os
import sys

PORT = 8000 # Bạn có thể thay đổi cổng nếu muốn, ví dụ 8080

# Cố gắng thiết lập encoding cho stdout là UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    print("Warning: Could not reconfigure stdout/stderr to UTF-8. Vietnamese characters in console output might not display correctly.")
    print("On Windows, you might need to run 'chcp 65001' in cmd before running this script.")
except Exception as e:
    print(f"Error reconfiguring stdout/stderr: {e}")


# Lấy đường dẫn đến thư mục hiện tại của file server.py
web_dir = os.path.join(os.path.dirname(__file__))
os.chdir(web_dir)

Handler = http.server.SimpleHTTPRequestHandler

# Thông báo bằng tiếng Anh để tránh lỗi UnicodeEncodeError trên một số console Windows
msg_server_running_en = f"Server is running on port: {PORT}"
msg_access_server_en = f"To access the program from THIS computer, open your browser and go to: http://localhost:{PORT}"
msg_access_server_lan_en = f"To access the program from OTHER computers on the LAN, use: http://192.168.1.10:{PORT} (replace 192.168.1.10 with this server's actual LAN IP if different)"
msg_server_stopped_en = "\nServer stopped."

# Thông báo gốc tiếng Việt
msg_server_running_vi = f"Server đang chạy tại cổng: {PORT}"
msg_access_server_vi = f"Để truy cập chương trình từ máy TÍNH NÀY, mở trình duyệt và vào địa chỉ: http://localhost:{PORT}"
msg_access_server_lan_vi = f"Để truy cập chương trình từ các máy KHÁC trong mạng LAN, sử dụng địa chỉ: http://192.168.1.10:{PORT} (thay 192.168.1.10 bằng IP LAN thực tế của máy chủ này nếu khác)"
msg_server_stopped_vi = "\nĐã dừng server."

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        print(msg_server_running_vi)
        print(msg_access_server_vi)
        print(msg_access_server_lan_vi) # Thêm thông báo này
    except UnicodeEncodeError:
        print("---")
        print("Notice: Could not display Vietnamese characters in the console.")
        print("You might need to change your console's code page (e.g., run 'chcp 65001' in cmd).")
        print("Continuing with English messages:")
        print(msg_server_running_en)
        print(msg_access_server_en)
        print(msg_access_server_lan_en) # Thêm thông báo này
        print("---")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        try:
            print(msg_server_stopped_vi)
        except UnicodeEncodeError:
            print(msg_server_stopped_en)
        httpd.shutdown()