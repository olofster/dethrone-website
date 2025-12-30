#!/usr/bin/env python3
"""
Script to download all images and videos from a Tumblr blog archive using Selenium.
This script renders the JavaScript-heavy archive page to extract all post URLs.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
import subprocess
import sys

TUMBLR_BLOG = "arthackday"
ARCHIVE_URL = f"https://{TUMBLR_BLOG}.tumblr.com/archive"
OUTPUT_DIR = "tumblr_media"

def check_selenium():
    """Check if selenium is installed."""
    try:
        import selenium
        return True
    except ImportError:
        return False

def install_selenium():
    """Install selenium if not available."""
    print("Selenium not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "webdriver-manager"])
    print("Selenium installed successfully!")

def extract_post_urls_with_selenium():
    """Extract all post URLs from the archive page using Selenium."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        if not check_selenium():
            install_selenium()
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
    
    print("Setting up Chrome driver...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print(f"Loading archive page: {ARCHIVE_URL}")
        driver.get(ARCHIVE_URL)
        
        # Wait for the page to load
        print("Waiting for page to load...")
        time.sleep(5)
        
        # Scroll to load more posts (Tumblr archive uses infinite scroll)
        print("Scrolling to load all posts...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 50  # Limit to prevent infinite scrolling
        
        while scroll_attempts < max_scrolls:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for content to load
            
            # Check if new content loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scroll_attempts += 1
            print(f"  Scrolled {scroll_attempts} times, height: {new_height}")
        
        print("Extracting post URLs...")
        # Find all post links
        post_urls = set()
        
        # Look for links that match post URL pattern
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute("href")
            if href and "/post/" in href:
                post_urls.add(href)
        
        print(f"Found {len(post_urls)} post URLs")
        return sorted(post_urls)
        
    finally:
        driver.quit()

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

def create_output_dir():
    """Create output directory if it doesn't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "videos"), exist_ok=True)

def download_media():
    """Download all media from Tumblr archive."""
    create_output_dir()
    
    print("=" * 60)
    print("Tumblr Media Downloader (Archive with Selenium)")
    print("=" * 60)
    print(f"Blog: {TUMBLR_BLOG}")
    print(f"Archive URL: {ARCHIVE_URL}")
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 60)
    print()
    
    try:
        # Extract post URLs using Selenium
        post_urls = extract_post_urls_with_selenium()
        
        if not post_urls:
            print("No post URLs found.")
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

