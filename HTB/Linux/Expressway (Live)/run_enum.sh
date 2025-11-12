#!/usr/bin/env bash
# Simple wrapper to run sensible TCP+UDP enumeration scans without memorizing long nmap commands.
# Usage: ./run_enum.sh 10.10.11.87

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <target> [outdir]"
  exit 1
fi

TARGET="$1"
OUTDIR="${2:-$HOME/Linux/Expressway}"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
mkdir -p "$OUTDIR"

echo "Target: $TARGET"
echo "Outputs: $OUTDIR"

echo "1) TCP full (fast) with default scripts"
TCP_OUT="$OUTDIR/${TARGET}_tcp_${TIMESTAMP}"
sudo nmap -sS -sV -sC -p- -T4 -oA "$TCP_OUT" "$TARGET"

echo "2) Focused UDP scan with high-value scripts"
UDP_OUT="$OUTDIR/${TARGET}_udp_${TIMESTAMP}"
sudo nmap -sU -sV \
  -p 53,67,68,69,111,123,137,138,139,161,162,500,514,1701,1900,4500,5353 \
  -T4 \
  --script "ike-version,tftp-enum,snmp-info,upnp-info,broadcast-dhcp-discover,dns-zone-transfer,ntp-info" \
  -oA "$UDP_OUT" -Pn --max-retries 3 --host-timeout 10m "$TARGET"

echo "3) Quick additional discovery scripts (safe)"
DISC_OUT="$OUTDIR/${TARGET}_discovery_${TIMESTAMP}"
sudo nmap -sS -sU -sV -Pn -T4 --script "discovery" -oA "$DISC_OUT" "$TARGET"

echo "All scans complete. Files in: $OUTDIR"
echo "TCP: $TCP_OUT.*  UDP: $UDP_OUT.*  DISCOVERY: $DISC_OUT.*"

echo "Tip: edit this script to adjust ports/scripts or add your own script list file."
