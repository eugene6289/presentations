# 網頁提升計畫進度報告 · 編輯規則

> 這份是 `web-improvement/presentation.html` 自己的編輯筆記，記錄這份簡報在多次迭代中建立的慣例。
> 通用樣板規則看 `../presentation-skill/SKILL.md`；這裡只記**這份報告專屬**的編輯約束。

---

## 🔴 鐵則 0 · 每次調整都要更新「最後更新日期」

**任何資料異動（不管大小）都必須同步更新日期欄位**，否則簡報的時效性會誤導讀者。

要同步的三處：

```js
slideData.cover.date          // 封面右下角 — 格式 "2026 / 05 / 27"
slideData.overview.lastUpdated // 第 2 頁右上角「最後更新」— 格式 "2026/05/27"
slideData.aiSkills.todayNote   // 第 6 頁 subtitle 若含日期 — 例 "今日 (5/27) ..."
```

KPI 裡若有「今日里程碑」之類含日期的卡片，也要一起改。

> 一個編輯動作 = 一個新日期。不要假設使用者會自己改。

---

## 1. 簡報結構（7 頁）

| 頁 | 區段 | 主題 | 關鍵元件 |
|---|---|---|---|
| 1 | Cover | 封面（標題 + 日期） | `slideData.cover` |
| 2 | Overview | 4 KPI + 關鍵進展摘要 | `slideData.overview` |
| 3 | Part A · Phase 1 | 部署流程自動化進度表 | `phase1_deployment[]` |
| 4 | Part A · 運作紀錄 | Repo 優化覆蓋率（4 卡片） | `slideData.repoHealth` |
| 5 | Part A · Phase 2 | 程式架構優化（Tailwind / API） | `phase2_architecture[]` + Tailwind modal |
| 6 | Part B · AI Skills | AI Skills 矩陣 + 兩顆按鈕 | `slideData.aiSkills` + standards modal |
| 7 | Roadmap | 2026 年度時程 | `slideData.timeline` |

> 順序在 `const renderers = [...]` 陣列裡定；重排只動陣列、不要搬 HTML。

---

## 2. 編輯入口（怎麼快速找到改哪裡）

| 想改什麼 | 改哪裡 |
|---|---|
| 任何文字 / 數據 / 連結 | `<script>` 開頭的 `slideData` 物件 |
| 投影片順序 | `renderers = [...]` |
| 顏色 / 字級 / 間距 | `<style>` 開頭的 `:root` token |
| 按鈕 / 狀態樣式 | `.row-action` / `.open-modal-btn` / `.pill` |
| 新增 modal | (1) `slideData.operationEfficiency.detailsModals` 加資料 → (2) body 加 `<div class="modal-overlay" id="xxxModal">` → (3) `mount()` 加渲染 → (4) 卡片 `detailsKey: "xxx"` |

---

## 3. 視覺語言（鐵則 · 不要混用）

| 角色 | 樣式 | 例 |
|---|---|---|
| **按鈕 / 連結（可按）** | **外框**：透明底 + accent 邊框 + accent 文字。hover 底色加深 + 微微 translateY | `.row-action`、`.open-modal-btn`、`.nav button` |
| **狀態 pill（資訊）** | **填色**：無邊框 + 淺底 + accent 文字 + 圓點 | `.pill.done`、`.pill.progress` |
| **數值 / 節點（純資料）** | **純色文字**：沒有容器，只用顏色強調 | KPI `.value`、`.tl-item::before` |

**判斷規則**：

- 能點 → 有邊框
- 表狀態 → 填色 + 圓點
- 純數字 → 只有顏色

混用 = 使用者搞不清楚哪個能點。

---

## 4. KPI 卡片規範（第 2 頁）

**敘事順序固定為：過去 → 現在 → 未來**

四張卡片必須維持這個時序，讀者一眼就能看到「已完成什麼 / 正在做什麼 / 接下來要做什麼」。

### Value 格式

統一用「**X / Y**」比例格式（含空白），不要寫單一數字、百分比、或縮寫：

- ✅ `4 / 4`、`5 / 5`、`1 / 5`、`4 / 5`
- ❌ `4`、`+4`、`100%`、`4項`

> 為什麼：比例自帶完成度語意（你知道分母是什麼），單一數字無法表達進度。

### Tone 映射

| 階段 | tone | 視覺 |
|---|---|---|
| 已完成的過去 | `success` | 綠（emerald） |
| 進行中的現在 | `accent` | 藍（sky） |
| 接下來的未來 | `highlight` | 漸層（sky+emerald） |

每張投影片**最多一張** `highlight`，這顆要留給「焦點 / 接下來」。

### hint 寫法

- **不要寫專用術語**（Skill 名稱、Repo 代號之類）。用一般人能讀的詞。
  - ❌ "Frontend · Debug · CreateDoc · Code Review"
  - ✅ "其餘 Skill 陸續進入落地階段"
- 一行內最多兩個資訊，用 `·`（middle dot）分隔
- 例：`"5 大 Skill 全員通過提案"`、`"Deploy Skill 首發完成"`

---

