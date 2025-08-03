#!/usr/bin/env python3
import os, time, datetime, subprocess, sys

CHANNEL_ID  = os.environ["CHANNEL_ID"]
RCLONE_DEST = "gdrive:"

def is_live():
    cmd = [
        "yt-dlp", "--quiet", "--skip-download", "--print", "%(url)s",
        "--match-filter", "is_live",
        f"https://www.youtube.com/channel/{CHANNEL_ID}/live"
    ]
    try:
        url = subprocess.check_output(cmd, text=True).strip()
        return url if url and url != "NA" else None
    except subprocess.CalledProcessError:
        return None

def record(url, outfile):
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", url, "-c", "copy", "-f", "mp4", outfile
    ], check=True)

def upload(file):
    subprocess.run(["rclone", "copy", file, RCLONE_DEST], check=True)

def main():
    print("Waiting for live stream ...")
    start = time.time()
    while time.time() - start < 6 * 3600:
        url = is_live()
        if url:
            break
        time.sleep(30)          # проверка каждые 30 с

    if not url:
        print("No live stream within 6 hours.")
        return

    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{CHANNEL_ID}_{ts}.mp4"
    print(f"Recording → {filename}")
    record(url, filename)
    print("Recording finished, uploading ...")
    upload(filename)

if __name__ == "__main__":
    try: main()
    except Exception as e:
        print(e, file=sys.stderr); sys.exit(1)
