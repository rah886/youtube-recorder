#!/usr/bin/env python3
import os
import sys
import time
import datetime
import subprocess

CHANNEL_ID = os.environ["CHANNEL_ID"]
# remote:path inside Google Drive
RCLONE_DEST = "gdrive:/YouTubeRecords"

def is_live():
    """Return the .m3u8 URL if the channel is currently live, else None."""
    cmd = [
        "yt-dlp",
        "--quiet",
        "--skip-download",
        "--print",
        "%(url)s",
        "--match-filter",
        "is_live",
        f"https://www.youtube.com/channel/{CHANNEL_ID}/live"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    url = result.stdout.strip()
    return url if url else None

def record(url, output):
    """Record the HLS stream until it ends."""
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        url,
        "-c",
        "copy",
        "-f",
        "mp4",
        output,
    ]
    subprocess.run(cmd, check=True)

def upload(file_path):
    """Upload to Google Drive via rclone."""
    subprocess.run(["rclone", "copy", file_path, RCLONE_DEST], check=True)
    print(f"Uploaded: {file_path}")

def main():
    print("Looking for live stream …")
    while True:
        stream_url = is_live()
        if stream_url:
            break
        time.sleep(60)  # wait 1 min between checks

    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{CHANNEL_ID}_{ts}.mp4"

    print(f"Recording started → {filename}")
    record(stream_url, filename)
    print("Recording finished")

    upload(filename)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
