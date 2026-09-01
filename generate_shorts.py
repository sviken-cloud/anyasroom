#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path


def download_and_trim_video(url, start_time, duration, output_path):
    """Download and trim a video using yt-dlp and ffmpeg."""
    try:
        temp_video = "/tmp/video_temp.mp4"
        
        print(f"Downloading: {url}")
        download_cmd = [
            "yt-dlp",
            "-f", "best[ext=mp4]",
            "-o", temp_video,
            url
        ]
        
        result = subprocess.run(download_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Download error: {result.stderr}")
            return False
        
        if not os.path.exists(temp_video):
            print(f"Video not created")
            return False
        
        print(f"Trimming: {start_time}s to {start_time + duration}s")
        trim_cmd = [
            "ffmpeg",
            "-i", temp_video,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-y",
            output_path
        ]
        
        result = subprocess.run(trim_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Trim error: {result.stderr}")
            return False
        
        if os.path.exists(temp_video):
            os.remove(temp_video)
        
        print(f"✓ Created: {output_path}")
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--refs", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    Path(args.out).mkdir(parents=True, exist_ok=True)
    
    with open(args.refs) as f:
        refs = json.load(f)
    
    print(f"Processing {len(refs)} videos...")
    success = 0
    
    for i, ref in enumerate(refs):
        title = ref.get('title', f'short_{i}')
        url = ref.get('url')
        start_time = ref.get('start_time', 0)
        duration = ref.get('duration', 60)
        
        if not url:
            print(f"Skipping {i}: no URL")
            continue
        
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).replace(' ', '_')
        output = os.path.join(args.out, f"{safe_title}_{i}.mp4")
        
        if download_and_trim_video(url, start_time, duration, output):
            success += 1
        else:
            print(f"Failed: {title}")
    
    print(f"\nDone! {success}/{len(refs)} shorts created")
