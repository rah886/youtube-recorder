import os
import subprocess
import requests
import time
from datetime import datetime

# YouTube channel ID
CHANNEL_ID = "UCVKJtFLOXBHqokQzW0tKGlg"  # individual_dekan

# Output file name with date
now = datetime.now().strftime("%Y-%m-%d_%H-%M")
output_file = f"stream_{now}.mp4"

# Check if livestream is active
def is_live(channel_id):
    url = f"https://www.youtube.com/channel/{channel_id}/live"
    r = requests.get(url)
    return "isLiveNow" in r.text

# Record livestream with yt-dlp
def record_stream(channel_id, output_file):
    print("Stream is LIVE! Starting recording...")
    livestream_url = f"https://www.youtube.com/channel/{channel_id}/live"
    subprocess.run([
        "yt-dlp",
        "--hls-use-mpegts",
        "--no-part",
        "--concurrent-fragments", "5",
        "-o", output_file,
        livestream_url
    ])

# Upload to Google Drive via rclone
def upload_to_drive(file_name):
    print("Uploading to Google Drive...")
    subprocess.run(["rclone", "copy", file_name, "gdrive2:", "-v"])

# Main logic
if is_live(CHANNEL_ID):
    record_stream(CHANNEL_ID, output_file)
    upload_to_drive(output_file)
else:
    print("Stream not live. Nothing to do.")
