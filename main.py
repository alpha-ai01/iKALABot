import os
import http.server
import socketserver
import threading

PORT = int(os.environ.get("PORT", 8080))

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"iKALABot is running and online!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Server serving at port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    # รันเว็บเซิร์ฟเวอร์ใน Background Thread เพื่อเปิดพอร์ตให้ Render และ UptimeRobot
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print("Telegram Bot application started successfully.")
    # คงสถานะโปรแกรมไม่ให้ปิดตัวลง
    server_thread.join()
