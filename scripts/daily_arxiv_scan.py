#!/usr/bin/env python3
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
import datetime
import time

# Configuration
PDF_DIR = "/home/xavier/cohera-repo/chatgpt/pdf"
LOG_FILE = "/home/xavier/cohera-repo/chatgpt/daily_scan.log"
KEYWORDS = [
    "time crystal", "holographic principle", "active inference", 
    "free energy principle", "bioelectric", "regenerative medicine",
    "epistemic", "information geometry", "scale-free network"
]
MAX_PAPERS = 5

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

def search_arxiv(query, max_results=10):
    url = f"https://export.arxiv.org/api/query?search_query={urllib.parse.quote(query)}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    try:
        response = urllib.request.urlopen(url)
        data = response.read().decode('utf-8')
        return ET.fromstring(data)
    except Exception as e:
        log(f"Error searching ArXiv for {query}: {e}")
        return None

def download_pdf(pdf_url, title):
    filename = "".join(x for x in title if x.isalnum() or x in " _-").replace(" ", "_") + ".pdf"
    filepath = os.path.join(PDF_DIR, filename)
    
    if os.path.exists(filepath):
        log(f"Skipping {filename} (already exists)")
        return False
        
    try:
        log(f"Downloading {title}...")
        # Use a proper User-Agent to avoid 403
        req = urllib.request.Request(
            pdf_url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
            out_file.write(response.read())
        log(f"Downloaded: {filename}")
        return True
    except Exception as e:
        log(f"Failed to download {title}: {e}")
        return False

def main():
    log("Starting Daily ArXiv Scan...")
    
    # Calculate date for filtering (e.g., last 5 days to be safe)
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=5)
    
    total_downloaded = 0
    
    for keyword in KEYWORDS:
        print(f"Searching for: {keyword}...")
        root = search_arxiv(f'all:"{keyword}"', max_results=5)
        if root is None: continue
        
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            published = entry.find('{http://www.w3.org/2005/Atom}published').text
            pub_date = datetime.datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
            
            print(f"  Found: {title} ({published})")
            
            if pub_date < cutoff_date:
                print("    -> Too old, skipping.")
                continue # Skip old papers
                
            pdf_link = None
            for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                if link.attrib.get('title') == 'pdf':
                    pdf_link = link.attrib['href']
                    
            if pdf_link:
                if download_pdf(pdf_link, title):
                    total_downloaded += 1
                    
            if total_downloaded >= MAX_PAPERS:
                break
        
        if total_downloaded >= MAX_PAPERS:
            break
            
        time.sleep(3) # Be nice to API

    log(f"Scan complete. Downloaded {total_downloaded} new papers.")

if __name__ == "__main__":
    main()
