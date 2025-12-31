#!/usr/bin/env python3
"""
Script to copy profile images from commit 8537061 and replace wayback/twitter URLs.
"""

import os
import subprocess
import re
from pathlib import Path

PROJECTS_DIR = Path("projects")
PROFILE_IMAGES_DIR = Path("profile_images")
COMMIT_HASH = "8537061"

def copy_profile_images():
    """Copy profile images from the commit."""
    print("Copying profile images from commit...")
    
    # Get list of profile images from the commit
    result = subprocess.run(
        ["git", "show", f"{COMMIT_HASH}:profile_images/"],
        capture_output=True,
        text=True
    )
    
    # Get list of files
    result = subprocess.run(
        ["git", "show", f"{COMMIT_HASH}", "--name-only"],
        capture_output=True,
        text=True
    )
    
    profile_files = [line for line in result.stdout.split('\n') if line.startswith('profile_images/')]
    
    PROFILE_IMAGES_DIR.mkdir(exist_ok=True)
    
    copied = 0
    for profile_file in profile_files:
        if not profile_file or profile_file == 'profile_images/':
            continue
        
        filename = os.path.basename(profile_file)
        dest_path = PROFILE_IMAGES_DIR / filename
        
        # Skip if already exists
        if dest_path.exists():
            continue
        
        try:
            # Extract file from commit
            result = subprocess.run(
                ["git", "show", f"{COMMIT_HASH}:{profile_file}"],
                capture_output=True,
                check=True
            )
            
            with open(dest_path, 'wb') as f:
                f.write(result.stdout)
            
            copied += 1
            print(f"  Copied: {filename}")
        except Exception as e:
            print(f"  Error copying {filename}: {e}")
    
    print(f"\nCopied {copied} profile images")
    return copied

def replace_profile_urls():
    """Replace wayback/twitter profile image URLs with blank avatars or local images."""
    print("\nReplacing profile image URLs...")
    
    # Patterns to match
    wayback_pattern = re.compile(r'https?://(web\.archive\.org|wayback\.archive-it\.org)[^"\'>\s]+', re.IGNORECASE)
    twitter_pattern = re.compile(r'https?://(si0|pbs)\.twimg\.com/profile_images/[^"\'>\s]+', re.IGNORECASE)
    
    replaced = 0
    
    for project_file in PROJECTS_DIR.glob("*.html"):
        with open(project_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace wayback URLs with blank avatar
        content = wayback_pattern.sub(
            '<div class="avatar-image blank"></div>',
            content
        )
        
        # Replace twitter URLs with blank avatar (most common case)
        # Check if we have a local image first by looking at the filename pattern
        def replace_twitter_url(match):
            # For now, just replace with blank avatar
            # In the original commit, some were replaced with local images
            return '<div class="avatar-image blank"></div>'
        
        content = twitter_pattern.sub(replace_twitter_url, content)
        
        if content != original_content:
            with open(project_file, 'w', encoding='utf-8') as f:
                f.write(content)
            replaced += 1
            print(f"  Updated: {project_file.name}")
    
    print(f"\nUpdated {replaced} project files")
    return replaced

if __name__ == "__main__":
    print("=" * 60)
    print("Copying Profile Images and Replacing URLs")
    print("=" * 60)
    
    copied = copy_profile_images()
    updated = replace_profile_urls()
    
    print("=" * 60)
    print(f"Summary: {copied} images copied, {updated} files updated")
    print("=" * 60)