## 5. 關鍵進展摘要（第 2 頁底）

對齊 KPI 的時序：3 條，過去 → 現在 → 未來：

1. **過去**（綠點）：第一階段已完成的事實
2. **現在**（藍點）：目前正在進行的關鍵進展
3. **未來**（藍點）：下階段要做什麼

第一條用 `:first-child` 自動上綠點，其餘是藍點，順序不要亂。

---

## 6. AI Skills 矩陣（第 6 頁）規則

### 四個 checkbox 欄位的語意

| 欄位 | 條件 | 注意 |
|---|---|---|
| 可行性 | 成員認可 Skill 並確認可在實際場景中運作 | 提案完成即可勾選 |
| 落地 | Demo 功能正常、輸出結果具備實用性與準確度 | 自用即可 |
| 文件 | 包含 README.md 並上傳 GitHub、說明易於理解 | **必須是正式文件，不是可行性提案** |
| 交叉驗收 | 至少 2 位以上成員測試並成功導入專案 | 跨人驗證 |

### `link` 欄位 ≠ `doc` checkbox

- `link` 是表格右側「Link ↗」按鈕的目標，可以指向任何相關內容（可行性提案、文件、進度頁）
- `doc` checkbox 只在文件已上 GitHub + README 完整時才打勾
- **不要因為加了 link 就把 doc 勾起來**——我們犯過這個錯

### 按鈕標籤

- 表格右側按鈕一律「**Link ↗**」（不寫「查看進度」「文件」等容易過時的詞）
- 欄位標題保持「進度頁」（即使按鈕是 Link，欄位標題語意是「導向更多進度的入口」）

---

## 7. Modal 規範

- 開關用通用 `openModal('xxxModal')` / `closeModal('xxxModal')`
- ESC 會關閉**任一**開啟中的 modal（不分哪一個）
- 點 modal 外側遮罩也會關閉
- 新增 modal 的 4 個步驟見上方 §2

目前有兩個 modal：
- `#standardsModal` — 第 6 頁「驗收標準」按鈕（資料：`slideData.aiSkills.standards`）
- `#tailwindModal` — 第 5 頁 Tailwind 卡片「詳細說明」按鈕（資料：`operationEfficiency.detailsModals.tailwind`）

---

## 8. 內容更新檢查清單

**新增進度（如「今天某個 Skill 落地了」）時，這些地方都要同步**：

- [ ] 🔴 **`slideData.cover.date` + `slideData.overview.lastUpdated`** — 兩個日期欄位（鐵則 0）
- [ ] `slideData.aiSkills.skillsList` — checkbox 與 link
- [ ] `slideData.overview.kpis` — 數值與 hint（特別是 `1 / 5` → `2 / 5`、`4 / 5` → `3 / 5`）
- [ ] `slideData.overview.highlights` — 第二、三條敘述
- [ ] `slideData.aiSkills.todayNote` — 第 6 頁 subtitle（含日期則同步）
- [ ] 對應 KPI 的日期值（如「今日里程碑」之類）

> **漏改日期或 KPI 是最常發生的事**——KPI 是 single source of truth 給「一眼看到的數字」，**矩陣與 KPI 不同步等於說謊**。日期沒更新等於告訴讀者「這份報告已過期」。

---

## 9. 已建立的決策 / 為什麼這樣做

- **KPI 從 4 → 3 → 4**：曾經拿掉「100% 第一階段」想留三張，但「可行性 5/5 通過」是重要里程碑值得自己一張卡，最後決定四張。
- **狀態 pill 拿掉邊框**：原本邊框 + 淺底跟按鈕長得一樣，看起來都像可以按的東西。改成無邊框純填色之後就分開了。
- **欄位標題不跟著按鈕改**：使用者多次調整按鈕文字（查看進度 → 文件 → Link），但「進度頁」欄位標題穩定不動，因為它的語意是「導向進度資訊的入口」，不論按鈕怎麼叫都成立。
- **Tailwind modal 而非外連**：Gamma 文件已經有完整版本，但 in-deck modal 提供「不離開簡報」的快速摘要。兩個按鈕並排：詳細說明（modal）+ 查看文件（外連）。
- **`detailsKey` 而非 `modalId`**：欄位叫 `detailsKey` 因為它指向「詳細說明的鍵」，至於對應的 modal HTML id 是 `${detailsKey}Modal` 約定生成。這樣未來新增其他卡片的 modal 只要照規則命名即可。

---

## 10. 不要做的事

- ❌ **改了內容沒改日期** — 違反鐵則 0，會誤導讀者
- ❌ 直接改 `<section class="slide">` 的 HTML 內容 — 永遠改 `slideData`
- ❌ 在 KPI value 寫文字（「下一步」「待定」之類）— 永遠用比例數字
- ❌ 把 Skill 名稱寫在 hint 裡 — 對非團隊讀者沒意義
- ❌ 用 pill 樣式寫按鈕、或用按鈕樣式寫狀態
- ❌ 加新 modal 時複製整段 `openXxxModal/closeXxxModal` 函式 — 用通用 `openModal(id)`
