#!/usr/bin/env python3
"""
Find all project files that are NOT linked from any event files
"""

import os
import re
from bs4 import BeautifulSoup

PROJECTS_DIR = "projects"
EVENTS_DIR = "events"

def get_all_project_files():
    """Get all HTML files in projects directory"""
    project_files = []
    for filename in os.listdir(PROJECTS_DIR):
        if filename.endswith('.html'):
            # Get base name without .html
            base_name = filename[:-5]
            project_files.append((filename, base_name))
    return project_files

def get_all_links_from_events():
    """Extract all project links from event files"""
    linked_projects = set()
    
    for filename in os.listdir(EVENTS_DIR):
        if not filename.endswith('.html'):
            continue
        
        filepath = os.path.join(EVENTS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all links to projects
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            # Match patterns like: ../../projects/filename or /projects/filename
            match = re.search(r'projects/([^/?#]+)', href)
            if match:
                project_name = match.group(1)
                linked_projects.add(project_name)
    
    return linked_projects

def main():
    print("=" * 60)
    print("Finding Unlinked Project Files")
    print("=" * 60)
    print()
    
    # Get all project files
    project_files = get_all_project_files()
    print(f"Total project files: {len(project_files)}")
    
    # Get all linked projects
    linked_projects = get_all_links_from_events()
    print(f"Projects linked from event files: {len(linked_projects)}")
    print()
    
    # Find unlinked projects
    unlinked = []
    for filename, base_name in project_files:
        if base_name not in linked_projects:
            unlinked.append(filename)
    
    print("=" * 60)
    print(f"Unlinked project files: {len(unlinked)}")
    print("=" * 60)
    print()
    
    if unlinked:
        for filename in sorted(unlinked):
            print(f"  {filename}")
    else:
        print("  All project files are linked from event files!")
    
    print()

if __name__ == "__main__":
    main()

