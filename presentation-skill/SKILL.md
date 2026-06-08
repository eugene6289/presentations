---
name: presentation-requirements
description: |
  Gate-keeper skill for presentation requests. Before any deck (HTML / .pptx /
  slides / 簡報 / 投影片 / report deck) is built, force a confirmation of the
  three core elements — 聽眾 (Audience)、目的 (Purpose)、大綱 (Outline) — so
  Claude never guesses its way into the wrong content or structure.

  **Trigger on** any request that produces a slide deliverable:
  "做一份簡報"、"做 slides"、"做 PPT"、"做 deck"、"幫我做投影片"、
  ".pptx"、"presentation"、"report deck"、"進度報告 deck" etc.

  This skill runs FIRST. After the three elements are confirmed, hand off to
  the appropriate builder (the `pptx` skill for .pptx output, or a fresh HTML
  deck build for browser-based decks).
---

# Presentation Requirements (三大要素 Gate)

A presentation that misses 聽眾、目的、大綱 will always go in circles — Claude
will guess the level, guess the takeaway, guess the structure, and the user
will have to redo it. This skill forces the conversation up-front so the deck
gets built once, correctly.

---

## 1. The three elements

Before writing a single slide, every one of these must be on the table. If
any are missing, ASK using `AskUserQuestion` — do not assume.

### 1.1 聽眾 (Audience)

- **問自己**：誰來看？他們的背景是什麼？
- **為什麼重要**：知道聽眾，才能決定要不要解釋術語、內容要多深、舉什麼例子。
- **範例**：「資料工程組組員 + 組長，熟悉 BigQuery，不需要解釋基本概念」

### 1.2 目的 (Purpose)

- **問自己**：聽眾看完後，應該知道什麼或做什麼？
- **為什麼重要**：目的不清楚，Claude 會猜，猜錯就要來回修。
- **範例**：「了解我如何使用 Claude 產 PPT」

### 1.3 大綱 (Outline)

- **問自己**：每頁大概講什麼？幾頁？
- **為什麼重要**：有大綱，Claude 不會自己發揮，結構就是你要的。
- **範例**：「開場→痛點→結論→Prompt→Chat→Code→工具化→總結，共 8 頁」

---

## 2. Workflow (strict order)

1. **Detect**: user asks for a deck / slides / .pptx / 簡報.
2. **Check**: scan the request for 聽眾 / 目的 / 大綱. Mark which are stated
   and which are missing.
3. **Ask**: if any are missing, call `AskUserQuestion` to collect them in ONE
   batch. Provide sensible default options when possible (e.g. typical
   audience profiles, common purposes) but always allow free-text via "Other".
4. **Echo back**: once collected, restate the three elements in a short block
   so the user can confirm or correct before any slides are made:
   ```
   聽眾：…
   目的：…
   大綱：…（共 N 頁）
   開工嗎？
   ```
5. **Hand off**: only after explicit confirmation, hand off to the right
   builder:
   - `.pptx` requested → invoke the `pptx` skill
   - HTML browser deck requested → build fresh (no locked template)
   - Unclear format → ask which one before handing off

---

## 3. Asking well (AskUserQuestion patterns)

Batch the missing elements into a SINGLE `AskUserQuestion` call (1–3
questions max) so the user fills them in one go. Examples:

**聽眾 options** (pick from likely profiles, plus Other):
- 同部門同事（熟悉領域術語）
- 跨部門同事（需要白話一點）
- 主管 / 高階主管（重結論、輕細節）
- 外部客戶 / 合作夥伴

**目的 options**:
- 報告進度 / 現況更新
- 說服對方做某個決定
- 教學 / 知識分享
- 提案 / pitch

**大綱**: use free-text via "Other" most of the time — outlines are too
specific to enumerate. But it's fine to offer a suggested skeleton based on
purpose and ask the user to confirm or edit.

---

## 4. HTML deck conventions

When building a browser-based HTML deck (not .pptx), follow these conventions:

- **URL deep-link**: every slide must be reachable via `?page=N` (1-indexed). On load, read the param and jump to that slide. On navigation, update with `history.replaceState`. This lets anyone share a link to a specific slide.
- **Slide numbering**: nav shows `01 / N` format; dots update on each navigation.
- **Scale**: the deck scales to viewport via `transform: scale()` so it stays 1280×720 regardless of window size.
- **Data / renderer separation**: all content lives in a `slideData` object at the top of the script; renderers are pure functions that read from it. Edits to content should only touch `slideData`.

---

## 5. What this skill does NOT do

- It does NOT build the deck itself. It only gates and hands off.
- It does NOT carry a locked visual template. Each deck is designed for its
  audience and purpose. (The previous `dark-report-deck` template has been
  removed.)
- It does NOT skip the gate just because the user sounds like they're in a
  hurry. Spending 30 seconds on three questions saves 30 minutes of rework.

---

## 6. Edge cases

- **User provides all three up-front** → echo back for confirmation, then
  hand off. No need to ask redundant questions.
- **User says "你決定就好" / "隨便"** → still ask the minimum: at least 聽眾
  and 目的. Without those two, even a default is a guess.
- **Iterating on an existing deck** → the three elements are still the
  frame. If the user wants to edit a deck, confirm the audience/purpose
  haven't shifted before making structural changes.
- **Very short request** (e.g. "做一頁總結 slide") → the gate still applies
  but can be lightweight: one quick question covering all three.
