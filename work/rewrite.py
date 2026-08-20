#!/usr/bin/env python3
"""Rewrite captured absolute URLs to local mirror paths.

Logged as a construction-time accommodation in MIRROR_REPORT.md.
Only URL origins are changed; no markup, styles, or bytes are otherwise touched.
"""
import json, re, sys, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
MIRROR = ROOT / "mirror"
url_map = json.load(open(ROOT / "work/url_map.json"))

# index.html sits at mirror root, so local paths are already relative to it.
# The CSS lives at _ext/cdn.../css/x.css, so it needs ../../../.. prefixes.
def rel_from(depth, path):
    return "../" * depth + path

accommodations = collections.Counter()

def rewrite(text, depth):
    # longest URLs first so a prefix never eats a longer match
    for url in sorted(url_map, key=len, reverse=True):
        local = rel_from(depth, url_map[url])
        for variant in (url, url.replace("&", "&amp;")):
            if variant in text:
                n = text.count(variant)
                text = text.replace(variant, local)
                accommodations[url] += n
    return text

# --- index.html (depth 0) ---
idx = MIRROR / "index.html"
t = idx.read_text(encoding="utf-8", errors="surrogateescape")
before = len(t)
t = rewrite(t, 0)

# Protocol-relative and bare-origin leftovers
t = t.replace("https://cdn.prod.website-files.com/", "_ext/cdn.prod.website-files.com/")
idx.write_text(t, encoding="utf-8", errors="surrogateescape")
print(f"index.html: {before} -> {len(t)} bytes")

# --- captured CSS files ---
for css in MIRROR.rglob("*.css"):
    depth = len(css.relative_to(MIRROR).parts) - 1
    c = css.read_text(encoding="utf-8", errors="surrogateescape")
    c2 = rewrite(c, depth)
    if c2 != c:
        css.write_text(c2, encoding="utf-8", errors="surrogateescape")
        print(f"rewrote {css.relative_to(MIRROR)} (depth {depth})")

# --- the Google Fonts CSS was saved with a .bin extension; give it .css ---
for b in MIRROR.rglob("css__q_family_*.bin"):
    depth = len(b.relative_to(MIRROR).parts) - 1
    c = b.read_text(encoding="utf-8", errors="surrogateescape")
    c = rewrite(c, depth)
    target = b.with_suffix(".css")
    target.write_text(c, encoding="utf-8", errors="surrogateescape")
    print(f"fonts css -> {target.relative_to(MIRROR)}")

json.dump({u: n for u, n in accommodations.items()},
          open(ROOT / "work/rewrite_log.json", "w"), indent=1)
print(f"\nrewrote {len(accommodations)} distinct URLs, "
      f"{sum(accommodations.values())} total references")
