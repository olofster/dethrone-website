#!/usr/bin/env python3
"""
Script to download all images and videos from a Tumblr blog using RSS feed.
This is more reliable than scraping the archive page.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

TUMBLR_BLOG = "arthackday"
RSS_URL = f"https://{TUMBLR_BLOG}.tumblr.com/rss"
OUTPUT_DIR = "tumblr_media"

def create_output_dir():
    """Create output directory if it doesn't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "videos"), exist_ok=True)

def get_filename_from_url(url):
    """Extract filename from URL."""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename or '.' not in filename:
        # Try to extract from URL pattern
        match = re.search(r'/([^/]+\.(jpg|jpeg|png|gif|mp4|webm|mov))', url, re.IGNORECASE)
        if match:
            filename = match.group(1)
        else:
            # Generate filename from URL hash
            filename = f"media_{abs(hash(url)) % 1000000}.jpg"
    return filename

def download_file(url, filepath):
    """Download a file from URL to filepath."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  Error downloading {url}: {e}")
        return False

def extract_media_from_rss():
    """Extract all media URLs from Tumblr RSS feed."""
    print("Fetching RSS feed...")
    response = requests.get(RSS_URL, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.find_all('item')
    
    print(f"Found {len(items)} posts in RSS feed")
    print()
    
    all_media = set()
    
    for item in items:
        # Get description which contains HTML with media
        description = item.find('description')
        if not description:
            continue
        
        desc_html = description.string or ""
        desc_soup = BeautifulSoup(desc_html, 'html.parser')
        
        # Find all images
        for img in desc_soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                # Get higher resolution
                if '_500.' in src:
                    src = src.replace('_500.', '_1280.')
                elif '_250.' in src:
                    src = src.replace('_250.', '_1280.')
                all_media.add(('image', src))
        
        # Find all video sources
        for video in desc_soup.find_all('video'):
            src = video.get('src')
            if src:
                all_media.add(('video', src))
        
        for source in desc_soup.find_all('source'):
            src = source.get('src')
            if src:
                all_media.add(('video', src))
        
        # Find iframe embeds
        for iframe in desc_soup.find_all('iframe'):
            src = iframe.get('src', '')
            if src:
                all_media.add(('embed', src))
    
    return all_media

def download_media():
    """Download all media from Tumblr RSS feed."""
    create_output_dir()
    
    print("=" * 60)
    print("Tumblr Media Downloader (RSS Method)")
    print("=" * 60)
    print(f"Blog: {TUMBLR_BLOG}")
    print(f"RSS URL: {RSS_URL}")
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 60)
    print()
    
    try:
        media_items = extract_media_from_rss()
        
        print(f"Found {len(media_items)} unique media items")
        print("-" * 60)
        print()
        
        downloaded = {'images': 0, 'videos': 0, 'embeds': 0, 'failed': 0}
        
        for idx, (media_type, media_url) in enumerate(sorted(media_items), 1):
            print(f"[{idx}/{len(media_items)}] {media_type}: {media_url[:70]}...")
            
            if media_type == 'embed':
                print(f"  (Embed URL - skipping download)")
                downloaded['embeds'] += 1
                continue
            
            filename = get_filename_from_url(media_url)
            
            if media_type == 'image':
                filepath = os.path.join(OUTPUT_DIR, "images", filename)
            elif media_type == 'video':
                filepath = os.path.join(OUTPUT_DIR, "videos", filename)
            else:
                filepath = os.path.join(OUTPUT_DIR, filename)
            
            # Skip if already exists
            if os.path.exists(filepath):
                print(f"  Already exists, skipping...")
                continue
            
            if download_file(media_url, filepath):
                if media_type == 'image':
                    downloaded['images'] += 1
                else:
                    downloaded['videos'] += 1
                print(f"  ✓ Saved ({os.path.getsize(filepath) / 1024:.1f} KB)")
            else:
                downloaded['failed'] += 1
            
            time.sleep(0.3)  # Small delay between downloads
        
        print()
        print("=" * 60)
        print("Download Summary:")
        print(f"  Images: {downloaded['images']}")
        print(f"  Videos: {downloaded['videos']}")
        print(f"  Embeds: {downloaded['embeds']}")
        print(f"  Failed: {downloaded['failed']}")
        print(f"  Total: {sum(downloaded.values())}")
        print(f"{'=' * 60}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    download_media()

