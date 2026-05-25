# Deploy Skill 簡報

## 檔案清單

| 檔案 | 說明 |
|------|------|
| `presentation.html` | 主簡報檔，用瀏覽器開啟即可播放（基於 reveal.js） |
| `ScreenShoot/test/` | 測試機部署流程截圖（step1 ～ step5） |
| `ScreenShoot/prod/` | 正式機 PR 流程截圖（step1 ～ step6） |

## 開啟方式

直接用瀏覽器開啟 `presentation.html`，左右方向鍵翻頁，`F` 鍵全螢幕。

## 簡報結構

1. 標題頁
2. 架構總覽（四層方塊圖）
3. 三項設計原則
4. Layer 1 Orchestrator — 職責邊界
5. Layer 2 Flows — test-deploy / production-pr 步驟
6. Demo：測試機部署實際畫面（互動截圖）
7. Demo：正式機 PR 實際畫面（互動截圖）
8. Layer 3 Behaviors — 5 個可複用行為
9. Config 設定層 — project-configs.md
10. 資料流（Data Flow）
11. 設計決策 Q&A
12. 總結

## 注意

此資料夾內容不上傳 GitHub（已列入 `.gitignore`）。
