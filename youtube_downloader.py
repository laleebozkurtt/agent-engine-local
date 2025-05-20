#!/usr/bin/env python3
import argparse
import json
import os
import sys

try:
    import yt_dlp
except ImportError:
    print("yt-dlp kütüphanesi bulunamadı. Lütfen 'pip install yt-dlp' komutu ile yükleyin.")
    sys.exit(1)


def download_youtube_content(url: str, format_type: str = "mp4", output_dir: str = "./downloads"):
    """
    YouTube URL'sinden belirtilen formatta (mp3 veya mp4) içerik indirir.

    Args:
        url: YouTube video URL'si
        format_type: İndirme formatı ("mp3" veya "mp4")
        output_dir: İndirilen dosyanın kaydedileceği dizin

    Returns:
        İşlem sonucunu içeren bir sözlük
    """
    try:
        os.makedirs(output_dir, exist_ok=True)

        ydl_opts = {
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
        }

        if format_type.lower() == "mp4":
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4'
        elif format_type.lower() == "mp3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            return {
                "status": "error",
                "message": f"Desteklenmeyen format: {format_type}. Lütfen 'mp3' veya 'mp4' seçin."
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # İndirilen dosyanın tam yolu
        file_ext = 'mp3' if format_type.lower() == 'mp3' else 'mp4'
        file_name = f"{info['title']}.{file_ext}"
        file_path = os.path.join(output_dir, file_name)

        if not os.path.exists(file_path):
            # Bazen dosya uzantısı farklı olabilir, bunu kontrol edelim
            # Alternatif olarak info'dan 'requested_formats' kontrol edilebilir
            # veya 'filesize' ve 'filepath' gibi alanlar
            for key in ['requested_formats', 'formats']:
                if key in info:
                    for f in info[key]:
                        if f.get('ext') == file_ext:
                            file_path = f.get('filepath', file_path)
                            break

        # Dosya boyutu alalım
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        return {
            "status": "success",
            "output": file_path,
            "metadata": {
                "title": info['title'],
                "format": file_ext,
                "file_size": file_size
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"İndirme hatası: {str(e)}"
        }


def main():
    parser = argparse.ArgumentParser(description="YouTube'dan mp3 veya mp4 olarak içerik indir")
    parser.add_argument("--url", required=True, help="İndirilecek YouTube video URL'si veya video ID'si")
    parser.add_argument("--format", default="mp4", choices=["mp3", "mp4"], help="İndirme formatı (mp3 veya mp4)")
    parser.add_argument("--output_dir", default="./downloads", help="İndirilen dosyanın kaydedileceği dizin")

    args = parser.parse_args()

    # Eğer sadece video ID verilmişse tam url yapalım
    if not args.url.startswith("http"):
        args.url = f"https://www.youtube.com/watch?v={args.url}"

    result = download_youtube_content(args.url, args.format, args.output_dir)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
