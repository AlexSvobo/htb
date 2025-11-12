#!/usr/bin/env python3
"""
webdav_enum.py

Simple WebDAV enumeration and upload helper.

Features:
- OPTIONS to fingerprint allowed methods and server headers
- PROPFIND to list contents (Depth: 0/1)
- PUT to upload a test file
- MKCOL to create a collection (directory)
- MOVE to rename/move a resource
- DELETE to remove a resource
- GET to fetch uploaded resource for verification

Depends on 'requests'. See requirements.txt in the same folder.

Usage examples:
  python tools/webdav_enum.py --url http://ftp.soulmate.htb/ --host ftp.soulmate.htb --propfind --depth 1
  python tools/webdav_enum.py --url http://ftp.soulmate.htb/ --host ftp.soulmate.htb --put /test.txt --data "hello" --verify

"""

from __future__ import annotations
import argparse
import sys
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin


def norm_url(url: str) -> str:
    if not url.endswith('/'):
        return url + '/'
    return url


def do_options(session: requests.Session, url: str, headers: dict):
    resp = session.options(url, headers=headers, allow_redirects=False)
    print(f"OPTIONS {url} -> {resp.status_code}")
    for k, v in resp.headers.items():
        if k.lower() in ('allow', 'dav', 'server', 'www-authenticate'):
            print(f"  {k}: {v}")
    return resp


def do_propfind(session: requests.Session, url: str, headers: dict, depth: int = 0):
    hdrs = headers.copy()
    hdrs.update({'Depth': str(depth), 'Content-Type': 'text/xml'})
    # Minimal propfind body that asks for allprop
    body = ('<?xml version="1.0" encoding="utf-8" ?>\n'
            '<propfind xmlns="DAV:">\n'
            '  <allprop/>\n'
            '</propfind>')
    resp = session.request('PROPFIND', url, headers=hdrs, data=body, allow_redirects=False)
    print(f"PROPFIND {url} (Depth: {depth}) -> {resp.status_code}")
    if resp.status_code in (207, 207):
        # Multi-status XML; print a short snippet
        text = resp.text
        snippet = text[:1000]
        print(snippet)
    else:
        print(resp.text[:1000])
    return resp


def do_put(session: requests.Session, url: str, headers: dict, data: bytes):
    resp = session.put(url, headers=headers, data=data, allow_redirects=False)
    print(f"PUT {url} -> {resp.status_code}")
    return resp


def do_get(session: requests.Session, url: str, headers: dict):
    resp = session.get(url, headers=headers, allow_redirects=False)
    print(f"GET {url} -> {resp.status_code}")
    if resp.status_code == 200:
        print(resp.text[:1000])
    return resp


def do_mkcol(session: requests.Session, url: str, headers: dict):
    resp = session.request('MKCOL', url, headers=headers, allow_redirects=False)
    print(f"MKCOL {url} -> {resp.status_code}")
    return resp


def do_move(session: requests.Session, url: str, dest: str, headers: dict, overwrite: bool = True):
    hdrs = headers.copy()
    hdrs.update({'Destination': dest, 'Overwrite': 'T' if overwrite else 'F'})
    resp = session.request('MOVE', url, headers=hdrs, allow_redirects=False)
    print(f"MOVE {url} -> {resp.status_code}")
    return resp


def do_delete(session: requests.Session, url: str, headers: dict):
    resp = session.delete(url, headers=headers, allow_redirects=False)
    print(f"DELETE {url} -> {resp.status_code}")
    return resp


def build_session(args) -> requests.Session:
    s = requests.Session()
    if args.insecure:
        s.verify = False
    if args.auth:
        if ':' in args.auth:
            u, p = args.auth.split(':', 1)
            s.auth = HTTPBasicAuth(u, p)
        else:
            print("Invalid auth format. Use user:pass")
            sys.exit(1)
    return s


def main() -> None:
    p = argparse.ArgumentParser(description='Simple WebDAV enumeration and upload tool')
    p.add_argument('--url', '-u', required=True, help='Base URL of target (e.g. http://ftp.soulmate.htb/)')
    p.add_argument('--host', '-H', help='Host header to use (e.g. ftp.soulmate.htb)')
    p.add_argument('--auth', help='Basic auth as user:pass')
    p.add_argument('--insecure', action='store_true', help='Disable TLS verification')
    p.add_argument('--options', action='store_true', help='Send OPTIONS request')
    p.add_argument('--propfind', action='store_true', help='Send PROPFIND request')
    p.add_argument('--depth', type=int, default=1, help='Depth for PROPFIND (0 or 1)')
    p.add_argument('--put', help='PUT a file at this path (relative to base), e.g. /test.txt')
    p.add_argument('--data', help='String data to PUT (if omitted, small default used)')
    p.add_argument('--mkcol', help='MKCOL at this path (relative to base), e.g. /newdir/')
    p.add_argument('--move', nargs=2, metavar=('SRC','DST'), help='MOVE src_path dst_path (both relative to base)')
    p.add_argument('--delete', help='DELETE a path (relative to base)')
    p.add_argument('--get', help='GET a resource (relative to base)')
    p.add_argument('--verify', action='store_true', help='After PUT try GET/PROPFIND to verify')
    args = p.parse_args()

    base = norm_url(args.url)
    session = build_session(args)
    headers = {}
    if args.host:
        headers['Host'] = args.host

    # OPTIONS
    if args.options:
        do_options(session, base, headers)

    # PROPFIND
    if args.propfind:
        do_propfind(session, base, headers, depth=args.depth)

    # MKCOL
    if args.mkcol:
        target = urljoin(base, args.mkcol.lstrip('/'))
        do_mkcol(session, target, headers)

    # PUT
    if args.put:
        target = urljoin(base, args.put.lstrip('/'))
        data = args.data.encode() if args.data is not None else b'WebDAV test upload\n'
        r = do_put(session, target, headers, data)
        if args.verify and r.status_code in (200, 201, 204):
            # try GET first
            do_get(session, target, headers)
            # and PROPFIND the parent
            parent = '/'.join(target.rstrip('/').split('/')[:-1]) + '/'
            do_propfind(session, parent, headers, depth=1)

    # MOVE
    if args.move:
        src, dst = args.move
        src_url = urljoin(base, src.lstrip('/'))
        dst_url = urljoin(base, dst.lstrip('/'))
        do_move(session, src_url, dst_url, headers)

    # DELETE
    if args.delete:
        target = urljoin(base, args.delete.lstrip('/'))
        do_delete(session, target, headers)

    # GET
    if args.get:
        target = urljoin(base, args.get.lstrip('/'))
        do_get(session, target, headers)


if __name__ == '__main__':
    main()
