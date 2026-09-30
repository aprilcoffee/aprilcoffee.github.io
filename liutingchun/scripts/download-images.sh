#!/usr/bin/env bash
# Download every Wix-hosted image/video referenced in data/site.json and posts/*.md
# into images/wix/, convert images to webp, and rewrite the references to local paths.
# Run from anywhere:  bash liutingchun/scripts/download-images.sh
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p images/wix

urls=$(grep -ohE 'https://(static|video)\.wixstatic\.com/(media|video)/[^")> ]+' data/site.json posts/*.md | sort -u)
total=$(printf '%s\n' "$urls" | grep -c . || true)
echo "Found $total Wix files"

n=0
for url in $urls; do
  n=$((n + 1))
  if [[ "$url" == https://video.wixstatic.com/* ]]; then
    # https://video.wixstatic.com/video/<id>/480p/mp4/file.mp4 -> <id>.mp4
    id=$(echo "$url" | sed -E 's#.*/video/([^/]+)/.*#\1#')
    file="images/wix/$id.mp4"
  else
    file="images/wix/${url##*/}"
  fi
  webp="${file%.*}.webp"
  if [ -s "$file" ] || [ -s "$webp" ]; then
    echo "[$n/$total] skip $file"
    continue
  fi
  echo "[$n/$total] $url"
  curl -fsSL --retry 3 -o "$file" "$url" || { echo "  failed"; rm -f "$file"; continue; }
  # Convert to webp like the rest of images/wix/ (skip gifs to keep animation, and videos).
  if command -v cwebp >/dev/null && [[ "$file" =~ \.(jpe?g|png)$ ]]; then
    cwebp -quiet -q 82 -resize 2000 0 "$file" -o "$webp" 2>/dev/null || cwebp -quiet -q 82 "$file" -o "$webp"
    rm -f "$file"
  fi
done

# Rewrite only the references whose file actually downloaded.
python3 - <<'EOF'
import glob, json, os, re

def local(url):
    m = re.match(r"https://video\.wixstatic\.com/video/([^/]+)/", url)
    names = [m.group(1) + ".mp4"] if m else [os.path.splitext(url.rsplit("/", 1)[1])[0] + ".webp", url.rsplit("/", 1)[1]]
    for name in names:
        f = "images/wix/" + name
        if os.path.exists(f) and os.path.getsize(f) > 0:
            return f
    return None

pat = re.compile(r'https://(?:static|video)\.wixstatic\.com/(?:media|video)/[^")> \n]+')
for path in ["data/site.json"] + sorted(glob.glob("posts/*.md")):
    s = open(path, encoding="utf-8").read()
    new = pat.sub(lambda m: local(m.group(0)) or m.group(0), s)
    if path.endswith(".json"):
        json.loads(new)  # sanity check
    if new != s:
        open(path, "w", encoding="utf-8").write(new)
        print("updated", path)
EOF

left=$(grep -ohE 'https://(static|video)\.wixstatic\.com/[^")> ]+' data/site.json posts/*.md | sort -u | wc -l)
echo "Done. $left Wix references left. Commit images/wix/, data/site.json and posts/."
