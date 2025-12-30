#!/usr/bin/env python3
"""
Script to properly replace wayback/twitter profile image URLs with blank avatars or local images.
This version avoids replacing URLs in HTML comments and maps contributors to their profile images.
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup, Comment

PROJECTS_DIR = Path("projects")
PROFILE_IMAGES_DIR = Path("profile_images")

# Mapping of contributor names to their profile image files
CONTRIBUTOR_IMAGES = {
    "jan berkel": "jan-berkel.jpg",
    "fabien artal": None,  # No image available
    "olof mathé": "olof-mathe.jpg",
    "olof mathe": "olof-mathe.jpg",
    "conrad whelan": "conrad-whelan.jpg",
    "andrey zhukov": None,
    "alexander reben": "alexander-reben.jpg",
    "allison kudla": "allison-kudla.jpg",
    "anders mellbratt": "anders-mellbratt.jpg",
    "andreas": "andreas.jpg",
    "benoit verjat": "benoit-verjat.jpg",
    "blair neal": "blair-neal.jpg",
    "bradley rothenberg": "bradley-rothenberg.jpg",
    "cassie tarakajian": "cassie-tarakajian.jpg",
    "christo de klerk": "christo-de-klerk.jpg",
    "clement valla": "clement-valla.jpg",
    "daniel beauchamp": "daniel-beauchamp.jpg",
    "daniel hrynczenko": "daniel-hrynczenko.jpg",
    "david nunez": "david-nunez.jpg",
    "dennis paul": "dennis-paul.jpg",
    "derek mansen": "derek-mansen.jpg",
    "emil stenstrom": "emil-stenstrom.jpg",
    "eugena ossi": "eugena-ossi.jpg",
    "eve worthington": "eve-worthington.jpg",
    "fredrik stockman": "fredrik-stockman.jpg",
    "gabriel dunne": "gabriel-dunne.jpg",
    "go28o": "go28o.jpg",
    "gustaf josefsson": "gustaf-josefsson.jpg",
    "helga wretman": "helga-wretman.jpg",
    "jason francis": "jason-francis.jpg",
    "jelili atiku": "jelili-atiku.jpg",
    "jeremy rotsztain": "jeremy-rotsztain.jpg",
    "jerome saint clair": "jerome-saint-clair.jpg",
    "joana oberg": "joana-oberg.jpg",
    "johan nilsson": "johan-nilsson.jpg",
    "johannes p osterhoff": "johannes-p-osterhoff.jpg",
    "jonatan walck": "jonatan-walck.jpg",
    "jonathan dahan": "jonathan-dahan.jpg",
    "juan duarte regino": "juan-duarte-regino.jpg",
    "justin blinder": "justin-blinder.jpg",
    "kevin lee jr": "kevin-lee-jr.jpg",
    "lauren mccarthy": "lauren-mccarthy.jpg",
    "marcel schwittlick": "marcel-schwittlick.jpg",
    "maxwell foley": "maxwell-foley.jpg",
    "nataliya petkova": "nataliya-petkova.jpg",
    "niko princen": "niko-princen.jpg",
    "olle bjerkas": "olle-bjerkas.jpg",
    "peat wollaeger": "peat-wollaeger.jpg",
    "peter day": "peter-day.jpg",
    "philipp ronnenberg": "philipp-ronnenberg.jpg",
    "rafael coimbra": "rafael-coimbra.jpg",
    "raquel meyers": "raquel-meyers.jpg",
    "sam lavigne": "sam-lavigne.jpg",
    "sarah groff palermo": "sarah-groff-palermo.jpg",
    "shou jie eng": "shou-jie-eng.jpg",
    "simon andersson": "simon-andersson.jpg",
    "susan evans": "susan-evans.jpg",
    "tobias bernstrup": "tobias-bernstrup.jpg",
    "uno seis tres": "uno-seis-tres.jpg",
    "will brand": "will-brand.jpg",
}

def get_contributor_image(contributor_name):
    """Get the profile image filename for a contributor."""
    name_lower = contributor_name.lower().strip()
    return CONTRIBUTOR_IMAGES.get(name_lower)

def replace_profile_images_in_file(file_path):
    """Replace profile image URLs in a project file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Parse HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all img tags with wayback/twitter URLs (excluding those in comments)
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if not src:
            continue
        
        # Skip if in a comment (shouldn't happen with BeautifulSoup, but check parent)
        if any(isinstance(p, Comment) for p in img.parents):
            continue
        
        # Check if it's a wayback or twitter URL
        if 'wayback' in src.lower() or 'web.archive' in src.lower() or 'twimg.com' in src.lower():
            # Try to find the contributor name nearby
            contributor_name = None
            contributor_div = img.find_parent('div', class_='project-contributor')
            if contributor_div:
                name_elem = contributor_div.find('div', class_='basic-colfax')
                if name_elem:
                    contributor_name = name_elem.get_text(strip=True)
            
            # Get the image file for this contributor
            image_file = None
            if contributor_name:
                image_file = get_contributor_image(contributor_name)
            
            # Replace with local image or blank avatar
            if image_file and (PROFILE_IMAGES_DIR / image_file).exists():
                img['src'] = f"../../profile_images/{image_file}"
                img['alt'] = ""
            else:
                # Replace img tag with blank avatar div
                blank_div = soup.new_tag('div', attrs={'class': 'avatar-image blank'})
                img.replace_with(blank_div)
    
    new_content = str(soup)
    
    if new_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    """Main function."""
    print("=" * 60)
    print("Replacing Profile Image URLs")
    print("=" * 60)
    
    updated = 0
    
    for project_file in sorted(PROJECTS_DIR.glob("*.html")):
        if replace_profile_images_in_file(project_file):
            updated += 1
            print(f"  Updated: {project_file.name}")
    
    print("=" * 60)
    print(f"Updated {updated} project files")
    print("=" * 60)

if __name__ == "__main__":
    main()

