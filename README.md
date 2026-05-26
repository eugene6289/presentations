# Presentations

eugene6289 的簡報集中地。整個 repo 透過 **GitHub Pages** 對外發布，根目錄的 `index.html` 是清單頁，每份簡報各自一個資料夾、用 `index.html` 當入口。

---

## 📁 資料夾結構

```
presentations/
├── README.md               ← 本檔案（給未來的 Claude / eugene 參考）
├── index.html              ← 清單頁，列出所有簡報的卡片
├── deploy/
│   ├── presentation.html   ← Deploy Skill 架構設計（舊版命名，沿用）
│   ├── PRESENTATION.md     ← 該簡報的說明文件
│   └── ScreenShoot/        ← 簡報用到的截圖
└── web-improvement/
    └── index.html          ← 網頁提升計畫進度報告（JSON-driven 範本，內容持續更新）
```

### 命名慣例（之後新增都遵守這個）

- 每份簡報 = 一個 kebab-case 資料夾，用主題命名（不要寫死日期）：例如 `web-improvement`、`q3-review`、`onboarding`、`design-system`
- 同一份「持續更新型」簡報用主題名（不帶日期），每次只動內部的 JSON 資料
- 入口檔案統一是 `index.html`（這樣 GitHub Pages 上的網址是乾淨的 `/foo/`，不必帶檔名）
- 截圖、素材放在簡報資料夾內的子目錄，例如 `screenshots/`、`assets/`
- 簡報相關說明文件放在簡報資料夾內，命名 `PRESENTATION.md`（給人看）

> `deploy/` 是舊版（用 `presentation.html`），暫時保留不動。要統一的話可改名為 `deploy/index.html` 並更新根 `index.html` 連結為 `deploy/`。

---

## 🌐 GitHub Pages 上的網址

假設 repo 名稱為 `presentations`、帳號為 `eugene6289`：

| 內容 | URL |
|------|-----|
| 清單頁 | `https://eugene6289.github.io/presentations/` |
| 網頁提升計畫進度報告 | `https://eugene6289.github.io/presentations/web-improvement/` |
| Deploy 簡報（舊版命名） | `https://eugene6289.github.io/presentations/deploy/presentation.html` |

新增簡報後，**必須在根目錄 `index.html` 加一張卡片**，否則清單頁看不到。

---

## 🎨 視覺風格基準（`web-improvement` 是樣板）

當 eugene 要求做「乾淨、專業、McKinsey/Apple 風」的簡報時，直接參考 `web-improvement/index.html`：

### 設計準則

- **配色**：深底（`#0d0d0d`）+ 高對比白灰文字 + 兩個 accent
  - 科技藍 `#38bdf8`（資訊／進行中）
  - 螢光綠 `#10b981`（完成／成功）
  - 黃 `#fbbf24`、紅 `#f43f5e` 備用（警示／危險）
- **字體**：`Inter` + `Noto Sans TC`（中文）+ `JetBrains Mono`（數字、metadata）
- **比例**：每張投影片固定 `1280×720`（16:9），用 JS 自動縮放符合視窗
- **間距**：投影片內距 `56px 72px`；卡片圓角 `12px`、邊框 `1px solid #262626`
- **元素層次**：eyebrow（小字 accent）→ title（30px / 600）→ subtitle（14px dim）→ body

### 慣用元件

- **KPI 卡**：label（小寫 mute）+ value（32px 粗體，可上色）+ hint
- **進度條**：`<div class="pbar"><span style="width:N%"></span></div>`，依完成度切 `done` / `partial` / `idle`
- **狀態 pill**：膠囊狀小標籤，`done` 綠 / `progress` 藍
- **表格**：薄分隔線、表頭全大寫 + letter-spacing
- **時間軸**：左側 1px 線 + 圓點

### 互動

- 鍵盤：`←` `→` `space` 翻頁；`Home` `End` 跳首尾
- 底部固定 nav：上/下按鈕、頁碼、可點的圓點

---

## 🧩 JSON-driven 簡報範本（重要！）

`web-improvement/index.html` 採用 **資料與渲染完全分離** 的寫法。未來 eugene 要做類似的「定期更新型」簡報，直接複製這份當骨架。

### 核心結構

```html
<script>
  // 1. 全部資料集中放這裡，未來只動 JSON
  const slideData = {
    overview: { ... },
    section1: [ ... ],
    // ...
  };

  // 2. 渲染函式（一頁一個）
  function renderSlide1() { return `<div class="slide-header">...</div>`; }
  function renderSlide2() { ... }
  // ...

  // 3. 工具函式
  const esc = (s) => ...;              // HTML escape
  const progressBar = (pct) => ...;     // 數字 → 進度條
  const checkIcon = (v) => v ? '✅' : '🔲';

  // 4. Mount + 導航（鍵盤、按鈕、圓點、自動縮放）
  const renderers = [renderSlide1, renderSlide2, ...];
  function mount() { ... }
  function goTo(i) { ... }
  function fitStage() { ... }
</script>
```

### 為什麼這樣寫？

- eugene 想要「以後只改 JSON、不碰 HTML」——所有文字、進度、勾選、負責人都從 `slideData` 讀
- 數字（如 `prepare: 100`）自動轉成進度條寬度
- 布林值（`feasibility: true`）自動轉成 ✅ / 🔲
- 每頁有獨立 `renderSlideN()`，方便個別調整版型

---

## ✅ 新增一份簡報的 SOP

1. 在根目錄建立 kebab-case 資料夾，例如 `q3-review/`
2. 在資料夾內建立 `index.html`
   - 若是儀表板／報告類：複製 `web-improvement/index.html` 改 JSON
   - 若是說明／設計類：可參考 `deploy/presentation.html`（reveal.js 風）或自由發揮
3. 素材放在同資料夾內的子目錄
4. 更新根目錄 `index.html`，加一張卡片連到新資料夾（`href="q3-review/"`）
5. commit & push → GitHub Pages 自動部署

---

## 🛠️ 給未來的 Claude 的提示

- **eugene 偏好**：黑底、極簡、不要太多裝飾、英文 eyebrow + 中文標題的層次
- **不要**：用太多 emoji、過度漸層、彩色背景、reveal.js 以外的重型框架
- **可以**：原生 JS + 內嵌 CSS（單一 HTML 檔，無打包工具，方便 GitHub Pages 直出）
- **資料來源**：eugene 提供的 JSON 結構**直接照搬欄位名**，不要自己改名（他會用同一份 JSON 多次更新）
- **驗證**：寫完用 `node --check` 跑一下抽出來的 `<script>` 內容，確保語法正確
- **檔案位置**：簡報最終都放在 `/Users/eugenechua/Projects/presentations/<folder>/index.html`
