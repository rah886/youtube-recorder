import os
import time
import subprocess
import datetime
import requests

YOUTUBE_URL = os.environ["YOUTUBE_URL"]
MAX_WAIT_TIME = os.environ.get("MAX_WAIT_TIME", "01:30:00")  # формат HH:MM:SS
MAX_DURATION = os.environ.get("MAX_DURATION", "03:00:00")    # формат HH:MM:SS

def parse_duration(duration_str):
    h, m, s = map(int, duration_str.strip().split(":"))
    return h * 3600 + m * 60 + s

def is_live(url):
    try:
        response = requests.get(url)
        return "isLiveBroadcast" in response.text or "hlsManifestUrl" in response.text
    except:
        return False

def wait_for_stream(url, max_wait_seconds):
    print(f"Ожидание начала трансляции (макс {max_wait_seconds // 60} минут)...")
    start_time = time.time()
    while time.time() - start_time < max_wait_seconds:
        if is_live(url):
            print("Эфир начался!")
            return True
        print("Эфир еще не начался. Жду 30 сек...")
        time.sleep(30)
    print("Эфир не начался. Завершаю.")
    return False

def record_stream(url, max_duration_seconds):
    print("Начинаю запись...")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"recording_{timestamp}.mp4"
    command = [
        "yt-dlp",
        "--hls-use-mpegts",
        "--no-part",
        "--no-mtime",
        "--downloader", "ffmpeg",
        "--live-from-start",
        "--max-download-seconds", str(max_duration_seconds),
        "-o", output_file,
        url
    ]
    subprocess.run(command)
    return output_file

def upload_to_drive(file_path):
    print("☁️ Загружаю в Google Drive...")
    remote_path = f"gdrive:{file_path}"
    subprocess.run(["rclone", "copy", file_path, remote_path])
    print("Загружено.")
    os.remove(file_path)

# === Основной процесс ===

print(f"Цель: {YOUTUBE_URL}")
max_wait_seconds = parse_duration(MAX_WAIT_TIME)
max_duration_seconds = parse_duration(MAX_DURATION)

if wait_for_stream(YOUTUBE_URL, max_wait_seconds):
    video_file = record_stream(YOUTUBE_URL, max_duration_seconds)
    upload_to_drive(video_file)
