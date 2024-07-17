import subprocess
import os
import requests

# Configuration for the Telegram Bot
BOT_TOKEN = 'your_telegram_bot_token'  # Replace with your actual Telegram Bot Token
CHAT_ID = 'your_chat_id'  # Replace with your actual Telegram Chat ID

# Directory to save the recordings
RECORDINGS_DIR = 'recordings'
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR')

def record_m3u8(url, duration, filename):
    # Define the full path for the recording
    recording_path = os.path.join(RECORDINGS_DIR, filename)
    
    # Command to start the recording
    command = [
        'ffmpeg',
        '-i', url,
        '-t', duration,
        '-c', 'copy',
        recording_path
    ]
    # Run the command to record the stream
    subprocess.run(command)
    print(f"Recording saved as {recording_path}")

def upload_to_telegram(filename):
    upload_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(filename, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': CHAT_ID}
        response = requests.post(upload_url, files=files, data=data)
    if response.ok:
        print(f"Upload Successful! Response: {response.json()}")
    else:
        print(f"Upload Failed! Response: {response.text}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Record a live M3U8 stream and upload it to Telegram.')
    parser.add_argument('url', type=str, help='M3U8 stream URL')
    parser.add_argument('duration', type=str, help='Recording duration in HH:MM:SS format')
    parser.add_argument('filename', type=str, help='Name of the file to save')
    
    args = parser.parse_args()
    
    # Record the M3U8 stream
    record_m3u8(args.url, args.duration, os.path.join(RECORDINGS_DIR, args.filename))
    
    # Upload the recorded file to Telegram
    upload_to_telegram(os.path.join(RECORDINGS_DIR, args.filename))

if name == 'main':
    main()
