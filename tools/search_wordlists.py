#!/usr/bin/env python3
"""
search_wordlists.py

Search recursively through common wordlist repos (/usr/share/seclists and /usr/share/wordlists)
for filenames that match a keyword, and optionally search file contents for a keyword.

Usage:
  ./search_wordlists.py -k crushftp
  ./search_wordlists.py -k sql -c injection --max-size 50000

Outputs matches to stdout and can optionally write a JSON results file.

"""

import argparse
import os
import fnmatch
import json
import sys
from pathlib import Path


def iter_files(roots, follow_symlinks=False):
    for root in roots:
        p = Path(root)
        if not p.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(p, followlinks=follow_symlinks):
            for f in filenames:
                yield Path(dirpath) / f


def search_wordlists(roots, name_kw=None, content_kw=None, max_size=200000, ignore_ext=None):
    results = []
    for fp in iter_files(roots):
        try:
            # skip special files and large files
            if fp.is_symlink():
                continue
            size = fp.stat().st_size
            if size > max_size:
                continue
            name = fp.name.lower()
            matched_name = (name_kw and name_kw.lower() in name) or (not name_kw)
            matched_content = False
            content_snippet = None

            if content_kw and matched_name or content_kw and not name_kw:
                # try reading text safely
                try:
                    text = fp.read_text(errors='ignore')
                except Exception:
                    text = ''
                if content_kw.lower() in text.lower():
                    matched_content = True
                    # get a snippet
                    idx = text.lower().find(content_kw.lower())
                    start = max(0, idx-60)
                    content_snippet = text[start:start+180].replace('\n','\\n')

            if matched_name or matched_content:
                results.append({
                    'path': str(fp),
                    'size': size,
                    'matched_name': matched_name,
                    'matched_content': matched_content,
                    'snippet': content_snippet,
                })
        except Exception:
            continue

    return results


def main():
    parser = argparse.ArgumentParser(description='Search wordlists and SecLists for filenames and content.')
    parser.add_argument('-k','--keyword', help='Keyword to match filenames', required=False)
    parser.add_argument('-c','--content', help='Keyword to search inside files (optional)', required=False)
    parser.add_argument('-r','--roots', help='Comma-separated roots to search (defaults to /usr/share/seclists,/usr/share/wordlists)', default='/usr/share/seclists,/usr/share/wordlists')
    parser.add_argument('--max-size', type=int, default=200000, help='Skip files larger than this many bytes (default 200k)')
    parser.add_argument('-o','--output', help='Write results JSON to this file', required=False)
    parser.add_argument('--follow-symlinks', action='store_true', help='Follow symlinks while walking')
    args = parser.parse_args()

    roots = [r for r in args.roots.split(',') if r]
    if not args.keyword and not args.content:
        print('Specify at least --keyword or --content', file=sys.stderr)
        sys.exit(2)

    res = search_wordlists(roots, name_kw=args.keyword, content_kw=args.content, max_size=args.max_size, ignore_ext=None)

    print(f'Found {len(res)} matches')
    for r in res:
        flags = []
        if r['matched_name']:
            flags.append('NAME')
        if r['matched_content']:
            flags.append('CONTENT')
        print(f"[{','.join(flags)}] {r['path']} (size={r['size']})")
        if r['snippet']:
            print(f"  ...{r['snippet']}...")

    if args.output:
        try:
            with open(args.output,'w') as f:
                json.dump(res, f, indent=2)
            print('Wrote results to', args.output)
        except Exception as e:
            print('Failed to write output:', e)


if __name__ == '__main__':
    main()
