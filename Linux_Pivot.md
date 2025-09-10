# Linux Pivot Summary

This file summarizes web/low-privilege to user pivots found in the notes. Each entry includes: source note path, pivot command(s) used, and resulting user.

---

## 1) TartarSauce — www-data -> onuma
Source: `Linux/TartarSauce/notes.txt`

Pivot command:

sudo -u onuma tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh

Result: spawned a shell as `onuma` (whoami => onuma)

---

## 2) Magic — www-data -> theseus
Source: `Linux/Magic/notes.txt`

Pivot command:

su theseus
(password from DB: `Th3s3usW4sK1ng`)

Result: authenticated as `theseus` and obtained shell.

---

## 3) Popcorn — www-data -> root
Source: `Linux/Popcorn/notes.txt`

Pivot command:

./14339.sh

Result: root shell (root@popcorn:/tmp#) and `root.txt` accessible.

---

## 4) SwagShop — www-data -> root
Source: `Linux/SwagShop/notes.txt`

Pivot command:

sudo /usr/bin/vi /var/www/html/php.ini.sample -c ':!/bin/bash'

Result: root shell via sudo vi escape.

---

## 5) Nibbles — nibbler -> root
Source: `Linux/Nibbles/notes.txt`

Pivot detail:

User `nibbler` allowed to run `/home/nibbler/personal/stuff/monitor.sh` as root (NOPASSWD). Created `monitor.sh` to spawn a root shell.

Result: root via sudo NOPASSWD exploitation.

---

## 6) Bashed — www-data -> scriptmanager
Source: `Linux/Bashed/notes.txt`

Pivot detail:

`www-data` may run commands as `scriptmanager` (NOPASSWD). Used `sudo` to execute commands as `scriptmanager` and pivot.

Result: shell as `scriptmanager`.

---

## 7) SolidState — web user -> root
Source: `Linux/SolidState/notes.txt`

Pivot detail:

Reverse shell connected back and subsequently a root shell observed.

Result: root access.

---

> Notes: This summary lists explicit pivots found in the repository notes. For each pivot, verify exact command history in the referenced note files when reproducing.
