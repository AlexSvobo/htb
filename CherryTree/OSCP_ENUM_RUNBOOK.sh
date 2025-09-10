#!/usr/bin/env bash
# OSCP quick enum runbook
# usage: ./OSCP_ENUM_RUNBOOK.sh <TARGET>
set -euo pipefail
KALI_IP=10.10.14.16
TARGET="$1"
if [ -z "$TARGET" ]; then
  echo "usage: $0 TARGET"
  exit 1
fi

echo "[+] Full TCP port scan"
nmap -Pn -p- -T4 --min-rate=1000 "$TARGET"

echo "[+] Top ports + scripts"
nmap -Pn -sC -sV -p22,80,443,139,445,3389,5985,5986 -T4 "$TARGET"

echo "[+] Fast UDP/TCP fuzz (rustscan if available)"
if command -v rustscan >/dev/null 2>&1; then
  rustscan -a "$TARGET" -b 2000 -u 5000 -- -sV -sC -T4
fi

echo "[+] Masscan (fast)"
if command -v masscan >/dev/null 2>&1; then
  masscan "$TARGET" -p1-65535 --rate=1000 || true
fi

echo "[+] Web discovery"
ffuf -u http://$TARGET/FUZZ -w /usr/share/wordlists/dirb/big.txt -t 50 -mc 200,301,302,401,403 -fs 0 -k || true
gobuster dir -u http://$TARGET -w /usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt -t 50 -x php,html,txt -k || true
feroxbuster -u http://$TARGET -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 50 -x php,txt,html -k || true

echo "[+] SMB / shares"
smbclient -L //$TARGET -N || true
smbmap -H "$TARGET" || true
crackmapexec smb "$TARGET" -u users.txt -p passwords.txt || true

echo "[+] AD / Kerberos checks (if DC)"
impacket-GetUserSPNs -request -dc-ip "$TARGET" DOMAIN/USER:PASS || true
certipy-ad find -u USER@DOMAIN -p 'Password' -dc-ip "$TARGET" -stdout || true

echo "[+] MSSQL quick"
impacket-mssqlclient DOMAIN/USER:PASS@"$TARGET" || true

echo "[+] finish"

echo "done"
