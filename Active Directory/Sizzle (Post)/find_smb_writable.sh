#!/usr/bin/env bash
set -euo pipefail

print_usage(){
  cat <<'EOF'
Usage: find_smb_writable.sh -H HOST [-u USER] [-p PASS] [-o OUTFILE]
  -H HOST         Target host (required). Example: 10.10.10.103
  -u USER         Username (omit to try anonymous)
  -p PASS         Password (omit to try anonymous)
  -o OUTFILE      Output CSV (default ./writable_shares.csv)
  -h              Show this help
EOF
}

HOST=""
USER=""
PASS=""
OUTFILE="./writable_shares.csv"

while getopts "H:u:p:o:h" opt; do
  case $opt in
    H) HOST="$OPTARG" ;;
    u) USER="$OPTARG" ;;
    p) PASS="$OPTARG" ;;
    o) OUTFILE="$OPTARG" ;;
    h) print_usage; exit 0 ;;
    *) print_usage; exit 1 ;;
  esac
done

if [ -z "$HOST" ]; then
  echo "Host (-H) required" >&2; print_usage; exit 1
fi

# temp files & cleanup
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# create local probe file
TIMESTAMP=$(date +%s)
LOCAL_PROBE="$TMPDIR/probe-$TIMESTAMP.txt"
echo "smb-writable-test-$TIMESTAMP" > "$LOCAL_PROBE"

# create authfile to avoid escaping issues if creds provided
AUTHFILE=""
SMBCLIENT_AUTH_OPTS=""
if [ -n "$USER" ]; then
  AUTHFILE="$TMPDIR/auth.txt"
  cat > "$AUTHFILE" <<EOF
username = $USER
password = $PASS
EOF
  SMBCLIENT_AUTH_OPTS="-A $AUTHFILE"
else
  SMBCLIENT_AUTH_OPTS="-N"
fi

echo "🔍 SMB Writable Share Scanner"
echo "Host: $HOST"
echo ""

echo "Enumerating shares..."
# Get full smbclient list output and parse share names robustly (keep spaces)
SHARES_RAW=$(smbclient -L "//$HOST" -m SMB3 $SMBCLIENT_AUTH_OPTS 2>/dev/null || true)
# Extract shares: parse each line with share name, look for Disk types
SHARES=$(printf '%s' "$SHARES_RAW" | awk '
  /Sharename/ { in_shares=1; next }
  /^[[:space:]]*$/ { in_shares=0 }
  in_shares && /^[[:space:]]*[^[:space:]-]/ {
    if ($0 ~ /Disk[[:space:]]*/) {
      gsub(/[[:space:]]*Disk.*$/, "")
      gsub(/^[[:space:]]*/, "")
      gsub(/[[:space:]]*$/, "")
      if (length($0) > 0 && $0 != "IPC$") print $0
    }
  }
')

if [ -z "$SHARES" ]; then
  echo "No shares enumerated. Try with credentials (-u user -p pass)." >&2
  exit 1
fi

echo "Shares found: $(echo "$SHARES" | wc -l)"
echo ""

echo "host,share,path,writable,detail" > "$OUTFILE"

# helper to test a put/del at a specific path
test_write(){
  share="$1"
  path="$2"
  REMOTE_FILE="smbtest-${TIMESTAMP}.txt"
  
  if [ -n "$path" ]; then
    target_desc="$share/$path"
    CMD="cd \"$path\"; put \"$LOCAL_PROBE\" \"$REMOTE_FILE\"; del \"$REMOTE_FILE\"; exit"
  else
    target_desc="$share"
    CMD="put \"$LOCAL_PROBE\" \"$REMOTE_FILE\"; del \"$REMOTE_FILE\"; exit"
  fi

  OUT=$(smbclient "//$HOST/$share" -m SMB3 $SMBCLIENT_AUTH_OPTS -c "$CMD" 2>&1 || true)

  if printf '%s' "$OUT" | grep -qiE 'putting file|putting|uploaded|stored'; then
    printf "✅ %s\n" "$target_desc"
    printf '%s,%s,%s,yes,"%s"\n' "$HOST" "$share" "$path" "$(printf '%s' "$OUT" | tr '\n' ' ' | sed 's/"/""/g')" >> "$OUTFILE"
    return 0
  else
    printf '%s,%s,%s,no,"%s"\n' "$HOST" "$share" "$path" "$(printf '%s' "$OUT" | tr '\n' ' ' | sed 's/"/""/g')" >> "$OUTFILE"
    return 1
  fi
}

echo "🔍 SCANNING FOR WRITABLE LOCATIONS..."
echo "======================================"

# Test each share root first
printf '%s\n' "$SHARES" | while IFS= read -r share; do
  sh=$(printf '%s' "$share" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
  if test_write "$sh" ""; then
    :  # Already printed by test_write
  fi
done

# Test specific known paths that are commonly writable
COMMON_PATHS=(
  "Users/Public"
  "ZZ_ARCHIVE"
  "Temp"
  "tmp"
  "Public"
  "Upload"
  "Uploads"
)

printf '%s\n' "$SHARES" | while IFS= read -r share; do
  sh=$(printf '%s' "$share" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
  
  for path in "${COMMON_PATHS[@]}"; do
    if test_write "$sh" "$path"; then
      :  # Already printed by test_write
    fi
  done
done

echo ""
echo "✅ SCAN COMPLETE!"
echo ""
WRITABLE_COUNT=$(grep -c ",yes," "$OUTFILE" 2>/dev/null || echo "0")
if [ "$WRITABLE_COUNT" -gt 0 ]; then
  echo "🎯 Found $WRITABLE_COUNT writable location(s)"
  echo "📄 Full details saved to: $OUTFILE"
else
  echo "❌ No writable locations found"
  echo "📄 Details saved to: $OUTFILE"
fi

