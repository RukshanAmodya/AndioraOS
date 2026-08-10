import urllib.request
import re

url = "https://packages.anduinos.com/artifacts/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    links = re.findall(r'href=["\'](.*?)["\']', html)
    print("Links under /artifacts/:")
    for link in links:
        if not link.startswith('?') and not link.startswith('#'):
            print(" -", link)
except Exception as e:
    print("Error:", e)
