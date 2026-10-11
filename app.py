import os
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'رابط الفيديو مطلوب'}), 400

    filename_base = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_FOLDER, f'{filename_base}.%(ext)s')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'cookiefile': 'cookies.txt',  # استخدام ملف الكوكيز لتجاوز الحظر
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            mp3_filename = f"{filename_base}.mp3"

        download_url = f"{request.host_url}download/{mp3_filename}"
        return jsonify({'download_url': download_url, 'title': info.get('title', 'Audio')})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'الملف غير موجود'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
