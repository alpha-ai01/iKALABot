from flask import Flask
import threading
import logging

app = Flask(__name__)
# ปิด log กวนใจของ Werkzeug
logging.getLogger('werkzeug').setLevel(logging.ERROR)

@app.route('/', methods=['GET', 'HEAD'])
def health_check():
    # ตอบกลับ 200 OK ให้ UptimeRobot และ Render รู้ว่าระบบปกติ
    return "Bot status: Active", 200

def run_server(port):
    app.run(host='0.0.0.0', port=port)

def start_web_server(port):
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
