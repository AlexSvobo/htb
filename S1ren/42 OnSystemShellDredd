This is a comprehensive summary of the machine walkthrough **"OnSystemShellDredd"** by S1REN from OffSec, detailing the methodology, key concepts, and exact commands used for the OSCP journey.

***

## 📝 OSCP Walkthrough Notes: OnSystemShellDredd

The walkthrough covers the process of compromising the **On System Shell Dredd** machine on PG Play, which is categorized as an **easy** box. The core concepts involve thorough enumeration of open ports, handling hidden files on FTP, proper SSH key usage, and identifying an unusual **SUID binary** for privilege escalation.

### I. Initial Enumeration

The first step is always to scan all 65,535 TCP ports (`-p-`) and perform service version detection (`-sV`) on the target IP address.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `nmap -p- -sV --open <Target_IP>` | Full port scan, service version detection, and showing only open ports. | [[31:16](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=1876)] |
| **Ports Discovered:** | **21 (FTP)** and **61000 (SSH)**. | [[34:28](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=2068)] |
| **OS Detected:** | **Debian** | [[35:24](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=2124)] |

***

### II. Initial Foothold (User Access)

The open **FTP** service allowed for an anonymous login, which was the vector for the initial foothold.

#### A. FTP and Hidden Files

The standard `dir` command failed to list files, requiring a different approach to find hidden files and directories.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `ftp <Target_IP>` | Connect to the FTP server. | [[36:08](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=2168)] |
| **Login:** | **anonymous** as the username and password. | [[36:15](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=2175)] |
| `ls -lsa` | List all files, including **hidden ones** (starting with `.`), to bypass security through obscurity. | [[37:58](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=2278)] |
| **Discovery:** | A hidden directory named **`.hana`** and the user **hana** were discovered. | [[38:09](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=2289)] |
| `cd .hana` | Navigate into the hidden directory. | [[38:19](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=2299)] |
| `get .id_rsa` | Download the private SSH key found in the directory. | [[38:51](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=2331)] |
| `bye` | Exit the FTP session. | [[39:02](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=2342)] |

#### B. SSH Login

The downloaded **`id_rsa`** key is used to log in as the user **`hana`** on the non-standard SSH port **61000**.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `chmod 600 id_rsa` | **Crucial Step:** Set the private key file permissions correctly (read/write only for the owner) as required by SSH. | [[42:28](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=2548)] |
| `ssh -i id_rsa hana@<Target_IP> -p 61000` | Log in using the private key (`-i`), the discovered user (`hana`), and the non-standard port (`-p 61000`). | [[43:34](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=2614)] |
| **Result:** | User **`hana`** shell is obtained. | [[44:03](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=2643)] |

***

### III. Privilege Escalation

After gaining the initial shell, the core focus shifts to local privilege escalation, specifically by searching for unusual binaries with the **SUID (Set User ID)** bit set.

#### A. Post-Exploitation Check

The first checks confirm the low-privileged state and the lack of an immediate, easy path to root.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `whoami` / `id` | Confirm the current user and group memberships. | [[44:44](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=2684)] |
| `sudo -l` | Check if the user has permissions to run any commands as another user (e.g., root) via `sudo`. | [[45:00](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=2700)] |

#### B. SUID Binary Discovery and Exploit

Privilege escalation was achieved by finding an exotic SUID binary that could be abused to execute commands as **root**.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `find / -perm -u=s -type f 2>/dev/null` | **Standard Command:** Search the entire filesystem for files with the **SUID bit set** (runs with the file owner's privileges, e.g., root). | [[01:07:13](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=4033)] |
| **Discovery:** | The unusual SUID binary **`/usr/bin/cpulimit`** was discovered. | [[01:07:59](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=4079)] |
| **Exploitation (GTFOBins):** | The **cpulimit** binary is listed on [GTFOBins](https://gtfobins.github.io/gtfobins/cpulimit/), which provides instructions on how to leverage it for privilege escalation. | [[01:16:14](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=4574)] |
| `cpulimit -l 100 -e /bin/sh -c 'exec /bin/sh -p'` | **Root Shell Command:** Exploits the SUID capability of `cpulimit` to execute a privileged shell (`/bin/sh -p`) as root. | [[01:16:38](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=4598)] (Implied) |
| **Result:** | **Root Shell (`#`)** is obtained, confirming full compromise. | [[01:17:08](http://www.youtube.com/watch?v=UPYHCc7PdGQ&t=4628)] |

***

## ⭐ Key Takeaways for OSCP

* **Never trust the `dir` command in FTP.** Always use `ls -lsa` or similar flags to reveal **hidden files** and directories (starting with a dot: `.`).
* **SSH Key Permissions:** Always run `chmod 600 <key_file>` on any private key you find; otherwise, the SSH client will refuse to use it.
* **Non-Standard Ports:** Always note and use non-standard ports found in your Nmap scan (e.g., SSH on **61000** instead of 22).
* **SUID Abuse:** SUID binaries are a primary focus for Linux privilege escalation. Use the `find` command to locate them, and cross-reference any unusual binaries with **GTFOBins** to find exploit techniques.

http://googleusercontent.com/youtube_content/0