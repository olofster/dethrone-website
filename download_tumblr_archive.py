#!/usr/bin/env python3
"""
Script to download all images and videos from a Tumblr blog by scraping the archive page.
This extracts all post URLs from the archive, then visits each post to download media.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time

TUMBLR_BLOG = "arthackday"
ARCHIVE_URL = f"https://{TUMBLR_BLOG}.tumblr.com/archive"
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

def extract_post_urls_from_archive():
    """Extract all post URLs from the archive page."""
    print("Fetching archive page...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    response = requests.get(ARCHIVE_URL, headers=headers, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all post links - Tumblr archive has links like /post/1234567890
    post_urls = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Match post URLs
        if '/post/' in href:
            full_url = urljoin(ARCHIVE_URL, href)
            post_urls.add(full_url)
    
    print(f"Found {len(post_urls)} post URLs in archive")
    return sorted(post_urls)

def extract_media_from_post(post_url):
    """Extract all media URLs from a single post."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(post_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        media_urls = set()
        
        # Find all images
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src and 'tumblr.com' in src:
                # Get higher resolution
                if '_500.' in src:
                    src = src.replace('_500.', '_1280.')
                elif '_250.' in src:
                    src = src.replace('_250.', '_1280.')
                elif '_400.' in src:
                    src = src.replace('_400.', '_1280.')
                media_urls.add(('image', src))
        
        # Find all video sources
        for video in soup.find_all('video'):
            src = video.get('src')
            if src:
                media_urls.add(('video', src))
        
        for source in soup.find_all('source'):
            src = source.get('src')
            if src:
                media_urls.add(('video', src))
        
        return media_urls
    except Exception as e:
        print(f"  Error fetching post {post_url}: {e}")
        return set()

def download_media():
    """Download all media from Tumblr archive."""
    create_output_dir()
    
    print("=" * 60)
    print("Tumblr Media Downloader (Archive Scraper)")
    print("=" * 60)
    print(f"Blog: {TUMBLR_BLOG}")
    print(f"Archive URL: {ARCHIVE_URL}")
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 60)
    print()
    
    try:
        post_urls = extract_post_urls_from_archive()
        
        if not post_urls:
            print("No post URLs found. The archive page might require JavaScript rendering.")
            print("You may need to use a headless browser like Selenium.")
            return
        
        print(f"Extracting media from {len(post_urls)} posts...")
        print("-" * 60)
        print()
        
        all_media = set()
        
        for idx, post_url in enumerate(post_urls, 1):
            print(f"[{idx}/{len(post_urls)}] Processing: {post_url[:60]}...")
            media = extract_media_from_post(post_url)
            all_media.update(media)
            print(f"  Found {len(media)} media items")
            time.sleep(0.5)  # Be polite to the server
        
        print()
        print(f"Found {len(all_media)} unique media items total")
        print("-" * 60)
        print()
        
        downloaded = {'images': 0, 'videos': 0, 'failed': 0}
        
        for idx, (media_type, media_url) in enumerate(sorted(all_media), 1):
            print(f"[{idx}/{len(all_media)}] {media_type}: {media_url[:70]}...")
            
            filename = get_filename_from_url(media_url)
            
            if media_type == 'image':
                filepath = os.path.join(OUTPUT_DIR, "images", filename)
            else:
                filepath = os.path.join(OUTPUT_DIR, "videos", filename)
            
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
        print(f"  Failed: {downloaded['failed']}")
        print(f"  Total: {sum(downloaded.values())}")
        print(f"{'=' * 60}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    download_media()

