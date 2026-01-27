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
        # Permanent Solution Strategy:
        # 1. Use a fresh Mobile User-Agent
        # 2. Force basic extraction to avoid login walls
        cmd = [
            "yt-dlp",
            "-f", "best",
            "--no-check-certificate",
            "--user-agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
            "--geo-bypass",
            "-o", output_path,
            video_url
        ]
        
        subprocess.run(cmd, check=True, timeout=120)

        if os.path.exists(output_path):
            return jsonify({"status": "success", "link": f"/files/{unique_name}"})
        else:
            return jsonify({"status": "error", "message": "File download nahi hui."})

    except Exception as e:
        return jsonify({"status": "error", "message": "Instagram ne block kiya ya link galat hai."})

@app.route("/files/<filename>")
def serve_file(filename):
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    @after_this_request
    def remove_file(response):
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
        return response

    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    
