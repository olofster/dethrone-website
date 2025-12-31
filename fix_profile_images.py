#!/usr/bin/env python3
"""
Script to replace wayback/twitter profile images with blank avatars and local images.
This replicates the changes from commit 8537061.
"""

import os
import re
from pathlib import Path

PROJECTS_DIR = Path("projects")
PROFILE_IMAGES_DIR = Path("profile_images")

# Mapping of contributor names to their profile image files
# This will be populated from existing profile_images directory
PROFILE_IMAGE_MAP = {}

def build_profile_image_map():
    """Build a map of contributor names to profile image paths."""
    if not PROFILE_IMAGES_DIR.exists():
        return
    
    for img_file in PROFILE_IMAGES_DIR.glob("*.jpg"):
        # Extract name from filename (e.g., "jan-berkel.jpg" -> "jan-berkel")
        name = img_file.stem.lower().replace("_", "-")
        PROFILE_IMAGE_MAP[name] = f"../../profile_images/{img_file.name}"
    
    print(f"Found {len(PROFILE_IMAGE_MAP)} profile images")

def get_profile_image_for_contributor(contributor_name):
    """Get profile image path for a contributor, or None if not found."""
    # Try various name formats
    name_variants = [
        contributor_name.lower().replace(" ", "-").replace("_", "-"),
        contributor_name.lower().replace(" ", "").replace("_", "-"),
        contributor_name.lower().replace("-", ""),
    ]
    
    for variant in name_variants:
        if variant in PROFILE_IMAGE_MAP:
            return PROFILE_IMAGE_MAP[variant]
    
    return None

def replace_profile_images_in_file(file_path):
    """Replace wayback/twitter profile images in a project file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = False
    
    # Pattern 1: Replace wayback machine URLs
    wayback_pattern = r'<img\s+src=["\']https?://web\.archive\.org[^"\']+["\']'
    if re.search(wayback_pattern, content):
        # Replace with blank avatar
        content = re.sub(
            wayback_pattern,
            '<div class="avatar-image blank"></div>',
            content
        )
        changes_made = True
    
    # Pattern 2: Replace Twitter profile image URLs
    twitter_pattern = r'<img\s+src=["\']https?://(si0|pbs)\.twimg\.com[^"\']+profile[^"\']+["\']'
    if re.search(twitter_pattern, content):
        # Replace with blank avatar
        content = re.sub(
            twitter_pattern,
            '<div class="avatar-image blank"></div>',
            content
        )
        changes_made = True
    
    # Pattern 3: Replace old Twitter URLs in commented sections (clean them up)
    commented_twitter = r'<!--.*?<img\s+src=["\']https?://(si0|pbs)\.twimg\.com[^"\']+["\'].*?-->'
    if re.search(commented_twitter, content, re.DOTALL):
        # Remove the entire commented block
        content = re.sub(commented_twitter, '', content, flags=re.DOTALL)
        changes_made = True
    
    # Pattern 4: Fix img tags that should be div.avatar-image.blank
    # Look for img tags in project-contributor that have broken URLs
    broken_img_pattern = r'(<div class="project-contributor">.*?<img\s+src=["\'])(https?://[^"\']+)(["\'].*?>)'
    
    def replace_broken_img(match):
        url = match.group(2)
        if 'web.archive.org' in url or 'twimg.com' in url or 'wayback' in url.lower():
            # Extract contributor name if possible to check for local image
            contributor_section = match.group(0)
            name_match = re.search(r'<div class="basic-colfax">([^<]+)</div>', contributor_section)
            if name_match:
                contributor_name = name_match.group(1).strip()
                local_img = get_profile_image_for_contributor(contributor_name)
                if local_img:
                    return match.group(1) + local_img + match.group(3)
            return match.group(1) + 'div class="avatar-image blank"></div>' + match.group(3)
        return match.group(0)
    
    new_content = re.sub(broken_img_pattern, replace_broken_img, content, flags=re.DOTALL)
    if new_content != content:
        content = new_content
        changes_made = True
    
    if changes_made and content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Main function to fix profile images in all project files."""
    print("=" * 60)
    print("Fixing Profile Images in Project Files")
    print("=" * 60)
    print()
    
    build_profile_image_map()
    print()
    
    updated = 0
    checked = 0
    
    for project_file in PROJECTS_DIR.glob("*.html"):
        checked += 1
        if replace_profile_images_in_file(project_file):
            updated += 1
            print(f"  Updated: {project_file.name}")
    
    print()
    print("=" * 60)
    print(f"Summary: {updated} files updated out of {checked} checked")
    print("=" * 60)

if __name__ == "__main__":
    main()

