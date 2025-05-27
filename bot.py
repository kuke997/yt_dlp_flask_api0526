import os
import logging
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL", "https://yt-dlp-flask-api0526-1.onrender.com/download")

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# Handle messages sent to the bot
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("请发送一个有效的 YouTube 链接。")
        return

    try:
        # 调用你的 Flask API
        response = requests.post(API_URL, json={"url": url})
        if response.status_code == 200:
            with open("video.mp4", "wb") as f:
                f.write(response.content)
            await update.message.reply_video(video=open("video.mp4", "rb"))
            os.remove("video.mp4")
        else:
            await update.message.reply_text(f"下载失败：{response.text}")
    except Exception as e:
        await update.message.reply_text(f"出错了：{e}")

# Telegram Bot 启动
@app.route("/")
def home():
    return "Telegram bot is running!"

def start_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app_bot.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_bot()
