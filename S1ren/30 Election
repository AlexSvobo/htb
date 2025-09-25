The video you linked is a walkthrough of an Offensive Security Proving Grounds (PG) Play machine named **Election-1**. The video demonstrates a full penetration testing methodology, starting from reconnaissance to gaining a root shell.

Here are the comprehensive notes and commands for your OSCP study, structured by the stages of the exploit path:

***

## 1. Initial Reconnaissance and Web Enumeration

The first step involved identifying open services and performing in-depth web application enumeration to find an initial foothold.

### Scanning and Target Identification

| Action | Command/Tool | Notes | Timestamp |
| :--- | :--- | :--- | :--- |
| **Full Port Scan** | `nmap -p- -sc -sv <TARGET_IP> --open` | Scans all 65535 ports, runs default scripts (`-sc`), attempts service version detection (`-sv`), and only shows open ports (`--open`) for speed. | [[29:37](http://www.youtube.com/watch?v=4ls30YSlfAM&t=1777)] |
| **Port Findings** | N/A | Ports **80 (HTTP)** and **22 (SSH)** were found. SSH was deferred due to lack of credentials. | [[32:13](http://www.youtube.com/watch?v=4ls30YSlfAM&t=1933)] |
| **Hidden Path Discovery** | Manual/Web Browser | Checking `robots.txt` in the web root revealed the core application path: **`/election`**. | [[36:55](http://www.youtube.com/watch?v=4ls30YSlfAM&t=2215)] |

### Directory and File Fuzzing (Wfuzz)

The video used **`wfuzz`** for directory and file discovery against the target web application.

| Action | Command/Tool (Concept) | Findings | Timestamp |
| :--- | :--- | :--- | :--- |
| **Directory Fuzzing** | `wfuzz` with `raft-large-directories.txt` on web root (`/`) | Discovered **/phpmyadmin** and **/javascript** [[49:12](http://www.youtube.com/watch?v=4ls30YSlfAM&t=2952)] |
| **File Fuzzing** | `wfuzz` with `raft-large-files.txt` on `/election/` | Confirmed files like `index.php`, `card.php`, and directories like **/admin**, **/logs**, **/data** [[46:07](http://www.youtube.com/watch?v=4ls30YSlfAM&t=2767)] |
| **Directory Indexing** | Manual Browser Check | Directory indexing was enabled on `/election/data`, a low-priority finding that could expose files. | [[47:25](http://www.youtube.com/watch?v=4ls30YSlfAM&t=2845)] |
| **Credential Disclosure** | Manual File Check | **Crucially**, navigating to **`/election/admin/logs/system.log`** revealed plaintext credentials for a system user. | [[01:05:30](http://www.youtube.com/watch?v=4ls30YSlfAM&t=3930)] |

***

## 2. Initial Foothold

### Key Credentials and Database Access

| System/File | Credential Found | Type | Notes | Timestamp |
| :--- | :--- | :--- | :--- |
| **PHPMyAdmin** | **`root:toor`** | Default Creds | Used to gain administrative access to the MariaDB database. | [[52:02](http://www.youtube.com/watch?v=4ls30YSlfAM&t=3122)] |
| **System Log** | **`love:password`** | User Creds | Found in `/election/admin/logs/system.log`, this is the valid system user for the SSH foothold. | [[01:05:40](http://www.youtube.com/watch?v=4ls30YSlfAM&t=3940)] |
| **DB Config** | `new_user:password` | DB Creds | Found in `/election/admin/inc/con.php`, confirming a misconfiguration. | [[01:14:11](http://www.youtube.com/watch?v=4ls30YSlfAM&t=4451)] |

### Gaining a Shell (SSH)

The credentials from the log file were successfully used to log in via SSH, gaining a low-privilege shell.

| Action | Command | Result | Timestamp |
| :--- | :--- | :--- | :--- |
| **SSH Login** | `ssh love@<TARGET_IP>` | Successful login as user `love`. | [[01:07:33](http://www.youtube.com/watch?v=4ls30YSlfAM&t=4053)] |

***

## 3. Privilege Escalation (PrivEsc)

The post-exploitation phase focused on checking for common misconfigurations that allow low-privilege users to escalate to `root`.

### Post-Exploitation Enumeration (User `love`)

| Target/Concept | Key Commands | Purpose | Timestamp |
| :--- | :--- | :--- | :--- |
| **SUID/SGID Binaries** | `find / -perm -u=s -type f 2>/dev/null` | Search the entire system for binaries with the **Set-User-ID (SUID)** bit set, which run with the owner's permissions (often `root`). | [[01:16:11](http://www.youtube.com/watch?v=4ls30YSlfAM&t=4571)] |
| **Root Processes** | `ps aox | grep -i root` | Check which processes are running as the root user. | [[01:11:23](http://www.youtube.com/watch?v=4ls30YSlfAM&t=4283)] |
| **Network** | `netstat -antp` | Check listening ports for services like MySQL (tcp/3306), which may offer an alternative entry point. | [[01:12:44](http://www.youtube.com/watch?v=4ls30YSlfAM&t=4364)] |

### SUID Exploit

The `find` command revealed a non-standard SUID binary: **/usr/sbin/servu** [[01:17:15](http://www.youtube.com/watch?v=4ls30YSlfAM&t=4635)].

| Action | Command/Tool | Result | Timestamp |
| :--- | :--- | :--- | :--- |
| **Exploit Research** | `searchsploit serv-u local` | Identified a local privilege escalation exploit (**47173.sh**) for the Serv-U FTP Server. | [[01:18:03](http://www.youtube.com/watch?v=4ls30YSlfAM&t=4683)] |
| **Payload Preparation** | `searchsploit -m 47173.sh` and copied the contents to `/var/tmp/payload.shell` | Used the world-writable `/var/tmp` to stage the exploit. | [[01:19:35](http://www.youtube.com/watch?v=4ls30YSlfAM&t=4775)] |
| **Execution** | `chmod 755 payload.shell` then `./payload.shell` | The script executed, leveraging the SUID binary to spawn a root shell. | [[01:20:16](http://www.youtube.com/watch?v=4ls30YSlfAM&t=4816)] |
| **Final Proof** | `whoami` | Confirmed **root** privileges. | [[01:20:23](http://www.youtube.com/watch?v=4ls30YSlfAM&t=4823)] |

***

## Key Takeaways for OSCP

* **Be Thorough in Web Enumeration:** The foothold depended on finding a single file (`system.log`) hidden within a directory (`/admin/logs`) that was found through fuzzing.
* **Check Everything for Defaults:** The `root:toor` default credentials on `phpmyadmin` was a key pivot point, although not the final exploit path.
* **The SUID Bit is Critical:** Always run the SUID binary check. An unusual binary running as root is a major indication of an easy Privilege Escalation vector.
* **Log Everything:** The entire methodology relies on documenting findings, such as the DB credentials and the `love:password` pair, which were then used to progress.

http://googleusercontent.com/youtube_content/0