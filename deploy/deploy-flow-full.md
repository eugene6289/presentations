# Deploy Skill 完整流程說明

---

## 測試機部署（Test Deploy）

### 入口：詢問部署環境
Claude 偵測當前 repo 與 branch 後，詢問要部署哪個環境。

```
要更新哪個環境？
  → 測試機（Test）
  → 正式機（Production PR）
```

---

### T-1：部署前檢查

```bash
git fetch origin
git status --porcelain
git status -uno
```

| 狀況 | 處理方式 |
|------|----------|
| 在 `development` / `master` | ❌ 中止，需切到開發分支 |
| 有未 commit 的變更 | 詢問：Commit / Stash / 中止 |
| 本地落後遠端 | ⚠️ 警告，詢問是否繼續 |

**偵測到未 commit 時，詢問處理方式：**
```
偵測到未 commit 的變更，要如何處理？
  → Commit 變更（自動產生 commit message）
  → Stash 暫存（部署完自動恢復）
  → 中止部署
```

**若選擇「Commit 變更」，自動產生 commit message 並請確認：**
```
【類型】簡短描述

建議選項：
  → 使用建議的 message
  → 自行輸入
```

執行：
```bash
git add <changed_files>
git commit -m "<COMMIT_MESSAGE>"
```

---

### T-2：推送開發分支

```bash
git push origin <CURRENT_BRANCH>
```

---

### T-3：決定版本號

```bash
git tag --sort=-creatordate | grep "-dev$" | head -10
git log -1 --oneline
```

顯示最近 10 個 dev tag，計算建議版本後詢問確認：

```
下一個版本號？（目前最新：1.6.12-dev）
  → 1.6.13-dev（建議，PATCH +1）
  → 1.6.12.1-dev（小修正 / hotfix）
  → 自行輸入
```

---

### T-4：合併到集合式 branch（development）

```bash
git checkout development
git pull origin development
git merge <CURRENT_BRANCH> --no-edit
git push origin development
```

若發生衝突 → 中止，請使用者解決後重新執行。

---

### T-5：建立並推送 Tag

```bash
git tag -a "<VERSION>" -m "Release <VERSION>"
git push origin "<VERSION>"
```

---

### T-6：觸發 GitHub Actions Workflow

```bash
gh workflow run "🧪 Deploy to Test Environment" -f tag=<VERSION>
sleep 3
gh run list --workflow="🧪 Deploy to Test Environment" --limit 1
```

---

### T-7：切回原始開發分支

```bash
git checkout <CURRENT_BRANCH>
# 若先前選擇 Stash 暫存：
git stash pop
```

---

### T-8：顯示部署摘要

```
✅ 測試機部署完成

Project：tapirus_web_backend
版本：1.6.13-dev
開發分支：207947-physical_reward
已合併到：development
Workflow：queued（已觸發）
已切回：207947-physical_reward
```

---

### T-9：詢問是否產生 Commit Log

```
需要產生 Commit Log 給主管嗎？
  → 是，產生 commit log
  → 不用
```

---

## 正式機 PR（Production PR）

> **注意：** 如果是 hotfix（從 master 直接切出），可跳過 P-3 ~ P-5，直接從 hotfix branch 對 master 開 PR。

---

### 入口：詢問部署環境

同測試機入口，選擇「正式機（Production PR）」。

---

### P-0：部署前檢查

```bash
git fetch origin
git status --porcelain
```

| 狀況 | 處理方式 |
|------|----------|
| 在 `master` / `prerelease_*` | ❌ 中止 |
| 有未 commit 的變更 | 同 T-1 處理邏輯 |

---

### P-1：詢問 Redmine 票務連結

```
請貼上此次的 Redmine 票務連結（若沒有請填「無」）
```

---

### P-2：確認開發分支

```
確認使用哪個 branch？
  → 使用當前 branch（207947-physical_reward）
  → 手動輸入其他 branch 名稱
```

---

### P-3：詢問 Release 日期與功能名稱

```
預計 Release 日期（YYYY-MM-DD）：2026-06-09
功能名稱（用於 branch 命名）：physical-reward
```

Branch 命名格式：`prerelease_2026-06-09_physical-reward`

---

### P-4：建立 prerelease branch

```bash
git checkout master
git pull origin master
git checkout -b prerelease_2026-06-09_physical-reward
```

---

### P-5：合併開發分支並推送

```bash
git merge <DEV_BRANCH> --no-edit
git push origin prerelease_2026-06-09_physical-reward
```

---

### P-6：選擇 PR Reviewer

從 GitHub collaborators 清單中勾選（多選）：

```
選擇 PR Reviewer（可多選）
  ☐ igs-tonylin
  ☑ igs-weimangchen
  ☐ igs-tsungtingchen
  ...
```

---

### P-7：產生 PR 說明

Claude 讀取 diff 後自動產生：

```markdown
## Summary
<一句話說明這次 PR 的目的>

## Changes
- <根據實際 diff 整理的變更項目>

## Redmine
<REDMINE_URL>（無則省略）

## Release
2026-06-09
```

---

### P-8：確認並建立 PR

顯示完整 PR 預覽後詢問確認：

```
確認建立 PR？
  → 確認，建立 PR
  → 取消
```

執行：
```bash
gh pr create \
  --base master \
  --head prerelease_2026-06-09_physical-reward \
  --title "prerelease_2026-06-09_physical-reward" \
  --reviewer igs-weimangchen \
  --body "..."
```

---

### P-9：顯示結果並切回開發分支

```
✅ PR 已建立

Project：tapirus_web_backend
PR Branch：prerelease_2026-06-09_physical-reward
Base：master
Reviewers：igs-weimangchen
PR URL：https://github.com/.../pull/15

⚠️ PR approve 後，需手動觸發正式機 workflow 才會部署
```

```bash
git checkout <CURRENT_BRANCH>
```

---

## Hotfix 直接 PR 到 master（快速通道）

當改動只影響 infra / config（如 workflow yml），不需要走 prerelease 流程：

```bash
# 從 master 切 hotfix branch
git checkout master
git pull origin master
git checkout -b hotfix/<description>

# commit 改動
git add <files>
git commit -m "【調整】..."

# push 並直接對 master 開 PR
git push origin hotfix/<description>
gh pr create --base master --head hotfix/<description> ...
```
