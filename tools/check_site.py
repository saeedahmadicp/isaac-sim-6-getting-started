"""Fail (exit 1) if any page in site/ links to a missing file or a missing #anchor.

    python3 tools/check_site.py
"""

import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

pages = sorted(f for f in os.listdir(SITE) if f.endswith(".html"))
ids = {p: set(re.findall(r'\sid="([^"]+)"', open(os.path.join(SITE, p)).read())) for p in pages}
broken = []
for p in pages:
    html = open(os.path.join(SITE, p)).read()
    for url in re.findall(r'(?:href|src)="([^"]+)"', html):
        if url.startswith(("http:", "https:", "mailto:", "data:")):
            continue
        path, _, frag = url.partition("#")
        target = os.path.normpath(os.path.join(SITE, urllib.parse.unquote(path))) if path else os.path.join(SITE, p)
        if not os.path.exists(target):
            broken.append(f"{p}: missing {url}")
        elif frag and target.endswith(".html") and frag not in ids.get(os.path.basename(target), set()):
            broken.append(f"{p}: missing anchor {url}")

print(f"checked {len(pages)} pages")
if broken:
    print("\n".join(broken))
    sys.exit(1)
print("all links and anchors resolve")
