#!/usr/bin/env python3
"""
Download profile pictures from Twitter/X for contributors
"""

import os
import re
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse

PROFILE_IMAGES_DIR = "profile_images"

def download_profile_image(handle, output_path):
    """Download profile image from X/Twitter"""
    # Try multiple methods to get the profile image
    
    # Method 1: Try the profile page and extract image
    profile_url = f"https://x.com/{handle}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(profile_url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        # Look for profile image in the HTML
        # Twitter/X often uses meta tags or JSON-LD for profile images
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find profile image in meta tags
        meta_image = soup.find('meta', property='og:image')
        if meta_image and meta_image.get('content'):
            img_url = meta_image['content']
            # Get higher resolution if available (replace _normal with _400x400 or _bigger)
            img_url = img_url.replace('_normal', '_400x400')
            img_url = img_url.replace('_200x200', '_400x400')
            
            # Download the image
            img_response = requests.get(img_url, headers=headers, timeout=10)
            img_response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(img_response.content)
            
            return True
        
        # Try to find in script tags (Twitter embeds JSON data)
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'profile_image_url' in script.string:
                # Extract URL from JSON - handle escaped characters
                # Look for profile_image_url_https or profile_image_url
                patterns = [
                    r'"profile_image_url_https":"([^"]+)"',
                    r'"profile_image_url":"([^"]+)"',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, script.string)
                    if match:
                        img_url = match.group(1)
                        # Unescape JSON string
                        img_url = img_url.replace('\\/', '/')
                        img_url = img_url.replace('\\u002F', '/')
                        # Get higher resolution
                        img_url = img_url.replace('_normal', '_400x400')
                        img_url = img_url.replace('_200x200', '_400x400')
                        img_url = img_url.replace('_mini', '_400x400')
                        
                        try:
                            img_response = requests.get(img_url, headers=headers, timeout=10)
                            img_response.raise_for_status()
                            
                            with open(output_path, 'wb') as f:
                                f.write(img_response.content)
                            
                            return True
                        except Exception as e:
                            print(f"      Error downloading image from {img_url}: {e}")
                            continue
        
    except Exception as e:
        print(f"    Error downloading {handle}: {e}")
        return False
    
    return False

def main():
    # Read the list from the previous script output or recreate it
    # For now, let's get it from the find script
    from find_blank_avatars_with_twitter import find_blank_avatars_with_twitter
    
    print("=" * 60)
    print("Downloading Twitter Profile Pictures")
    print("=" * 60)
    print()
    
    contributors = find_blank_avatars_with_twitter()
    
    if not os.path.exists(PROFILE_IMAGES_DIR):
        os.makedirs(PROFILE_IMAGES_DIR)
    
    downloaded = 0
    failed = 0
    skipped = 0
    
    for i, contrib in enumerate(contributors, 1):
        name = contrib['name']
        handle = contrib['handle']
        
        # Create filename from name (normalize)
        filename = re.sub(r'[^\w]+', '-', name.lower()).strip('-')
        filename = f"{filename}.jpg"
        output_path = os.path.join(PROFILE_IMAGES_DIR, filename)
        
        # Skip if already exists
        if os.path.exists(output_path):
            print(f"[{i}/{len(contributors)}] Skipping {name} (@{handle}) - file exists")
            skipped += 1
            continue
        
        print(f"[{i}/{len(contributors)}] Downloading {name} (@{handle})...")
        
        if download_profile_image(handle, output_path):
            file_size = os.path.getsize(output_path)
            print(f"    ✓ Saved {filename} ({file_size / 1024:.1f} KB)")
            downloaded += 1
        else:
            print(f"    ✗ Failed to download")
            failed += 1
        
        # Be nice to Twitter's servers
        time.sleep(1)
    
    print()
    print("=" * 60)
    print(f"Summary:")
    print(f"  Downloaded: {downloaded}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    print(f"  Total: {len(contributors)}")
    print("=" * 60)

if __name__ == "__main__":
    main()

