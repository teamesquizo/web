from flask import Flask, request, jsonify, send_file
import os
import yt_dlp

app = Flask(__name__)

# Carpeta donde se guardarán temporalmente los archivos MP3
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/api/download', methods=['POST'])
def download():
    data = request.get_json()
    youtube_url = data.get('url')

    if not youtube_url:
        return jsonify({"error": "No se proporcionó una URL"}), 400

    try:
        # Opciones para yt_dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            filename = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')

        # Devolver la ruta del archivo descargado
        return jsonify({"downloadUrl": f"/downloads/{os.path.basename(filename)}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/downloads/<filename>', methods=['GET'])
def serve_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "Archivo no encontrado"}), 404


if __name__ == '__main__':
    app.run(debug=True)
