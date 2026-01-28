from flask import Flask, request, jsonify, send_from_directory, render_template, after_this_request
import os
import subprocess
import uuid

app = Flask(__name__)

# 🔹 Folder & Cookies Setup
DOWNLOAD_FOLDER = "/tmp/downloads"
COOKIES_FILE = "instagram_cookies.txt" # Is file ko upload karna mat bhoolna

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

    unique_name = f"nexus_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join(DOWNLOAD_FOLDER, unique_name)

    try:
        # 🚀 Advanced Nexus Engine Command
        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", # Best MP4 quality logic
            "--no-check-certificate",
            "--no-playlist",
            "--geo-bypass",
            # Fresh Mobile User-Agent to avoid detection
            "--user-agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "--referer", "https://www.instagram.com/",
            "-o", output_path
        ]

        # 🍪 Add cookies if the file exists
        if os.path.exists(COOKIES_FILE):
            cmd.extend(["--cookies", COOKIES_FILE])
        
        cmd.append(video_url)

        # Engine execution with timeout
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if os.path.exists(output_path):
            return jsonify({
                "status": "success",
                "link": f"/files/{unique_name}"
            })
        else:
            print(f"Engine Log: {result.stderr}") # Logs for debugging in Render
            return jsonify({"status": "error", "message": "Instagram ne block kiya ya link galat hai."})

    except Exception as e:
        print(f"System Error: {str(e)}")
        return jsonify({"status": "error", "message": "Nexus Engine Busy. Try again!"})

# 🔥 AUTO-DELETE LOGIC (STAYS SAME)
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
            print(f"Error deleting file: {e}")
        return response

    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
