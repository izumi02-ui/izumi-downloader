import os, io
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url')
    if not video_url: return "URL missing!", 400

    try:
        # In-Memory download options
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': '-', # Isse file save nahi hoti, direct stream hoti hai
            'logtostderr': True,
        }

        buffer = io.BytesIO()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Info nikalna
            info = ydl.extract_info(video_url, download=False)
            filename = f"{info.get('title', 'video')}.mp4"
            
            # Streaming download (Ye storage error fix karega)
            with ydl.urlopen(info['url']) as video_data:
                buffer.write(video_data.read())
        
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype='video/mp4')

    except Exception as e:
        return f"Server Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
