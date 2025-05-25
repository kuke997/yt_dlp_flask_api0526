from flask import Flask, request, send_file, jsonify
from yt_dlp import YoutubeDL
import os
import uuid

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"message": "yt-dlp Flask API is running!"})

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    output_dir = "/tmp"
    filename = str(uuid.uuid4())
    output_template = os.path.join(output_dir, f"{filename}.%(ext)s")

    ydl_opts = {
        'outtmpl': output_template,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        video_path = os.path.join(output_dir, f"{filename}.mp4")
        return send_file(video_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
