from flask import Flask, request, jsonify, send_from_directory, render_template, after_this_request
import requests
import os
import subprocess
import uuid
import threading
import time

app = Flask(__name__)

# 🔹 Folder Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")
TEMPLATES_FOLDER = os.path.join(BASE_DIR, "templates")

for folder in [DOWNLOAD_FOLDER, TEMPLATES_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# ---------------- Background Cleanup Function ----------------
def delete_file_later(filepath, delay=600): # 10 minutes delay
    def delay_delete():
        time.sleep(delay)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"🔥 Auto-deleted: {filepath}")
    
    threading.Thread(target=delay_delete).start()

# ---------------- Platform Detection ----------------
def detect_platform(url: str) -> str:
    url = url.lower()
    if "youtube.com" in url or "youtu.be" in url or "googleusercontent.com" in url:
        return "youtube"
    elif "instagram.com" in url:
        return "instagram"
    elif "pin.it" in url or "pinterest.com" in url:
        return "pinterest"
    else:
        return "direct"

# ---------------- Routes ----------------
@app.route("/")
def home():
    try:
        return render_template("index.html")
    except:
        return "⚡ Izumi Server is running! (index.html missing)"

@app.route("/api/download", methods=["POST"])
def download_api():
    data = request.get_json()
    video_url = data.get("url", "")
    
    if not video_url:
        return jsonify({"status": "error", "message": "Link kahan hai?"})

    platform = detect_platform(video_url)
    unique_name = f"{platform}_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join(DOWNLOAD_FOLDER, unique_name)

    try:
        if platform in ["youtube", "instagram", "pinterest"]:
            cmd = [
                "yt-dlp",
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "--no-playlist",
                "-o", output_path,
                video_url
            ]
            subprocess.run(cmd, check=True)
        else:
            r = requests.get(video_url, stream=True, timeout=30)
            r.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # 🕒 File ko 10 min baad delete karne ke liye schedule karein
        delete_file_later(output_path)

        return jsonify({
            "status": "success",
            "link": f"/files/{unique_name}"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/files/<filename>")
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
