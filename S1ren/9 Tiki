This walkthrough for the "Tiki" machine, part of the TJ Knowles OSCP preparation list, demonstrates a full penetration test methodology including initial enumeration, exploitation of a CMS vulnerability, and a trivial privilege escalation via a misconfigured `sudo` permission.

The comprehensive notes, commands, and key takeaways are summarized below.

## 📝 OSCP Notes: Tiki Walkthrough

### 1. Initial Enumeration (Nmap & Open Ports)

The first step is always a full, comprehensive port and service scan to understand the machine's attack surface.

| Port | Service | Version/Details | Action/Goal |
| :--- | :--- | :--- | :--- |
| **22/TCP** | **SSH** | OpenSSH 8.2p1 (Ubuntu) | Requires credentials, low priority initially. |
| **80/TCP** | **HTTP** | Apache httpd 2.4.41 | High priority: Web application enumeration. |
| **139/TCP** | **SMB** | Samba 4.6.2 | High priority: Check for null sessions, shares, and users. |
| **445/TCP** | **SMB** | Samba 4.6.2 | High priority: Check for null sessions, shares, and users. |

***

### 2. HTTP Enumeration (Port 80)

The main goal is to find the web application and its version.

| Tool | Purpose | Commands & Findings | Timestamp |
| :--- | :--- | :--- | :--- |
| **Nmap** | Default Scripts (`-sC`) | Confirms the presence of `/tiki` [[25:47](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=1547)] | [[25:47](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=1547)] |
| **Wfuzz** | Directory Fuzzing | `wfuzz -c -w /opt/seclists/.../raft-large-directories.txt --hc 404 <URL>/FUZZ/` **Finding:** Directory `/tiki` [[33:14](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=1994)] | [[30:22](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=1822)] |
| **Nikto** | Vulnerability Scan | `nikto -h <URL>` **Finding:** Confirmed **/tiki** directory [[34:26](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=2066)] | [[33:55](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=2035)] |
| **Manual** | File Review | Navigate to `/tiki/changelog.txt` [[01:00:26](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=3626)] **Finding:** **Tiki CMS Groupware 21.1** [[01:00:26](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=3626)] | [[58:18](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=3498)] |

***

### 3. SMB Enumeration (Ports 139 & 445)

Exploiting misconfigurations in SMB is a common OSCP vector, often yielding credentials or files.

| Tool | Purpose | Commands & Findings | Timestamp |
| :--- | :--- | :--- | :--- |
| **enum4linux** | Null Session Check | `enum4linux -a <TARGET_IP>` **Findings:** Share **`notes`** is open [[40:44](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=2444)]; User **`silky`** found [[41:29](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=2489)] | [[40:10](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=2410)] |
| **smbclient** | Share Access | `smbclient //<TARGET_IP>/notes -N` (`-N` for null session) **File Retrieved:** `mail.txt` [[42:46](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=2566)] | [[42:26](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=2546)] |
| **cat** | Review File Content | `cat mail.txt` **Finding:** CMS credentials for user **`silky`** [[43:03](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=2583)] | [[43:00](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=2580)] |

***

### 4. Gaining Initial Access (CMS Exploitation)

The initial user credentials found did not work for SSH, so the next pivot is to the web application.

1.  **Exploit Identification:** Use **Searchsploit** to search for the found CMS version.
    * **Command:** `searchsploit tiki 21.1` [[01:00:41](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=3641)]
    * **Finding:** **Tiki CMS Groupware 21.1 - Authentication Bypass** (CVE-2020-15906) [[01:01:21](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=3681)].
2.  **Exploit Execution:** The specific exploit requires logging in as the `admin` user with no password via a modified POST request, typically done through **Burp Suite** [[01:02:54](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=3774)].
3.  **Post-Exploitation (Finding SSH Password):** Once logged in as an administrator, navigate through the CMS pages to find more sensitive information.
    * **Finding:** A "Credentials" page is found within the Wiki/CMS, which contains the SSH password for user **`silky`** [[01:05:30](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=3930)].

***

### 5. Privilege Escalation (Privesc)

With valid SSH credentials, the focus shifts to gaining a root shell.

| Step | Tool/Command | Purpose & Findings | Timestamp |
| :--- | :--- | :--- | :--- |
| **SSH Login** | `ssh silky@<TARGET_IP>` | Log in with the newly found SSH password [[01:05:41](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=3941)]. | [[01:05:35](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=3935)] |
| **Sudo Check** | **`sudo -l`** | The *most important* first command after gaining a shell. [[01:06:18](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=3978)] **Finding:** User `silky` can run **ALL commands** as root without a password. | [[01:06:18](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=3978)] |
| **Root Shell** | **`sudo /bin/bash`** | Execute the bash shell as root. [[01:07:49](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=4069)] | [[01:07:49](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=4069)] |
| **Confirmation** | `whoami` or `id` | Confirms the user is now `root` [[01:08:00](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=4080)]. | [[01:08:00](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=4080)] |

***

## 💡 Key Takeaway Concepts

The presenter emphasizes focusing on methodology and understanding vulnerability classes.

### A. Enumerating Login Forms [[46:00](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=2760)]

* **Error Messages:** Check for **username enumeration** via different error messages for invalid usernames vs. invalid passwords.
* **Injection:** Always test for **SQL Injection (SQLi)** or **Server-Side Template Injection (SSTI)**.
* **Brute Force:** Use **Hydra** or **Wfuzz** for password brute-forcing.
* **Defaults:** Google the CMS/Application for **default credentials** (e.g., `admin:admin`).

### B. Enumerating a Logged-in CMS [[50:33](http://www.youtube.com/watch?v=Gw4fAiCRmKg&t=3033)]

* **Version & Exploits:** Immediately search **Exploit-DB** for the specific version found.
* **File Uploads:** Look for **File Upload** functionality and ways to bypass restrictions to upload a webshell.
* **Configuration:** Check **user privileges** and look for administrative options to edit templates, modules, or extensions to plant executable code.
* **Sensitive Data:** Look for exposed configurations, **database information**, or other user **credentials** within the CMS's wiki or administrative pages.

***

The video can be found here: [Tiki Walkthrough with S1REN](http://www.youtube.com/watch?v=Gw4fAiCRmKg)
http://googleusercontent.com/youtube_content/0