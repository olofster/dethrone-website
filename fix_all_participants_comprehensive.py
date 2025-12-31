#!/usr/bin/env python3
"""
Comprehensively fix all participants across ALL event files:
- Use profile images from any event file where they appear
- Use Twitter handles from any event file where they appear
"""

import os
import re
from bs4 import BeautifulSoup
from collections import defaultdict

EVENTS_DIR = "events"
PROFILE_IMAGES_DIR = "profile_images"

def normalize_name(name):
    """Normalize a name for matching"""
    name = name.lower()
    name = re.sub(r'[^\w]+', '-', name)
    name = name.strip('-')
    return name

def extract_twitter_handle(link):
    """Extract Twitter handle from a link"""
    if not link:
        return None
    
    href = link.get('href', '')
    if not href:
        return None
    
    patterns = [
        r'(?:https?://)?(?:www\.)?(?:x\.com|twitter\.com)/([^/?]+)',
        r'@([a-zA-Z0-9_]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, href, re.IGNORECASE)
        if match:
            return match.group(1).lower()
    
    text = link.get_text(strip=True)
    if text.startswith('@'):
        return text[1:].lower()
    
    return None

def extract_image_from_style(style_attr):
    """Extract image path from style attribute"""
    if not style_attr:
        return None
    
    match = re.search(r'background-image:url\(([^)]+)\)', style_attr)
    if match:
        return match.group(1)
    return None

def collect_all_participant_data():
    """Collect profile images and Twitter handles from ALL event files"""
    name_to_image = {}  # normalized_name -> image_path
    name_to_handle = {}  # normalized_name -> twitter_handle
    
    print("Collecting participant data from all event files...")
    
    for filename in sorted(os.listdir(EVENTS_DIR)):
        if not filename.endswith('.html'):
            continue
        
        filepath = os.path.join(EVENTS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        participants = soup.find_all('div', class_='participant')
        
        for participant in participants:
            name_tag = participant.find('h4')
            if not name_tag:
                continue
            
            name = name_tag.get_text(strip=True)
            if not name:
                continue
            
            normalized_name = normalize_name(name)
            
            # Extract profile image
            avatar_div = participant.find('div', class_='avatar-image')
            if avatar_div:
                style = avatar_div.get('style', '')
                if style:
                    img_path = extract_image_from_style(style)
                    if img_path:
                        # Only store if we don't have one yet, or prefer profile_images folder
                        if normalized_name not in name_to_image or 'profile_images' in img_path:
                            name_to_image[normalized_name] = img_path
            
            # Extract Twitter handle
            links = participant.find_all('a', href=True)
            for link in links:
                handle = extract_twitter_handle(link)
                if handle:
                    # Store the handle (prefer existing if already set)
                    if normalized_name not in name_to_handle:
                        name_to_handle[normalized_name] = handle
                    break
    
    print(f"  Found {len(name_to_image)} participants with profile images")
    print(f"  Found {len(name_to_handle)} participants with Twitter handles")
    return name_to_image, name_to_handle

def update_event_file(filepath, name_to_image, name_to_handle):
    """Update a single event file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    soup = BeautifulSoup(content, 'html.parser')
    
    updated = False
    participants = soup.find_all('div', class_='participant')
    
    for participant in participants:
        name_tag = participant.find('h4')
        if not name_tag:
            continue
        
        name = name_tag.get_text(strip=True)
        if not name:
            continue
        
        normalized_name = normalize_name(name)
        
        # 1. Fix profile image
        if normalized_name in name_to_image:
            img_path = name_to_image[normalized_name]
            
            # Check current avatar state
            blank_avatar = participant.find('div', class_='avatar-image blank')
            avatar_div = participant.find('div', class_='avatar-image')
            
            if blank_avatar:
                # Replace blank avatar with image
                blank_avatar['style'] = f"background-image:url({img_path})"
                blank_avatar['class'] = ['avatar-image']
                updated = True
            elif avatar_div:
                # Check if it has a style
                current_style = avatar_div.get('style', '')
                if not current_style or 'blank' in str(avatar_div.get('class', [])):
                    # Update to use the image
                    avatar_div['style'] = f"background-image:url({img_path})"
                    if 'blank' in avatar_div.get('class', []):
                        avatar_div['class'] = ['avatar-image']
                    updated = True
            else:
                # No avatar div - create one
                name_div = participant.find('div', class_='name basic-colfax')
                if name_div:
                    new_avatar = soup.new_tag("div", class_="avatar-image")
                    new_avatar['style'] = f"background-image:url({img_path})"
                    name_div.insert(0, new_avatar)
                    updated = True
        
        # 2. Fix Twitter handle
        if normalized_name in name_to_handle:
            handle = name_to_handle[normalized_name]
            
            # Check if Twitter handle already exists
            existing_links = participant.find_all('a', href=True)
            has_twitter_link = False
            for link in existing_links:
                href = link.get('href', '')
                if handle in href.lower() or f'x.com/{handle}' in href.lower() or f'twitter.com/{handle}' in href.lower():
                    has_twitter_link = True
                    break
            
            if not has_twitter_link:
                # Find the name-area div to add Twitter link
                name_area = participant.find('div', class_='name-area')
                if name_area:
                    # Check if there's already a link
                    existing_link = name_area.find('a', href=True)
                    if not existing_link:
                        # Add Twitter link
                        new_link = soup.new_tag("a", href=f"https://x.com/{handle}")
                        new_p = soup.new_tag("p")
                        new_p.string = f"@{handle}"
                        new_link.append(new_p)
                        name_area.append(new_link)
                        updated = True
                    else:
                        # Update existing link if it doesn't have the correct handle
                        href = existing_link.get('href', '')
                        if handle not in href.lower():
                            existing_link['href'] = f"https://x.com/{handle}"
                            # Update the text
                            p_tag = existing_link.find('p')
                            if p_tag:
                                p_tag.string = f"@{handle}"
                            updated = True
    
    if updated:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True
    return False

def main():
    print("=" * 60)
    print("Comprehensive Fix: All Participants Across All Event Files")
    print("=" * 60)
    print()
    
    # Collect all data from all files first
    name_to_image, name_to_handle = collect_all_participant_data()
    print()
    
    # Update all event files
    print("Updating all event files...")
    updated_files = []
    
    for filename in sorted(os.listdir(EVENTS_DIR)):
        if not filename.endswith('.html'):
            continue
        
        filepath = os.path.join(EVENTS_DIR, filename)
        if update_event_file(filepath, name_to_image, name_to_handle):
            updated_files.append(filename)
            print(f"  ✓ Updated: {filename}")
    
    print()
    print("=" * 60)
    total_files = len([f for f in os.listdir(EVENTS_DIR) if f.endswith('.html')])
    print(f"Summary: Updated {len(updated_files)} out of {total_files} event files")
    print("=" * 60)
    
    if len(updated_files) < total_files:
        print(f"\nNote: {total_files - len(updated_files)} files were already up-to-date or had no changes needed.")

if __name__ == "__main__":
    main()

