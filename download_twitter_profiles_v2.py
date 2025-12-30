#!/usr/bin/env python3
"""
Download Twitter profile pictures using alternative methods
"""

import os
import requests
import time
from find_blank_avatars_with_twitter import find_blank_avatars_with_twitter

PROFILE_IMAGES_DIR = "profile_images"

def download_via_api(handle):
    """Try downloading via Twitter API v2 or public endpoints"""
    # Twitter profile images are often available at:
    # https://unavatar.io/twitter/{handle}
    # or
    # https://api.unavatar.io/twitter/{handle}
    
    try:
        url = f"https://unavatar.io/twitter/{handle}"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code == 200 and response.headers.get('content-type', '').startswith('image'):
            return response.content
    except Exception as e:
        pass
    
    return None

def main():
    import sys
    
    # Get batch number from command line (default: 1)
    batch_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    batch_size = 25  # Process 25 at a time
    
    print("=" * 60)
    print(f"Downloading Twitter Profile Pictures - Batch {batch_num}")
    print("=" * 60)
    print()
    
    contributors = find_blank_avatars_with_twitter()
    
    # Calculate batch range
    start_idx = (batch_num - 1) * batch_size
    end_idx = min(start_idx + batch_size, len(contributors))
    batch_contributors = contributors[start_idx:end_idx]
    
    print(f"Processing contributors {start_idx + 1} to {end_idx} of {len(contributors)}")
    print()
    
    if not os.path.exists(PROFILE_IMAGES_DIR):
        os.makedirs(PROFILE_IMAGES_DIR)
    
    downloaded = 0
    failed = 0
    skipped = 0
    
    for i, contrib in enumerate(batch_contributors, 1):
        name = contrib['name']
        handle = contrib['handle']
        
        # Skip if handle has special characters that might cause issues
        if '%' in handle or handle.startswith('@'):
            handle = handle.replace('%40', '').replace('@', '')
        
        # Create filename from name (normalize)
        import re
        filename = re.sub(r'[^\w]+', '-', name.lower()).strip('-')
        filename = f"{filename}.jpg"
        output_path = os.path.join(PROFILE_IMAGES_DIR, filename)
        
        # Skip if already exists
        if os.path.exists(output_path):
            print(f"[{i}/{len(contributors)}] Skipping {name} (@{handle}) - file exists")
            skipped += 1
            continue
        
        print(f"[{i}/{len(batch_contributors)}] ({start_idx + i}/{len(contributors)}) Downloading {name} (@{handle})...")
        
        image_data = download_via_api(handle)
        if image_data:
            with open(output_path, 'wb') as f:
                f.write(image_data)
            file_size = len(image_data)
            print(f"    ✓ Saved {filename} ({file_size / 1024:.1f} KB)")
            downloaded += 1
        else:
            print(f"    ✗ Failed to download")
            failed += 1
        
        # Be nice to the API
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print(f"Batch {batch_num} Summary:")
    print(f"  Downloaded: {downloaded}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    print(f"  Processed: {len(batch_contributors)}")
    print(f"  Remaining: {len(contributors) - end_idx}")
    print()
    if end_idx < len(contributors):
        print(f"To continue, run: python3 download_twitter_profiles_v2.py {batch_num + 1}")
    print("=" * 60)

if __name__ == "__main__":
    main()

