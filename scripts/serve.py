#!/usr/bin/env python3
"""open-mirror local server.

Serves a captured mirror with the serving contract modern sites need:
- exact path resolution with correct content types
- HTTP Range (byte-range) support for video/audio seeking
- query-aware resolution via a query-variant map (from manifest.json)
- optional SPA fallback to index.html for client-routed apps
- optional cross-origin isolation headers (COOP/COEP) for WASM threads

Usage:
  python serve.py --root mirror --port 8080
  python serve.py --root mirror --port 8080 --spa
  python serve.py --root mirror --manifest manifest.json --isolate
"""
import argparse
import json
import os
import posixpath
import re
import sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote

EXTRA_TYPES = {
    ".html": "text/html; charset=utf-8", ".htm": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8", ".mjs": "text/javascript; charset=utf-8",
    ".json": "application/json", ".map": "application/json",
    ".webmanifest": "application/manifest+json", ".manifest": "application/manifest+json",
    ".wasm": "application/wasm",
    ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp",
    ".avif": "image/avif", ".ico": "image/x-icon",
    ".woff": "font/woff", ".woff2": "font/woff2", ".ttf": "font/ttf",
    ".otf": "font/otf", ".eot": "application/vnd.ms-fontobject",
    ".mp4": "video/mp4", ".webm": "video/webm", ".mov": "video/quicktime",
    ".m4v": "video/x-m4v", ".ogv": "video/ogg",
    ".mp3": "audio/mpeg", ".wav": "audio/wav", ".ogg": "audio/ogg",
    ".m4a": "audio/mp4", ".flac": "audio/flac", ".aac": "audio/aac",
    ".glb": "model/gltf-binary", ".gltf": "model/gltf+json",
    ".hdr": "application/octet-stream", ".exr": "application/octet-stream",
    ".ktx": "application/octet-stream", ".ktx2": "application/octet-stream",
    ".drc": "application/octet-stream", ".bin": "application/octet-stream",
    ".basis": "application/octet-stream", ".dds": "application/octet-stream",
    ".xml": "application/xml", ".txt": "text/plain; charset=utf-8",
    ".pdf": "application/pdf", ".zip": "application/zip",
    ".mpd": "application/dash+xml", ".m3u8": "application/vnd.apple.mpegurl",
    ".ts": "video/mp2t", ".vtt": "text/vtt",
}

RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")


class MirrorHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    root = "."
    spa = False
    isolate = False
    query_map = {}  # "path?query" -> local relative path
    access_log_path = None

    # ---------- resolution ----------
    def _safe_join(self, rel):
        rel = posixpath.normpath(unquote(rel)).lstrip("/")
        if rel.startswith("..") or rel == "..":
            return None
        full = os.path.normpath(os.path.join(self.root, rel))
        if not full.startswith(os.path.abspath(self.root)):
            return None
        return full

    def _resolve(self, path, query):
        # 1. query-variant map (exact "path?query" key)
        if query:
            key = f"{path}?{query}"
            if key in self.query_map:
                return self._safe_join(self.query_map[key]), 200
        # 2. exact path
        candidates = [path]
        if path.endswith("/"):
            candidates = [path + "index.html", path + "index.htm"]
        else:
            candidates += [path + "/index.html", path + ".html"]
        for cand in candidates:
            full = self._safe_join(cand)
            if full and os.path.isfile(full):
                return full, 200
        # 3. SPA fallback (only for navigations, i.e. no file extension)
        if self.spa and "." not in posixpath.basename(path):
            full = self._safe_join("index.html")
            if full and os.path.isfile(full):
                return full, 200
        return None, 404

    # ---------- response ----------
    def _headers_common(self, ctype, length, extra=None):
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(length))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        if self.isolate:
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
            self.send_header("Cross-Origin-Resource-Policy", "cross-origin")
        if extra:
            for k, v in extra.items():
                self.send_header(k, v)

    def _serve_file(self, full, head_only=False):
        size = os.path.getsize(full)
        ext = os.path.splitext(full)[1].lower()
        ctype = EXTRA_TYPES.get(ext, "application/octet-stream")
        range_header = self.headers.get("Range")

        if range_header:
            m = RANGE_RE.match(range_header.strip())
            if m:
                start_s, end_s = m.groups()
                if start_s == "" and end_s == "":
                    start, end = 0, size - 1
                elif start_s == "":  # suffix range: last N bytes
                    n = min(int(end_s), size)
                    start, end = size - n, size - 1
                else:
                    start = int(start_s)
                    end = int(end_s) if end_s else size - 1
                    end = min(end, size - 1)
                if start > end or start >= size:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                length = end - start + 1
                self.send_response(206)
                self._headers_common(ctype, length,
                                     {"Content-Range": f"bytes {start}-{end}/{size}"})
                self.end_headers()
                if head_only:
                    return
                with open(full, "rb") as f:
                    f.seek(start)
                    remaining = length
                    while remaining > 0:
                        chunk = f.read(min(65536, remaining))
                        if not chunk:
                            break
                        try:
                            self.wfile.write(chunk)
                        except (BrokenPipeError, ConnectionResetError):
                            return
                        remaining -= len(chunk)
                return

        self.send_response(200)
        self._headers_common(ctype, size)
        self.end_headers()
        if head_only:
            return
        with open(full, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return

    def _handle(self, head_only):
        parsed = urlparse(self.path)
        full, status = self._resolve(parsed.path, parsed.query)
        if status == 200 and full:
            self._serve_file(full, head_only=head_only)
        else:
            body = b"404 - not in mirror\n"
            self.send_response(404)
            self._headers_common("text/plain; charset=utf-8", len(body))
            self.end_headers()
            if not head_only:
                self.wfile.write(body)

    def do_GET(self):
        self._handle(head_only=False)

    def do_HEAD(self):
        self._handle(head_only=True)

    def log_message(self, fmt, *args):
        line = "%s - %s" % (self.address_string(), fmt % args)
        print(line, file=sys.stderr)
        if self.access_log_path:
            with open(self.access_log_path, "a") as f:
                f.write(line + "\n")


def main():
    ap = argparse.ArgumentParser(description="open-mirror local server")
    ap.add_argument("--root", default="mirror", help="mirror root directory")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--spa", action="store_true",
                    help="fall back to /index.html for extensionless routes")
    ap.add_argument("--isolate", action="store_true",
                    help="send COOP/COEP headers (SharedArrayBuffer / WASM threads)")
    ap.add_argument("--manifest", default=None,
                    help="manifest.json containing a query_variants map")
    ap.add_argument("--access-log", default=None,
                    help="append access log lines to this file (dependency gate evidence)")
    args = ap.parse_args()

    MirrorHandler.root = os.path.abspath(args.root)
    MirrorHandler.spa = args.spa
    MirrorHandler.isolate = args.isolate
    MirrorHandler.access_log_path = args.access_log
    if args.manifest and os.path.isfile(args.manifest):
        with open(args.manifest) as f:
            MirrorHandler.query_map = json.load(f).get("query_variants", {})

    srv = ThreadingHTTPServer((args.host, args.port), MirrorHandler)
    print(f"Serving {MirrorHandler.root} at http://{args.host}:{args.port} "
          f"(spa={args.spa}, isolate={args.isolate}, "
          f"query_variants={len(MirrorHandler.query_map)})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
