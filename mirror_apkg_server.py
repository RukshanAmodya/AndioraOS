#!/usr/bin/env python3
"""
AnduinOS APKG Server Full Exact Mirror Downloader
Downloads all files from https://packages.anduinos.com keeping the exact directory tree structure.
"""

import os
import sys
import urllib.request
import urllib.parse

SERVER_URL = "https://packages.anduinos.com"
OUTPUT_DIR = "./apkg_server_mirror"
SUITE = "resolute-addon"
ARCH = "amd64"

def download_file(relative_path):
    url = f"{SERVER_URL}/{relative_path.lstrip('/')}"
    local_path = os.path.join(OUTPUT_DIR, relative_path.lstrip('/'))
    
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    print(f"Downloading: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(local_path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"  [OK] Saved to: {local_path}")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed ({e}): {url}")
        return False

def main():
    print("==================================================")
    print(" Starting Full Exact APKG Server Mirror Downloader")
    print(" Server:", SERVER_URL)
    print(" Target Directory:", os.path.abspath(OUTPUT_DIR))
    print("==================================================")

    # 1. Download Certificate
    cert_path = "artifacts/certs/anduinos"
    download_file(cert_path)

    # 2. Download Distribution Metadata / Release Files
    dists_prefix = f"artifacts/anduinos/dists/{SUITE}"
    release_files = [
        f"{dists_prefix}/InRelease",
        f"{dists_prefix}/Release",
        f"{dists_prefix}/Release.gpg",
        f"{dists_prefix}/main/binary-{ARCH}/Packages",
        f"{dists_prefix}/main/binary-{ARCH}/Packages.gz",
        f"{dists_prefix}/main/binary-{ARCH}/Packages.zst",
    ]
    
    for r_file in release_files:
        download_file(r_file)

    # 3. Parse Packages File to find all pool .deb paths
    pkg_index_local = os.path.join(OUTPUT_DIR, dists_prefix, "main", f"binary-{ARCH}", "Packages")
    if not os.path.exists(pkg_index_local):
        print("ERROR: Could not find Packages index file!")
        sys.exit(1)

    deb_paths = []
    with open(pkg_index_local, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("Filename:"):
                # e.g., Filename: pool/resolute-addon/main/a/anduinos-desktop/anduinos-desktop_2.0.1-1+resolute_all.deb
                rel_deb = line.split(":", 1)[1].strip()
                deb_paths.append(f"artifacts/anduinos/{rel_deb}")

    print(f"\nFound {len(deb_paths)} packages in repository index.\n")

    # 4. Download all .deb files maintaining exact pool subfolder tree
    success_count = 0
    for deb_path in deb_paths:
        if download_file(deb_path):
            success_count += 1

    print("\n==================================================")
    print(f" SUCCESS: Mirror completed! ({success_count}/{len(deb_paths)} packages downloaded)")
    print(f" All files saved in exact structure under: {os.path.abspath(OUTPUT_DIR)}")
    print("==================================================")

if __name__ == "__main__":
    main()
