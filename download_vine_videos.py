#!/usr/bin/env python3
"""
Script to download Vine videos from archive.vine.co
Run this script to download the Vine videos for the Smooch Booth project.
"""

import requests
import os
import json

# Vine video IDs from the smooch-booth page
vine_ids = ['bF7U97r6OBO', 'bFmzgLOrJFX', 'bFmhEtvhDxD', 'bF7TFbT107V']

output_dir = 'videos/smooch-booth'
os.makedirs(output_dir, exist_ok=True)

print("Attempting to download Vine videos from archive.vine.co...")
print("Note: Vine was discontinued, so some videos may no longer be available.\n")

for vid_id in vine_ids:
    print(f"Processing Vine video: {vid_id}")
    try:
        # Try archive.vine.co JSON endpoint
        json_url = f"https://archive.vine.co/posts/{vid_id}.json"
        response = requests.get(json_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Try different possible video URL fields
            video_url = None
            if 'videoUrl' in data:
                video_url = data['videoUrl']
            elif 'video' in data and isinstance(data['video'], dict):
                video_url = data['video'].get('url')
            elif 'entities' in data and 'video' in data['entities']:
                video_url = data['entities']['video'].get('url')
            
            if video_url:
                print(f"  Found video URL: {video_url}")
                # Download the video
                video_response = requests.get(video_url, stream=True, timeout=30)
                if video_response.status_code == 200:
                    filename = os.path.join(output_dir, f"{vid_id}.mp4")
                    with open(filename, 'wb') as f:
                        for chunk in video_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"  ✓ Downloaded: {filename}")
                else:
                    print(f"  ✗ Failed to download video: HTTP {video_response.status_code}")
            else:
                print(f"  ✗ No video URL found in JSON response")
                print(f"  JSON keys: {list(data.keys())}")
        else:
            print(f"  ✗ JSON endpoint returned: HTTP {response.status_code}")
            # Try alternative: vine.co/v/{id}
            print(f"  Trying alternative: https://vine.co/v/{vid_id}")
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Network error: {e}")
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON decode error: {e}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()

print("\nDownload attempt complete.")
print("If videos were not available, they may have been removed from the archive.")
print("You can try accessing them directly at: https://archive.vine.co/posts/{VIDEO_ID}.json")

