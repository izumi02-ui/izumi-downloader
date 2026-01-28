from flask import Flask, request, jsonify, send_from_directory, render_template, after_this_request
import os
import subprocess
import uuid
import json

app = Flask(__name__)

# 🔹 Folder & Cookies Setup
DOWNLOAD_FOLDER = "/tmp/downloads"
JSON_COOKIES = "cookies.json" 
TEMP_COOKIES_TXT = "/tmp/instagram_cookies.txt"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# 🍪 JSON to Netscape Converter (For yt-dlp)
def prepare_cookies():
    if os.path.exists(JSON_COOKIES):
        try:
            with open(JSON_COOKIES, 'r') as f:
                cookies_data = json.load(f)
            
            with open(TEMP_COOKIES_TXT, 'w') as f:
                f.write("# Netscape HTTP Cookie File\n")
                for c in cookies_data:
                    domain = c.get('domain', '')
                    flag = "TRUE" if domain.startswith('.') else "FALSE"
                    path = c.get('path', '/')
                    secure = "TRUE" if c.get('secure') else "FALSE"
                    expiry = int(c.get('expirationDate', 0))
                    name = c.get('name', '')
                    value = c.get('value', '')
                    f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")
            return TEMP_COOKIES_TXT
        except Exception as e:
            print(f"Cookie Conversion Error: {e}")
            return None
    return None

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
        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--no-check-certificate",
            "--no-playlist",
            "--geo-bypass",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "--referer", "https://www.instagram.com/",
            "-o", output_path
        ]

        cookie_path = prepare_cookies()
        if cookie_path:
            cmd.extend(["--cookies", cookie_path])
        
        cmd.append(video_url)
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if os.path.exists(output_path):
            return jsonify({"status": "success", "link": f"/files/{unique_name}"})
        else:
            return jsonify({"status": "error", "message": "Instagram block ya link error."})

    except Exception as e:
        return jsonify({"status": "error", "message": "Nexus Engine Busy."})

# 🔥 AUTO-DELETE LOGIC (YAHAN HAI BHAI)
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
    
