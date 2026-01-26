from flask import Flask, request, jsonify, send_from_directory, render_template, after_this_request
import os
import subprocess
import uuid

app = Flask(__name__)

# 🔹 Folder Setup
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
        return jsonify({"status": "error", "message": "Link dalo bhai!"})

    unique_name = f"video_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join(DOWNLOAD_FOLDER, unique_name)

    try:
        cmd = [
            "yt-dlp",
            "-f", "best[ext=mp4]", 
            "--no-playlist",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "-o", output_path,
            video_url
        ]
        subprocess.run(cmd, check=True, timeout=60)

        return jsonify({
            "status": "success",
            "link": f"/files/{unique_name}"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": "Server error ya block ho gaya."})

# 🔥 YAHAN HAI AUTO-DELETE LOGIC
@app.route("/files/<filename>")
def serve_file(filename):
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    @after_this_request
    def remove_file(response):
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"🔥 File deleted: {filename}")
        except Exception as e:
            print(f"Error: {e}")
        return response

    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
