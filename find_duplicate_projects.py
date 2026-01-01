#!/usr/bin/env python3
"""
Find unlinked project files and check if they are duplicates of linked files
"""

import os
import re
from bs4 import BeautifulSoup

PROJECTS_DIR = "projects"
EVENTS_DIR = "events"

def get_project_title(filepath):
    """Extract project title from a project file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Try to find title in various ways
        # 1. <h2> tag (most common)
        h2 = soup.find('h2')
        if h2:
            return h2.get_text(strip=True)
        
        # 2. <title> tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Remove common suffixes
            title = re.sub(r'\s*-\s*ART HACK DAY.*$', '', title, flags=re.IGNORECASE)
            if title and title != "Just a moment...":
                return title
        
        # 3. og:title meta tag
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title.get('content')
        
        return None
    except Exception as e:
        return None

def get_all_project_titles():
    """Get titles from all project files"""
    project_titles = {}
    
    for filename in os.listdir(PROJECTS_DIR):
        if not filename.endswith('.html'):
            continue
        
        filepath = os.path.join(PROJECTS_DIR, filename)
        title = get_project_title(filepath)
        if title:
            # Normalize title for comparison
            normalized = normalize_title(title)
            if normalized not in project_titles:
                project_titles[normalized] = []
            project_titles[normalized].append((filename, title))
    
    return project_titles

def normalize_title(title):
    """Normalize title for comparison"""
    if not title:
        return ""
    # Convert to lowercase, remove extra whitespace, remove special chars
    normalized = title.lower()
    normalized = re.sub(r'[^\w\s]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized.strip()

def get_all_links_from_events():
    """Extract all project links from event files"""
    linked_projects = set()
    
    for filename in os.listdir(EVENTS_DIR):
        if not filename.endswith('.html'):
            continue
        
        filepath = os.path.join(EVENTS_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                match = re.search(r'projects/([^/?#]+)', href)
                if match:
                    project_name = match.group(1)
                    linked_projects.add(project_name)
        except Exception:
            continue
    
    return linked_projects

def main():
    print("=" * 60)
    print("Finding Duplicate Unlinked Project Files")
    print("=" * 60)
    print()
    
    # Get all project titles
    print("Extracting project titles from all files...")
    project_titles = get_all_project_titles()
    print(f"Found {len(project_titles)} unique project titles")
    print()
    
    # Get linked projects
    linked_projects = get_all_links_from_events()
    print(f"Projects linked from event files: {len(linked_projects)}")
    print()
    
    # Find unlinked files
    unlinked = []
    for filename in os.listdir(PROJECTS_DIR):
        if not filename.endswith('.html'):
            continue
        
        base_name = filename[:-5]
        if base_name not in linked_projects:
            unlinked.append(filename)
    
    print("=" * 60)
    print(f"Analyzing {len(unlinked)} unlinked files...")
    print("=" * 60)
    print()
    
    duplicates_found = {}
    no_duplicates = []
    
    for filename in sorted(unlinked):
        filepath = os.path.join(PROJECTS_DIR, filename)
        title = get_project_title(filepath)
        
        if not title:
            no_duplicates.append((filename, "No title found"))
            continue
        
        normalized = normalize_title(title)
        
        # Check if this title exists in other files
        if normalized in project_titles:
            files_with_title = project_titles[normalized]
            # Filter out the current file
            other_files = [f for f in files_with_title if f[0] != filename]
            
            if other_files:
                # Check if any of the other files are linked
                linked_duplicates = []
                unlinked_duplicates = []
                for other_filename, other_title in other_files:
                    other_base = other_filename[:-5]
                    if other_base in linked_projects:
                        linked_duplicates.append((other_filename, other_title))
                    else:
                        unlinked_duplicates.append((other_filename, other_title))
                
                if linked_duplicates:
                    duplicates_found[filename] = {
                        'title': title,
                        'linked_duplicates': linked_duplicates,
                        'unlinked_duplicates': unlinked_duplicates
                    }
                elif unlinked_duplicates:
                    # All duplicates are also unlinked
                    no_duplicates.append((filename, f"Title: '{title}' (has unlinked duplicates: {[f[0] for f in unlinked_duplicates]})"))
            else:
                no_duplicates.append((filename, f"Title: '{title}' (no duplicates found)"))
        else:
            no_duplicates.append((filename, f"Title: '{title}' (no duplicates found)"))
    
    # Print results
    if duplicates_found:
        print("UNLINKED FILES WITH LINKED DUPLICATES:")
        print("=" * 60)
        for unlinked_file, info in sorted(duplicates_found.items()):
            print(f"\n{unlinked_file}")
            print(f"  Title: {info['title']}")
            print(f"  Linked duplicates:")
            for dup_file, dup_title in info['linked_duplicates']:
                print(f"    - {dup_file}")
            if info['unlinked_duplicates']:
                print(f"  Also unlinked:")
                for dup_file, dup_title in info['unlinked_duplicates']:
                    print(f"    - {dup_file}")
        print()
    
    print("=" * 60)
    print(f"UNLINKED FILES WITH NO DUPLICATES ({len(no_duplicates)}):")
    print("=" * 60)
    for filename, info in sorted(no_duplicates):
        print(f"  {filename}: {info}")
    print()
    
    print("=" * 60)
    print(f"Summary:")
    print(f"  Total unlinked files: {len(unlinked)}")
    print(f"  Files with linked duplicates: {len(duplicates_found)}")
    print(f"  Files with no duplicates: {len(no_duplicates)}")
    print("=" * 60)

if __name__ == "__main__":
    main()

