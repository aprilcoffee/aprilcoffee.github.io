# liutingchun — 靜態網站

從 Wix 搬出來的個人網站。沒有建置步驟：所有內容都在 `data/site.json`，頁面由 `assets/app.js` 讀取後產生。

```
liutingchun/
├── index.html          網站（側欄 + 全螢幕內容）
├── assets/style.css
├── assets/app.js
├── data/site.json      ← 全部內容：作品、表演、CV、文章、朋友、網站設定
├── images/             本地圖片（後台上傳的圖也會放這裡）
├── admin/              極簡後台
└── scripts/download-images.sh
```

網址：`https://aprilcoffee.github.io/liutingchun/`
頁面：`#/works`、`#/works/<slug>`、`#/performance`、`#/about`、`#/writing`、`#/friends`

## 後台

打開 `https://aprilcoffee.github.io/liutingchun/admin/`

- 每次修改都會自動存成**本機草稿**（瀏覽器 localStorage），左下「預覽草稿」可看效果。
- 發佈：
  - **A. 直接存到 GitHub**：在「發佈」頁填 fine-grained token（只給這個 repo 的 *Contents: Read and write*），按「發佈到 GitHub」。作品頁的「上傳圖片」也用同一個 token，圖會存到 `images/<slug>/`。
  - **B. 手動**：下載 `site.json`，替換 `data/site.json` 後 commit。
- 後台本身是公開的靜態頁，但沒有 token 就無法改動線上內容。

## 內容格式

- 作品說明文字：空一行＝分段；以 `# ` 開頭的段落＝小標題；網址會自動變成連結。
- `hidden: true` 的作品不會出現在網站（目前 *Fall*、*Let the drone fly* 設為隱藏，與 Wix 一致）。
- 作品順序＝`works` 陣列順序（後台可上下移）。
- 沒有封面圖時依序使用：第一張圖 → 影片縮圖 → 文字。

## 圖片（重要）

目前圖片仍連到 `static.wixstatic.com`。**Wix 方案到期前**請在本機執行：

```bash
bash liutingchun/scripts/download-images.sh
```

會把所有 Wix 圖下載到 `images/wix/`，並把 `site.json` 改成本地路徑，之後 commit 即可。

## 本機預覽

```bash
cd liutingchun && python3 -m http.server 8000
# http://localhost:8000
```
