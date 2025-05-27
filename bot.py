from flask import Flask
import threading
import os
import requests
import time

# 创建 Flask 实例
app = Flask(__name__)

# 读取环境变量
TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"
FLASK_API_URL = os.getenv("FLASK_API_URL", "https://yt-dlp-flask-api0526-1.onrender.com/download")

# 获取消息更新
def get_updates(offset=None):
    url = f"{API_URL}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=120)
        return response.json()
    except Exception as e:
        print(f"Error getting updates: {e}")
        return {"result": []}

# 发送消息
def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Error sending message: {e}")

# 处理收到的消息
def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text.startswith("http"):
        send_message(chat_id, "🎬 正在下载视频，请稍等...")
        try:
            resp = requests.post(FLASK_API_URL, json={"url": text})
            if resp.status_code == 200:
                send_message(chat_id, "✅ 视频已准备好（请在浏览器中查看 Render API 结果）")
            else:
                send_message(chat_id, f"❌ 下载失败：{resp.text}")
        except Exception as e:
            send_message(chat_id, f"❌ 出现错误：{str(e)}")
    else:
        send_message(chat_id, "📎 请发送 YouTube 视频链接。")

# 主循环：轮询 Telegram 消息
def run_bot():
    print("Bot is running...")
    offset = None
    while True:
        updates = get_updates(offset)
        for update in updates.get("result", []):
            offset = update["update_id"] + 1
            if "message" in update:
                handle_message(update["message"])
        time.sleep(1)

# 提供一个 HTTP 路由给 Render 检测端口
@app.route("/")
def home():
    return "✅ Telegram Bot is running."

# 启动
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)
