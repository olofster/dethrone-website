#!/usr/bin/env python3
"""
Find contributors with blank avatars who have Twitter handles
"""

import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

PROJECTS_DIR = "projects"

def extract_twitter_handle(link):
    """Extract Twitter handle from a link"""
    if not link:
        return None
    
    href = link.get('href', '')
    if not href:
        return None
    
    # Match patterns like:
    # https://x.com/username
    # https://www.x.com/username
    # https://twitter.com/username
    # @username in text
    patterns = [
        r'(?:https?://)?(?:www\.)?(?:x\.com|twitter\.com)/([^/?]+)',
        r'@([a-zA-Z0-9_]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, href, re.IGNORECASE)
        if match:
            return match.group(1).lower()
    
    # Also check the link text
    text = link.get_text(strip=True)
    if text.startswith('@'):
        return text[1:].lower()
    
    return None

def find_blank_avatars_with_twitter():
    print("=" * 60)
    print("Finding Contributors with Blank Avatars and Twitter Handles")
    print("=" * 60)
    print()
    
    contributors_with_twitter = []
    
    for filename in os.listdir(PROJECTS_DIR):
        if not filename.endswith('.html'):
            continue
        
        filepath = os.path.join(PROJECTS_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all project-contributor divs
        contributors = soup.find_all('div', class_='project-contributor')
        
        for contributor in contributors:
            # Check if it has a blank avatar
            blank_avatar = contributor.find('div', class_='avatar-image blank')
            if not blank_avatar:
                continue
            
            # Check if it has an actual image (not blank)
            img_tag = contributor.find('img')
            if img_tag and 'blank' not in img_tag.get('src', '').lower():
                continue
            
            # Get the name
            name_div = contributor.find('div', class_='basic-colfax')
            if not name_div:
                continue
            
            name = name_div.get_text(strip=True)
            if not name:
                continue
            
            # Find Twitter/X link
            twitter_handle = None
            links = contributor.find_all('a', href=True)
            for link in links:
                handle = extract_twitter_handle(link)
                if handle:
                    twitter_handle = handle
                    break
            
            if twitter_handle:
                contributors_with_twitter.append({
                    'name': name,
                    'handle': twitter_handle,
                    'file': filename
                })
    
    # Remove duplicates (same name and handle)
    seen = set()
    unique_contributors = []
    for contrib in contributors_with_twitter:
        key = (contrib['name'].lower(), contrib['handle'].lower())
        if key not in seen:
            seen.add(key)
            unique_contributors.append(contrib)
    
    print(f"Found {len(unique_contributors)} unique contributors with blank avatars and Twitter handles:")
    print()
    for contrib in sorted(unique_contributors, key=lambda x: x['name'].lower()):
        print(f"  {contrib['name']:30} @{contrib['handle']}")
    
    print()
    print("=" * 60)
    print(f"Total: {len(unique_contributors)} contributors")
    print("=" * 60)
    
    return unique_contributors

if __name__ == "__main__":
    contributors = find_blank_avatars_with_twitter()

