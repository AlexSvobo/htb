#!/usr/bin/env bash
# Export workspace into per-directory Markdown files for CherryTree import
# Usage: ./CherryTree/export_workspace_md.sh [WORKSPACE_ROOT] [OUTDIR]
# Default WORKSPACE_ROOT = . ; OUTDIR = CherryTree/exported

set -euo pipefail

WORKROOT="${1:-.}"
OUTDIR="${2:-CherryTree/exported}"
MAX_SIZE=${MAX_SIZE:-10485760} # 10MB
EXCLUDE=(".git" "node_modules" "__pycache__" "vendor" "$OUTDIR")

mkdir -p "$OUTDIR"

realpath() {
  # portable realpath: prefer builtin readlink, fallback to python
  if command -v readlink >/dev/null 2>&1; then
    readlink -f "$1"
  else
    python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "$1"
  fi
}

is_excluded() {
  local p="$1"
  for e in "${EXCLUDE[@]}"; do
    if [[ "$p" == *"/$e"* ]]; then
      return 0
    fi
  done
  return 1
}

echo "Exporting workspace: $WORKROOT -> $OUTDIR"

# iterate directories
cd "$WORKROOT"
IFS=$'\n'
for dir in $(find . -type d | sed 's|^\./||' | sort); do
  # skip excluded dirs
  if is_excluded "$dir"; then
    continue
  fi
  # create corresponding folder in OUTDIR
  target_dir="$OUTDIR/$dir"
  mkdir -p "$target_dir"
  # build per-directory markdown file (index.md)
  mdfile="$target_dir/index.md"
  echo "# Directory: $dir" > "$mdfile"
  echo "_Exported from workspace on: $(date -u)_" >> "$mdfile"
  echo >> "$mdfile"

  # list files (non-recursive for this dir)
  for file in $(find "$dir" -maxdepth 1 -type f 2>/dev/null | sed 's|^\./||' | sort); do
    # skip if file inside excluded path
    if is_excluded "$file"; then
      continue
    fi
    # skip output file itself
    if [[ "$file" == "$mdfile" || "$file" == "$OUTDIR"/* ]]; then
      continue
    fi
    # check readability and size
    if [[ ! -r "$file" ]]; then
      echo -e "## $file\n\n_skipped: unreadable_\n" >> "$mdfile"
      continue
    fi
    size=$(stat -c%s "$file" 2>/dev/null || echo 0)
    if [[ $size -gt $MAX_SIZE ]]; then
      echo -e "## $file\n\n(skipped binary/large file: ${size} bytes)\n" >> "$mdfile"
      continue
    fi
    mime=$(file --brief --mime-type "$file" 2>/dev/null || echo "application/octet-stream")
    if [[ "$mime" == text/* || "$mime" == */json || "$mime" == */xml || "$mime" == */yaml || "$mime" == */x-shellscript || "$mime" == */x-php || "$mime" == */javascript ]]; then
      echo -e "## $file\n" >> "$mdfile"
      echo '```' >> "$mdfile"
      # strip ANSI escapes
      sed -e 's/\x1b\[[0-9;]*[a-zA-Z]//g' "$file" >> "$mdfile" || true
      echo '```' >> "$mdfile"
    else
      echo -e "## $file\n\n(binary or non-text: mime=$mime, size=${size} bytes)\n" >> "$mdfile"
    fi
  done
done

echo "Export complete. Files under: $OUTDIR"

