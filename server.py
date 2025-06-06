from flask import Flask, request, send_file, jsonify
import yt_dlp
import subprocess
import os
import uuid

app = Flask(__name__)
OUTPUT_DIR = "downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/baixar', methods=['POST'])
def baixar():
    data = request.json
    url = data.get("url")
    tipo = data.get("tipo", "audio")
    inicio = data.get("inicio")
    fim = data.get("fim")

    if not url:
        return jsonify({"erro": "URL ausente"}), 400

    uid = str(uuid.uuid4())
    filename_base = os.path.join(OUTPUT_DIR, uid)
    final_file = ""

    try:
        if tipo == "video":
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': f'{filename_base}.%(ext)s',
                'merge_output_format': 'mp4',
            }
        else:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{filename_base}.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
            file_downloaded = ydl.prepare_filename(result)

        # Se for corte
        if inicio and fim:
            ext = "mp4" if tipo == "video" else "mp3"
            final_file = os.path.join(OUTPUT_DIR, f"{uid}_cut.{ext}")
            subprocess.run([
                "ffmpeg", "-i", file_downloaded,
                "-ss", inicio, "-to", fim,
                "-c", "copy", final_file
            ])
        else:
            final_file = file_downloaded

        return send_file(final_file, as_attachment=True)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
