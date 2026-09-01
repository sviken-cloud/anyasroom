import json
import os
import subprocess
import sys
from pathlib import Path


def download_and_trim_video(url, start_time, duration, output_path):
    """
    Download a YouTube video and trim it to the specified time range.
    
    Args:
        url: YouTube video URL
        start_time: Start time in seconds
        duration: Duration in seconds
        output_path: Output file path
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Download video using yt-dlp
        temp_video = "/tmp/video_temp.mp4"
        
        print(f"Downloading video from {url}...")
        download_cmd = [
            "yt-dlp",
            "-f", "best[ext=mp4]",
            "--js-runtime", "node",
            "-o", temp_video,
            url
        ]
        
        result = subprocess.run(download_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error downloading video: {result.stderr}")
            return False
        
        if not os.path.exists(temp_video):
            print(f"Video file not found after download")
            return False
        
        # Trim video using ffmpeg
        print(f"Trimming video: {start_time}s to {start_time + duration}s...")
        trim_cmd = [
            "ffmpeg",
            "-i", temp_video,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-y",  # Overwrite output file
            output_path
        ]
        
        result = subprocess.run(trim_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error trimming video: {result.stderr}")
            return False
        
        # Clean up temp file
        if os.path.exists(temp_video):
            os.remove(temp_video)
        
        print(f"Successfully created short: {output_path}")
        return True
    
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return False


def main(refs_file, output_dir):
    """
    Main function to generate shorts from refs.json
    
    Args:
        refs_file: Path to refs.json file
        output_dir: Output directory for generated shorts
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Load refs.json
    if not os.path.exists(refs_file):
        print(f"Error: {refs_file} not found")
        sys.exit(1)
    
    try:
        with open(refs_file, 'r') as f:
            refs = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing {refs_file}: {str(e)}")
        sys.exit(1)
    
    if not isinstance(refs, list):
        print("Error: refs.json must contain a JSON array")
        sys.exit(1)
    
    print(f"Processing {len(refs)} videos...")
    success_count = 0
    
    for i, ref in enumerate(refs):
        # Validate ref structure
        required_fields = ['title', 'url', 'start_time', 'duration']
        missing_fields = [field for field in required_fields if field not in ref]
        
        if missing_fields:
            print(f"Skipping ref {i}: missing fields {missing_fields}")
            continue
        
        title = ref['title']
        url = ref['url']
        start_time = ref['start_time']
        duration = ref['duration']
        
        # Sanitize title for filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).replace(' ', '_')
        output_file = os.path.join(output_dir, f"{safe_title}_{i}.mp4")
        
        print(f"\n[{i+1}/{len(refs)}] Processing: {title}")
        
        if download_and_trim_video(url, start_time, duration, output_file):
            success_count += 1
        else:
            print(f"Failed to process: {title}")
    
    print(f"\n✅ Complete! Generated {success_count}/{len(refs)} shorts")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate YouTube shorts from refs.json")
    parser.add_argument("--refs", required=True, help="Path to refs.json file")
    parser.add_argument("--out", required=True, help="Output directory for generated shorts")
    args = parser.parse_args()
    
    main(args.refs, args.out)
        
