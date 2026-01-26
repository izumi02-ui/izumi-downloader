import os, time, shutil
from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = '/tmp/downloads' # Render par /tmp folder use karna safe hota hai

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url')
    
    # Har download se pehle folder khaali karein
    shutil.rmtree(DOWNLOAD_FOLDER, ignore_errors=True)
    os.makedirs(DOWNLOAD_FOLDER)

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)

        # File bhejne ke baad usey server se delete karne ka jugad
        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
            except:
                pass
            return response

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
