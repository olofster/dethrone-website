#!/usr/bin/env python3
"""
Script to add main images to project files by extracting them from event pages.
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

PROJECTS_DIR = Path("projects")
EVENTS_DIR = Path("events")

# List of project files without images
PROJECTS_WITHOUT_IMAGES = [
    "22.html",
    "alberto-de-campo-hannes-hoelzl-polypalimpsestinator-2.html",
    "amir-tanne-tsila-hassine-humanum-unknown-error.html",
    "andreas-greiner-toccata-for-pyrocystis-fusiformis.html",
    "anna-uddenberg-pdf-prive.html",
    "anthony-antonellis-alma-alloro-l-l-l-l-l-l-l-l-l-l-l-l-l.html",
    "asa-stahl-kristina-lindstrom-nicklas-marelius-mobile-mining-i-wont-give-you-my-mobile-phone-there-s-too-much-gold-in-it.html",
    "baptiste-caramiaux-marco-donnarumma-septic-v1-0.html",
    "bengt-sjolen-nicklas-marelius-data-retention-resurrection.html",
    "bernhard-garnicnig-ddosnowball.html",
    "budhaditya-chattopadhyay-mind-your-own-dizziness.html",
    "carl-emil-carlsen-christian-villum-has-been-trash-bin.html",
    "conan-lai-paul-christophe-buddy-bot.html",
    "dani-ploeger-recycled-coil.html",
    "dantheman-messenger-of-god.html",
    "david-huerta-rachel-uwa-life-gif.html",
    "dennis-de-bel-s-m-s-smoke-messaging-service.html",
    "emilie-gervais-pong-with-fruits.html",
    "gento-matsumoto-http-exonemo-com-fireplace.html",
    "geraldine-juarez-submarine-wertkorper.html",
    "helga-wretman-exercice-noise.html",
    "igal-nassima-discontent-us.html",
    "jan-berkel-fabien-artal-k-ii-n-maps-for-these-territories.html",
    "jelili-atiku-dani-ploeger-back-to-sender.html",
    "jens-evaldsson-pyrotechnic-film.html",
    "johannes-p-osterhoff-sebastian-schmieg-10-kg-from-the-new-factory.html",
    "josh-michaels-sarah-bonser-overlooked.html",
    "justin-blinder-benjamin-gaulon-bit-by-bit.html",
    "katerina-undo-in_-out-signal.html",
    "katrin-caspar-jana-linke-verflussigtes-gestange-liquefied-solid-frame.html",
    "marcel-schwittlick-artificial-out-of-body-experience.html",
    "mario-de-vega-victor-mazon-babel.html",
    "megan-mckissack-april-soetarman-the-internet-doesn-t-know-you-re-dead.html",
    "michael-ang-jonah-brucker-cohen-printcade-druckerspiel.html",
    "nancy-mauro-flude-circe-s-new-equipment.html",
    "niko-princen-detective-camera.html",
    "ole-fach-kim-asendorf-transmoji.html",
    "philipp-ronnenberg-launchpad.html",
    "quin-kennedy-laid-to-rest.html",
    "rachel-de-joode-an-argument-for-technology.html",
    "rob-spectre-a-brooklyn-chorus.html",
    "robert-boehnke-johan-uhle-honeypot.html",
    "rosa-m-nkm-n-in-the-highest-in-the-best-welcome-to-post-digital-afterglow.html",
    "rosemary-lee-jens-jorgensen-mining-the-arbitrary.html",
    "sabrina-basten-audrey-samson-field-sweeper-inc.html",
    "saso-sedlacek-jobless-avatars-the-real-curriculum.html",
    "shunya-hagiwara-rachel-uwa-akihiko-taniguchi-laura-wadden-human-cursor.html",
    "tina-tonagel-praparat.html",
    "tomoya-watanabe-strong-arm.html",
    "uno-seis-tres-thank-you-basedworld.html",
    "wolfgang-spahn-elephants-graveyard.html",
    "yuko-mohri-urban-mine.html",
]

def extract_event_link(project_file_path):
    """Extract the event link from a project file."""
    with open(project_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for pattern like: <a href="../../events/afterglow">
    pattern = r'<a\s+href=["\']\.\./\.\./events/([^"\']+)["\']'
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    return None

def find_project_image_in_event(event_file_path, project_filename, project_canonical=None):
    """Find the image for a project in the event page."""
    with open(event_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all project divs
    project_divs = soup.find_all('div', class_='project')
    
    # Try to match by filename first
    search_terms = [project_filename.replace('.html', '')]
    
    # Also try to extract project name from canonical URL if provided
    if project_canonical:
        # Extract project name from canonical like: projects/rob-spectre-a-brooklyn-chorus
        match = re.search(r'/projects/([^/]+)', project_canonical)
        if match:
            search_terms.append(match.group(1))
    
    for project_div in project_divs:
        # Find the link to this project - try multiple search terms
        link = None
        for search_term in search_terms:
            link = project_div.find('a', href=re.compile(re.escape(search_term)))
            if link:
                break
        
        if link:
            # Check if there's an img tag before the link (or in the same div)
            img = project_div.find('img')
            if img and img.get('src'):
                return img.get('src')
    
    return None

def add_image_to_project(project_file_path, image_src):
    """Add an image to a project file's project-contents section."""
    with open(project_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if image already exists
    if '<img' in content and 'project-contents' in content:
        # Check if there's already an image in project-contents
        project_contents_match = re.search(
            r'(<div class="two-thirds column" id="project-contents">.*?)(</div>\s*</div>\s*</div>)',
            content,
            re.DOTALL
        )
        if project_contents_match:
            contents_section = project_contents_match.group(1)
            if '<img' in contents_section and 'no-project-photo' not in contents_section:
                return False  # Already has an image
    
    # Replace <div class="no-project-photo"></div> or empty project-contents
    # Pattern 1: Replace no-project-photo div
    if '<div class="no-project-photo"></div>' in content:
        image_html = f'<div class="project-item">\n              <img alt="" src="{image_src}"/>\n            </div>'
        content = content.replace(
            '<div class="no-project-photo"></div>',
            image_html
        )
    else:
        # Pattern 2: Add image to empty project-contents
        # Find the project-contents div and add image inside it
        pattern = r'(<div class="two-thirds column" id="project-contents">\s*<!-- Photos using paperclip gem -->\s*)'
        replacement = r'\1<div class="project-item">\n              <img alt="" src="' + image_src + '"/>\n            </div>\n            '
        content = re.sub(pattern, replacement, content)
    
    with open(project_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    """Main function to add images to all projects."""
    print("=" * 60)
    print("Adding Images to Project Files")
    print("=" * 60)
    print()
    
    updated = 0
    not_found = []
    no_image = []
    
    for project_filename in PROJECTS_WITHOUT_IMAGES:
        project_path = PROJECTS_DIR / project_filename
        
        if not project_path.exists():
            print(f"⚠️  Project file not found: {project_filename}")
            not_found.append(project_filename)
            continue
        
        print(f"Processing: {project_filename}")
        
        # Extract event link
        event_name = extract_event_link(project_path)
        if not event_name:
            print(f"  ⚠️  Could not find event link")
            not_found.append(project_filename)
            continue
        
        # Find event file
        event_path = EVENTS_DIR / f"{event_name}.html"
        if not event_path.exists():
            print(f"  ⚠️  Event file not found: {event_name}.html")
            not_found.append(project_filename)
            continue
        
        # Extract canonical URL for better matching
        with open(project_path, 'r', encoding='utf-8') as f:
            project_content = f.read()
        canonical_match = re.search(r'<link rel="canonical" href="([^"]+)"', project_content)
        canonical = canonical_match.group(1) if canonical_match else None
        
        # Find image in event page
        image_src = find_project_image_in_event(event_path, project_filename, canonical)
        if not image_src:
            print(f"  ⚠️  No image found in event page")
            no_image.append(project_filename)
            continue
        
        # Add image to project file
        if add_image_to_project(project_path, image_src):
            print(f"  ✓ Added image: {image_src}")
            updated += 1
        else:
            print(f"  ⚠️  Image already exists or couldn't add")
        
        print()
    
    print("=" * 60)
    print(f"Summary:")
    print(f"  Updated: {updated}")
    print(f"  No image in event: {len(no_image)}")
    print(f"  Not found: {len(not_found)}")
    if no_image:
        print(f"\nProjects without images in event pages:")
        for p in no_image:
            print(f"  - {p}")
    if not_found:
        print(f"\nProjects/events not found:")
        for p in not_found:
            print(f"  - {p}")
    print("=" * 60)

if __name__ == "__main__":
    main()

