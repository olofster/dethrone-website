#!/usr/bin/env python3
"""
Script to filter out tracking pixel files from downloaded Tumblr media.
Removes files that are very small (likely tracking pixels) or have tracking pixel patterns in their names.
"""

import os
from pathlib import Path

IMAGES_DIR = Path("tumblr_media/images")
TRACKING_DIR = Path("tumblr_media/tracking_pixels")
MIN_FILE_SIZE = 1024  # 1 KB - files smaller than this are likely tracking pixels

def filter_tracking_pixels():
    """Filter out tracking pixel files."""
    if not IMAGES_DIR.exists():
        print(f"Images directory not found: {IMAGES_DIR}")
        return
    
    # Create tracking pixels directory
    TRACKING_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Filtering Tracking Pixels")
    print("=" * 60)
    print(f"Images directory: {IMAGES_DIR}")
    print(f"Tracking pixels will be moved to: {TRACKING_DIR}")
    print(f"Minimum file size: {MIN_FILE_SIZE} bytes (1 KB)")
    print("=" * 60)
    print()
    
    moved = 0
    total_size_moved = 0
    
    # Get all image files
    image_files = list(IMAGES_DIR.glob("*"))
    
    print(f"Scanning {len(image_files)} files...")
    print()
    
    for file_path in image_files:
        if not file_path.is_file():
            continue
        
        file_size = file_path.stat().st_size
        file_name = file_path.name
        
        # Check if file is too small (likely a tracking pixel)
        is_tracking = False
        
        if file_size < MIN_FILE_SIZE:
            is_tracking = True
        
        # Check if filename contains tracking pixel patterns
        if "impixu" in file_name.lower() or "px.srvcs" in file_name.lower():
            is_tracking = True
        
        if is_tracking:
            # Move to tracking pixels directory
            dest_path = TRACKING_DIR / file_name
            try:
                file_path.rename(dest_path)
                moved += 1
                total_size_moved += file_size
                print(f"  Moved: {file_name} ({file_size} bytes)")
            except Exception as e:
                print(f"  Error moving {file_name}: {e}")
    
    print()
    print("=" * 60)
    print("Filtering Summary:")
    print(f"  Files moved: {moved}")
    print(f"  Total size moved: {total_size_moved / 1024:.2f} KB")
    print(f"  Remaining images: {len(list(IMAGES_DIR.glob('*'))) - moved}")
    print(f"  Tracking pixels location: {TRACKING_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    filter_tracking_pixels()

