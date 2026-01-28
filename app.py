import os
import subprocess
import uuid
from flask import Flask, request, jsonify, send_from_directory, render_template, after_this_request

app = Flask(__name__)

DOWNLOAD_FOLDER = "/tmp/downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/download", methods=["POST"])
def download_api():
    data = request.get_json()
    video_url = data.get("url", "")
    
    if not video_url:
        return jsonify({"status": "error", "message": "Link missing!"})

    unique_name = f"nexus_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join(DOWNLOAD_FOLDER, unique_name)

    try:
        # Nexus Engine: Anti-Block Strategy
        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--no-check-certificate",
            # Mobile Safari User Agent
            "--user-agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
            # Add Referer to fool Instagram
            "--referer", "https://www.instagram.com/",
            "--no-playlist",
            "--geo-bypass",
            # Force basic extraction to avoid JS challenges
            "--extractor-args", "instagram:fast",
            "-o", output_path,
            video_url
        ]
        
        # Capture error output for debugging
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if os.path.exists(output_path):
            return jsonify({"status": "success", "link": f"/files/{unique_name}"})
        else:
            # Agar file nahi bani toh error log check karein
            print(f"YT-DLP Error: {result.stderr}")
            return jsonify({"status": "error", "message": "Instagram ne server block kar diya hai. Thodi der baad try karein."})

    except Exception as e:
        print(f"System Error: {str(e)}")
        return jsonify({"status": "error", "message": "Nexus Engine Busy (IP Blocked). Try later!"})

@app.route("/files/<filename>")
def serve_file(filename):
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
