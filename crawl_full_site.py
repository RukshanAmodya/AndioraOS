import os
import sys
import re
import urllib.request
import urllib.parse

SERVER_ROOT = "https://packages.anduinos.com"
OUTPUT_DIR = "./full_packages_site_mirror"

# User-Agent to mimic browser
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

visited_urls = set()

def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as resp:
            content_type = resp.headers.get('Content-Type', '')
            if 'text/html' in content_type:
                return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[ERROR] Fetching HTML {url}: {e}")
    return None

def download_file(url, rel_path):
    local_path = os.path.join(OUTPUT_DIR, rel_path.lstrip('/'))
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        print(f"[SKIP] Already exists: {rel_path}")
        return

    print(f"[DOWNLOADING] {url} -> {rel_path}")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as resp, open(local_path, 'wb') as f:
            f.write(resp.read())
        print(f"  [OK] Saved successfully")
    except Exception as e:
        print(f"  [FAIL] Could not download {url}: {e}")

def crawl_directory(current_path=""):
    url = urllib.parse.urljoin(SERVER_ROOT, current_path)
    if url in visited_urls:
        return
    visited_urls.add(url)

    print(f"\nScanning directory: {url}")
    html = fetch_html(url)
    if not html:
        return

    # Extract all href links
    links = re.findall(r'href=["\'](.*?)["\']', html)
    
    for href in links:
        # Ignore query params, anchors, parent dir links
        if href.startswith('?') or href.startswith('#') or href in ['../', '..', '/']:
            continue
        if href.startswith('http://') or href.startswith('https://'):
            if not href.startswith(SERVER_ROOT):
                continue

        # Resolve relative link
        abs_url = urllib.parse.urljoin(url, href)
        if not abs_url.startswith(SERVER_ROOT):
            continue

        rel_path = urllib.parse.urlparse(abs_url).path

        if href.endswith('/'):
            # It's a directory -> Crawl recursively
            crawl_directory(rel_path)
        else:
            # Check if link looks like a folder listing directory not ending in /
            if any(link.endswith('/') for link in links if link.startswith(href)):
                crawl_directory(rel_path)
            else:
                # It's a file -> Download it
                download_file(abs_url, rel_path)

def main():
    print("==================================================")
    print(" Starting Complete Full Site Web Crawler & Mirror")
    print(" Target Site: https://packages.anduinos.com/")
    print(" Output Folder:", os.path.abspath(OUTPUT_DIR))
    print("==================================================")
    
    crawl_directory("/")

    print("\n==================================================")
    print(" FULL REPOSITORY CLONE FINISHED SUCCESSFULLY!")
    print(f" Saved under: {os.path.abspath(OUTPUT_DIR)}")
    print("==================================================")

if __name__ == "__main__":
    main()
