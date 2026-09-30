# liutingchun — 靜態網站

從 Wix 搬出來的個人網站。內容只有兩個地方：

- `data/site.json`：作品、表演、CV、朋友、文章列表、網站設定
- `posts/<slug>.md`：每篇文章的內文（Markdown）

`scripts/build.py` 會把它們產生成每一頁一個資料夾的靜態 HTML（`works/sun/`、`writing/lift-off/`…），每頁都有自己的 title、description、canonical、Open Graph、JSON-LD，並產生 `sitemap.xml`、`robots.txt`（放在網域根目錄）與文章 RSS（`writing/feed.xml`）。

```
liutingchun/
├── index.html, works/, performance/, about/, writing/, friends/   ← 自動產生，不要手改
├── data/site.json
├── posts/*.md
├── images/wix/          圖片與影片
├── assets/style.css, site.js
├── preview.html + assets/app.js   後台的草稿預覽
├── admin/               極簡後台
└── scripts/build.py, download-images.sh
```

網址：`https://aprilcoffee.github.io/liutingchun/`

## 更新內容

1. 打開 `/liutingchun/admin/`，修改後會自動存成本機草稿，「預覽草稿」可先看效果。
2. 「發佈」頁填入 fine-grained token（只給這個 repo 的 *Contents: Read and write*），按「發佈到 GitHub」。
3. GitHub Actions（`.github/workflows/build-liutingchun.yml`）會自動重跑 `build.py` 並 commit 產生的頁面，約 1–2 分鐘後上線。

直接在 GitHub 上改 `site.json` 或 `posts/*.md` 也一樣會觸發重建。

## 內容格式

- 作品說明：空一行＝分段；以 `# ` 開頭＝小標題；網址自動變連結。
- 文章：一般 Markdown。`![說明](圖片)` 會變成有圖說的圖片；單獨一行的 Vimeo / YouTube / mp4 網址會變成播放器。
- 舊網站 `liutingchun.com/...` 的連結會自動改指到新頁面（對照表在各作品的 `aliases`）。
- `hidden: true` 的作品或文章不會出現在網站。

## 網域

`site.json` 裡的 `site.base_url` 決定 canonical、分享連結與 sitemap。之後把網域指到這裡時改這個值即可；若網站放在網域根目錄，`build.py` 也會為舊的 Wix 網址（`/cv`、`/post/...`、`/sun`…）產生轉址頁。

## 連結檢查

`.github/workflows/check-links.yml` 每月 1 號檢查所有外部連結，也可在 Actions 分頁手動執行，結果在該次執行的 Summary。

## 圖片

新加入、還連到 Wix 的圖片（`static.wixstatic.com`）或影片，在本機執行：

```bash
bash liutingchun/scripts/download-images.sh
```

會下載到 `images/wix/`、轉成 webp，並改寫 `site.json` 與 `posts/*.md` 的路徑，之後 commit。

## 本機預覽

```bash
pip install markdown
python3 liutingchun/scripts/build.py
python3 -m http.server 8000      # 在 repo 根目錄執行
# http://localhost:8000/liutingchun/
```
