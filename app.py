import os
from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Proxy list (Free and Public)
    # Note: Agar ye slow chale, toh hum baad mein Premium Proxy bhi add kar sakte hain
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'proxy': 'http://public_proxy_address:port', # Main isse automatic handle kar raha hoon
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            return jsonify({"download_url": video_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
