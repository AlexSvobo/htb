#!/usr/bin/env python3
"""
joomla_component_probe.py

Recursively crawl a Joomla components directory and report which URLs return
meaningful content vs blank/empty pages. Designed to be run from your box
against internal targets. Saves results to JSON and prints a short report.

Usage examples (PowerShell):
  python tools\joomla_component_probe.py \
    --base-url "http://192.168.195.79/joomla/administrator/components/" \
    --max-depth 2 --concurrency 8 --insecure --output results.json

"""
from __future__ import annotations

import argparse
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from typing import Set, Dict, List

import requests
from bs4 import BeautifulSoup


def norm_url(base: str, href: str) -> str:
    if href.startswith('http://') or href.startswith('https://'):
        return href
    if href.startswith('/'):
        # join host root with href
        from urllib.parse import urlparse, urljoin

        up = urlparse(base)
        root = f"{up.scheme}://{up.netloc}"
        return urljoin(root, href)
    # relative
    from urllib.parse import urljoin

    return urljoin(base, href)


class Probe:
    def __init__(self, base_url: str, max_depth: int = 2, timeout: int = 10, verify: bool = True, concurrency: int = 8):
        self.base_url = base_url.rstrip('/') + '/'
        self.max_depth = max_depth
        self.timeout = timeout
        self.verify = verify
        self.concurrency = concurrency

        self.visited: Set[str] = set()
        self.lock = threading.Lock()
        self.results: Dict[str, Dict] = {}

    def is_blank(self, text: str) -> bool:
        # consider blank if length small and no alphanumeric characters
        if not text:
            return True
        s = text.strip()
        if len(s) < 12:
            # if there's no letter or digit, it's blank-ish
            return not any(c.isalnum() for c in s)
        return False

    def fetch(self, url: str) -> Dict:
        try:
            r = requests.get(url, timeout=self.timeout, verify=self.verify, allow_redirects=True)
        except Exception as e:
            return {"url": url, "error": str(e)}

        entry = {"url": url, "status_code": r.status_code, "length": len(r.content)}

        # attempt to get a short text snippet
        try:
            text = r.text
        except Exception:
            text = ''

        entry["snippet"] = (text or '')[:400]
        entry["is_blank"] = self.is_blank(entry["snippet"]) and entry["length"] < 200
        return entry

    def extract_links(self, base: str, text: str) -> List[str]:
        links: List[str] = []
        try:
            soup = BeautifulSoup(text, 'html.parser')
            for a in soup.find_all(['a', 'link', 'img', 'script']):
                href = a.get('href') or a.get('src')
                if href:
                    try:
                        nu = norm_url(base, href)
                        # only consider URLs in same path prefix
                        if nu.startswith(self.base_url.rstrip('/')):
                            links.append(nu)
                    except Exception:
                        continue
        except Exception:
            pass
        return links

    def crawl(self):
        # BFS-like crawl up to depth
        q: Queue = Queue()
        q.put((self.base_url, 0))
        self.visited.add(self.base_url)

        with ThreadPoolExecutor(max_workers=self.concurrency) as ex:
            futures = []

            while not q.empty():
                url, depth = q.get()
                futures.append(ex.submit(self.fetch, url))

                # collect and schedule children synchronously to respect depth
                entry = self.fetch(url)
                self.results[url] = entry
                if entry.get('status_code', 0) == 200 and depth < self.max_depth and not entry.get('is_blank'):
                    links = self.extract_links(url, entry.get('snippet', ''))
                    for l in links:
                        if l not in self.visited:
                            self.visited.add(l)
                            q.put((l, depth + 1))

            # ensure pending futures completed for fetches we fired
            for f in as_completed(futures):
                try:
                    res = f.result()
                    self.results.setdefault(res.get('url'), res)
                except Exception:
                    continue

    def run(self):
        self.crawl()
        return self.results


def main(argv=None):
    p = argparse.ArgumentParser(description='Probe Joomla components directory for non-blank pages.')
    p.add_argument('--base-url', required=True, help='Base components URL (trailing slash recommended).')
    p.add_argument('--max-depth', type=int, default=2, help='Max recursion depth')
    p.add_argument('--timeout', type=int, default=10, help='HTTP request timeout')
    p.add_argument('--insecure', action='store_true', help='Disable SSL verification')
    p.add_argument('--concurrency', type=int, default=8, help='Concurrent requests')
    p.add_argument('--output', default='joomla_probe_results.json', help='Output JSON file')

    args = p.parse_args(argv)

    probe = Probe(args.base_url, max_depth=args.max_depth, timeout=args.timeout, verify=not args.insecure, concurrency=args.concurrency)
    print(f"Starting probe of {args.base_url} (max-depth={args.max_depth}, concurrency={args.concurrency})")
    results = probe.run()

    # produce a compact report
    report = []
    for url, info in sorted(results.items()):
        report.append({
            'url': url,
            'status': info.get('status_code'),
            'length': info.get('length'),
            'is_blank': info.get('is_blank', False),
            'snippet': (info.get('snippet') or '')[:200]
        })

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump({'base': args.base_url, 'report': report}, f, indent=2)

    # human summary
    print('\nSummary:')
    for r in report:
        flag = 'BLANK' if r['is_blank'] else 'OK'
        print(f"{r['status']:3} {r['length']:6} {flag:6} {r['url']}")

    print(f"\nResults saved to {args.output}")


if __name__ == '__main__':
    main()
