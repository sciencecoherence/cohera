#!/usr/bin/env python3
import requests
import os
import re
import html
from pathlib import Path
import difflib

# Configuration
MAIN_SITE_URL = "https://www.sciencecoherence.com"
REPO_DIR = Path("/home/xavier/cohera-repo")
SNAPSHOT_DIR = REPO_DIR / "vault" / "main_site_tracking"
SNAPSHOT_FILE = SNAPSHOT_DIR / "latest_snapshot.md"
DIFF_LOG = SNAPSHOT_DIR / "diff_log.md"

def clean_html(raw_html):
    # Remove script and style tags
    clean = re.sub(r'<(script|style).*?>.*?</\1>', '', raw_html, flags=re.DOTALL)
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', ' ', clean)
    # Decode entities
    clean = html.unescape(clean)
    # Normalize whitespace
    lines = (line.strip() for line in clean.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)

def main():
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Fetching {MAIN_SITE_URL}...")
    try:
        response = requests.get(MAIN_SITE_URL, timeout=30)
        response.raise_for_status()
        current_content = clean_html(response.text)
    except Exception as e:
        print(f"Error fetching site: {e}")
        return

    previous_content = ""
    if SNAPSHOT_FILE.exists():
        previous_content = SNAPSHOT_FILE.read_text(encoding="utf-8")
    
    if current_content != previous_content:
        print("Changes detected!")
        
        # Generate diff
        diff = difflib.unified_diff(
            previous_content.splitlines(),
            current_content.splitlines(),
            fromfile='previous_snapshot',
            tofile='current_snapshot',
            lineterm=''
        )
        
        diff_text = '\n'.join(diff)
        
        # Log the diff
        timestamp = os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip()
        log_entry = f"\n\n## Change detected at {timestamp}\n```diff\n{diff_text}\n```\n"
        
        with open(DIFF_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
        # Update snapshot
        SNAPSHOT_FILE.write_text(current_content, encoding="utf-8")
        
        print(f"Updated snapshot and logged changes to {DIFF_LOG}")
    else:
        print("No changes detected.")

if __name__ == "__main__":
    main()
