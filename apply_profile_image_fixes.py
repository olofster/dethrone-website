#!/usr/bin/env python3
"""
Script to apply profile image fixes from commit 8537061.
This adds blank avatars to contributors and replaces broken URLs.
"""

import os
import re
from pathlib import Path

PROJECTS_DIR = Path("projects")

def fix_project_contributor_avatars(content):
    """Fix project contributor avatars - add blank avatars where missing."""
    # Pattern to find project-contributor divs that don't have an avatar-image or img
    # Look for: <div class="project-contributor"> followed by <div> (without img or avatar-image before it)
    
    # First, let's find all project-contributor sections
    pattern = r'(<div class="project-contributor">\s*)(<div[^>]*>|</div>|<img|<div class="avatar-image)'
    
    def add_blank_avatar(match):
        full_match = match.group(0)
        # Check if this contributor already has an img or avatar-image
        if '<img' in full_match or 'avatar-image' in full_match:
            return full_match
        
        # Check if the next tag after project-contributor is a <div> (not img or avatar-image)
        # This means we need to add a blank avatar
        if re.search(r'<div class="project-contributor">\s*<div[^>]*class="avatar-image', full_match):
            return full_match
        
        # Add blank avatar before the first <div> that contains the name
        if re.search(r'<div class="project-contributor">\s*<div[^>]*>', full_match):
            return re.sub(
                r'(<div class="project-contributor">\s*)(<div[^>]*>)',
                r'\1<div class="avatar-image blank"></div>\n            \n\2',
                full_match
            )
        
        return full_match
    
    # More targeted approach: find contributors without avatars
    contributor_pattern = r'(<div class="project-contributor">\s*)(?!(?:<div class="avatar-image|<img))(<div[^>]*>\s*<div[^>]*class="basic-colfax">)'
    
    def add_blank_avatar_safe(match):
        return match.group(1) + '<div class="avatar-image blank"></div>\n            \n' + match.group(2)
    
    # Replace contributors that start with <div> (no avatar) with ones that have blank avatar
    new_content = re.sub(contributor_pattern, add_blank_avatar_safe, content)
    
    return new_content

def replace_broken_image_urls(content):
    """Replace wayback/twitter image URLs with blank avatars."""
    # Replace wayback machine URLs
    content = re.sub(
        r'<img\s+src=["\']https?://web\.archive\.org[^"\']+["\'][^>]*>',
        '<div class="avatar-image blank"></div>',
        content
    )
    
    # Replace Twitter profile image URLs (but not in comments)
    # Only replace if not inside HTML comments
    def replace_twitter_img(match):
        full_text = match.group(0)
        # Check if we're inside a comment
        start_pos = match.start()
        # Look backwards for <!--
        before = content[:start_pos]
        if '<!--' in before:
            last_comment_start = before.rfind('<!--')
            last_comment_end = before.rfind('-->', last_comment_start)
            if last_comment_end < last_comment_start:
                # We're inside a comment, don't replace
                return full_text
        return '<div class="avatar-image blank"></div>'
    
    twitter_pattern = r'<img\s+src=["\']https?://(si0|pbs)\.twimg\.com[^"\']+profile[^"\']+["\'][^>]*>'
    content = re.sub(twitter_pattern, replace_twitter_img, content)
    
    return content

def fix_file(file_path):
    """Fix profile images in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Step 1: Replace broken URLs
    content = replace_broken_image_urls(content)
    
    # Step 2: Add blank avatars to contributors without images
    content = fix_project_contributor_avatars(content)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Main function."""
    print("=" * 60)
    print("Applying Profile Image Fixes")
    print("=" * 60)
    print()
    
    updated = 0
    total = 0
    
    # Get list of files that were changed in the commit
    # For now, let's process all project files
    for project_file in sorted(PROJECTS_DIR.glob("*.html")):
        total += 1
        if fix_file(project_file):
            updated += 1
            if updated % 50 == 0:
                print(f"  Updated {updated} files...")
    
    print()
    print("=" * 60)
    print(f"Summary: {updated} files updated out of {total} checked")
    print("=" * 60)

if __name__ == "__main__":
    main()

