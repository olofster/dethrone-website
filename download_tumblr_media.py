#!/usr/bin/env python3
"""
Script to download all images and videos from a Tumblr blog using yt-dlp.
"""

import os
import subprocess
import sys

TUMBLR_URL = "https://arthackday.tumblr.com"
OUTPUT_DIR = "tumblr_media"
YT_DLP_PATH = "/Users/olofmathe/Library/Python/3.9/bin/yt-dlp"

def create_output_dir():
    """Create output directory if it doesn't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_tumblr_media():
    """Download all media from Tumblr blog using yt-dlp."""
    create_output_dir()
    
    print("=" * 60)
    print("Tumblr Media Downloader")
    print("=" * 60)
    print(f"Blog URL: {TUMBLR_URL}")
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 60)
    print()
    print("Starting download...")
    print("This will download all images, videos, and other media from the blog.")
    print("This may take a while depending on the number of posts.")
    print("-" * 60)
    print()
    
    # Download all media from the blog
    download_cmd = [
        YT_DLP_PATH,
        "--cookies-from-browser", "chrome",
        "--write-thumbnail",
        "--write-description",
        "--write-info-json",
        "--no-playlist",
        "-o", f"{OUTPUT_DIR}/%(title)s - %(id)s.%(ext)s",
        TUMBLR_URL
    ]
    
    try:
        print("Running yt-dlp...")
        print()
        subprocess.run(download_cmd, check=False)
        
        print()
        print("=" * 60)
        print("Download complete!")
        print(f"Files saved to: {os.path.abspath(OUTPUT_DIR)}")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        print("Partial downloads may be in the output directory.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    download_tumblr_media()
