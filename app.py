import os
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

# Download folder setup
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url')
    if not video_url:
        return "URL missing!", 400

    try:
        # Final Fixed Options for YouTube and Render
        ydl_opts = {
            # 'best' format direct download karega bina merge kiye (FFmpeg error fix)
            'format': 'best[ext=mp4]/best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'no_warnings': True,
            'quiet': True,
            # YouTube block se bachne ke liye Fake Browser identity
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.google.com/',
            'nocheckcertificate': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Video info nikalna aur download karna
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)

        # File ko user ke phone/PC par bhejna
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        # Agar error aaye toh saaf-saaf dikhana
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    # Render ke liye port management
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
