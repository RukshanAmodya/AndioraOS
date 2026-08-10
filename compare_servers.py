import urllib.request
import re

OFFICIAL_BASE = "https://packages.anduinos.com"
USER_BASE = "https://andiora-packages.rukshan-amodaya-e.workers.dev"

def get_links(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8')
            links = re.findall(r'href=["\'](.*?)["\']', html)
            res = []
            for l in links:
                if not l.startswith('?') and not l.startswith('#') and l not in ['../', '..', '/', 'https://caddyserver.com']:
                    res.append(l)
            return sorted(list(set(res)))
    except Exception as e:
        return [f"ERROR: {e}"]

paths_to_check = [
    "/",
    "/artifacts/",
    "/artifacts/certs/",
    "/artifacts/anduinos/",
    "/artifacts/anduinos/dists/",
    "/artifacts/anduinos/dists/resolute-addon/",
    "/artifacts/anduinos/dists/resolute-addon/main/",
    "/artifacts/anduinos/dists/resolute-addon/main/binary-amd64/",
    "/artifacts/anduinos/pool/resolute-addon/main/a/",
]

print("==========================================================================")
print(" COMPARISON: Official (packages.anduinos.com) VS User Worker Server")
print("==========================================================================\n")

for p in paths_to_check:
    print(f"--- PATH: {p} ---")
    off_links = get_links(OFFICIAL_BASE + p)
    usr_links = get_links(USER_BASE + p)
    
    print(f"Official ({len(off_links)} items): {off_links}")
    print(f"Worker   ({len(usr_links)} items): {usr_links}")
    
    missing_in_user = set(off_links) - set(usr_links)
    extra_in_user = set(usr_links) - set(off_links)
    
    if missing_in_user:
        print(f"  [MISSING IN WORKER]: {missing_in_user}")
    if extra_in_user:
        print(f"  [EXTRA IN WORKER]: {extra_in_user}")
    if not missing_in_user and not extra_in_user:
        print("  [MATCH OK]")
    print("\n")
