#!/usr/bin/env bash
# Download every Wix-hosted image referenced in data/site.json into images/wix/
# and rewrite site.json to point at the local copies.
# Run from anywhere:  bash liutingchun/scripts/download-images.sh
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p images/wix

urls=$(grep -oE 'https://static\.wixstatic\.com/media/[^"]+' data/site.json | sort -u)
total=$(printf '%s\n' "$urls" | grep -c . || true)
echo "Found $total Wix images"

n=0
for url in $urls; do
  n=$((n + 1))
  file="images/wix/${url##*/}"
  if [ -s "$file" ]; then
    echo "[$n/$total] skip $file"
    continue
  fi
  echo "[$n/$total] $url"
  curl -fsSL --retry 3 -o "$file" "$url" || { echo "  failed"; rm -f "$file"; }
done

# Rewrite only the URLs whose file actually downloaded.
python3 - <<'EOF'
import json, os, re
p = "data/site.json"
s = open(p, encoding="utf-8").read()
def sub(m):
    f = "images/wix/" + m.group(1)
    ok = os.path.exists(f) and os.path.getsize(f) > 0
    return f if ok else m.group(0)
s = re.sub(r'https://static\.wixstatic\.com/media/([^"/]+)', sub, s)
json.loads(s)  # sanity check
open(p, "w", encoding="utf-8").write(s)
print("site.json updated")
EOF

echo "Done. Optional: shrink big files before committing, e.g."
echo "  mogrify -resize '2000x2000>' -quality 85 images/wix/*.jpg"
