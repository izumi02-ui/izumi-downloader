import os, time
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)
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
        # Har download se pehle purani files saaf karein (Storage Fix)
        for f in os.listdir(DOWNLOAD_FOLDER):
            os.remove(os.path.join(DOWNLOAD_FOLDER, f))

        ydl_opts = {
            'format': 'best', 
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'no_warnings': True,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Server Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
