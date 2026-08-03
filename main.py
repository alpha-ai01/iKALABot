import requests
import json
import os
import http.server
import socketserver
import threading

PORT = int(os.environ.get("PORT", 10000))

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
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            update = json.loads(post_data.decode('utf-8'))
        else:
            update = {}
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
        
        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            user_text = update["message"]["text"]
            
            import os
            TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
            if TOKEN:
                reply_text = f"บอทได้รับข้อความของคุณแล้ว: {user_text}"
                send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                import requests
                requests.post(send_url, json={"chat_id": chat_id, "text": reply_text})

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
