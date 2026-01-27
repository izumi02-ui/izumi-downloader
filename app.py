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
        # 🛡️ Advance Bypass Strategy
        cmd = [
            "yt-dlp",
            "-f", "best[ext=mp4]/best", 
            "--no-playlist",
            # Masking the request to look like a real browser
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "--add-header", "Referer:https://www.instagram.com/",
            "--add-header", "Origin:https://www.instagram.com/",
            "--no-check-certificate",
            "--geo-bypass", # Region block hatane ke liye
            "-o", output_path,
            video_url
        ]
        
        # subprocess.run pe thoda extra control
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)

        if result.returncode != 0:
            print(f"YT-DLP Error: {result.stderr}")
            return jsonify({"status": "error", "message": "Instagram ne block kiya. 2 min baad try karein."})

        return jsonify({
            "status": "success",
            "link": f"/files/{unique_name}"
        })

    except subprocess.TimeoutExpired:
        return jsonify({"status": "error", "message": "Server slow hai, re-fetch karein."})
    except Exception as e:
        print(f"System Error: {str(e)}")
        return jsonify({"status": "error", "message": "NEXUS Engine Busy."})

#  AUTO-DELETE LOGIC (Same)
@app.route("/files/<filename>")
def serve_file(filename):
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    @after_this_request
    def remove_file(response):
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f" File deleted: {filename}")
        except Exception as e:
            print(f"Error: {e}")
        return response

    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
