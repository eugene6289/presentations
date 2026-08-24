#!/usr/bin/env python3
"""
AI 寫的程式，誰在把關？ — 事業處分享版 .pptx

沿用 index.html 的做法：內容（SLIDES）與版型（renderers）分離。
改內容只要動 SLIDES；改視覺只要動 CONFIG 與 renderers。

    python3 build_pptx.py
"""

from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches as In, Pt

HERE = Path(__file__).resolve().parent
OUT = HERE / "ai-code-gates-share.pptx"

# ============================================================
# CONFIG
# ============================================================
DECK = "AI 寫的程式，誰在把關？ ／ 事業處分享"

# 字型：現場用 Mac 放映就維持 PingFang TC；要在 Windows 開改成 Microsoft JhengHei
EA_FONT = "PingFang TC"
LATIN_FONT = "Helvetica Neue"
MONO_FONT = "Menlo"

PAPER = RGBColor(0xE8, 0xEB, 0xEE)
CARD = RGBColor(0xDF, 0xE4, 0xE9)
INK = RGBColor(0x0F, 0x1E, 0x26)
MUTED = RGBColor(0x5B, 0x6C, 0x77)
RULE = RGBColor(0xC3, 0xCB, 0xD2)
FAIL = RGBColor(0xC1, 0x40, 0x2B)
PASS = RGBColor(0x1B, 0x6E, 0x52)
WARN = RGBColor(0xA8, 0x6A, 0x1E)
ON_INK = RGBColor(0xDC, 0xE6, 0xE9)
ON_INK_DIM = RGBColor(0x7F, 0x94, 0x9D)
ACCENT_ON_INK = RGBColor(0x7F, 0xD3, 0xAE)

SW, SH = 13.333, 7.5
L = 0.75
CW = SW - L * 2
BODY_BOTTOM = 6.60
HAIR = 1 / 72.0  # 1pt


# ============================================================
# primitives
# ============================================================
def set_font(run, size=13, bold=False, color=INK, font=None, italic=False):
    face = font or EA_FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = face if face == MONO_FONT else LATIN_FONT
    rPr = run.font._rPr
    for tag in ("a:ea", "a:cs"):
        rPr.append(rPr.makeelement(qn(tag), {"typeface": face}))


def tb(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(In(x), In(y), In(w), In(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    return tf


def p(tf, text, size=13, bold=False, color=INK, font=None, line=1.45,
      before=0, after=0, align=PP_ALIGN.LEFT, hang=0):
    """text 可以是 str，或 [(片段, {樣式覆寫}), ...]。"""
    para = tf.paragraphs[0] if not tf.paragraphs[0].runs else tf.add_paragraph()
    para.alignment = align
    para.line_spacing = line
    if before:
        para.space_before = Pt(before)
    if after:
        para.space_after = Pt(after)
    if hang:
        pPr = para._p.get_or_add_pPr()
        pPr.set("marL", str(In(hang)))
        pPr.set("indent", str(-In(hang)))

    base = dict(size=size, bold=bold, color=color, font=font)
    segments = text if isinstance(text, list) else [(text, {})]
    for frag, over in segments:
        run = para.add_run()
        run.text = frag
        set_font(run, **{**base, **over})
    return para


def rect(slide, x, y, w, h, fill=None, line=None, line_w=1):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, In(x), In(y), In(w), In(h))
    sh.shadow.inherit = False
    if fill is not None:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    else:
        sh.fill.background()
    if line is not None:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
    else:
        sh.line.fill.background()
    return sh


def hline(slide, x, y, w, color=RULE):
    return rect(slide, x, y, w, HAIR, fill=color)


def vline(slide, x, y, h, color=RULE):
    return rect(slide, x, y, HAIR, h, fill=color)


def fit(name, max_w, max_h):
    """等比縮放到不超過 max_w × max_h，回傳實際寬高。"""
    iw, ih = Image.open(HERE / name).size
    w, h = max_w, max_w * ih / iw
    if h > max_h:
        w, h = max_h * iw / ih, max_h
    return w, h


def picture(slide, name, x, y, w, h):
    pic = slide.shapes.add_picture(str(HERE / name), In(x), In(y), In(w), In(h))
    pic.line.color.rgb = RULE
    pic.line.width = Pt(1)
    return pic


def note_band(slide, x, y, w, h, text, size=12.5, color=MUTED):
    rect(slide, x, y, w, h, fill=CARD)
    rect(slide, x, y, 0.045, h, fill=INK)
    tf = tb(slide, x + 0.26, y + 0.14, w - 0.52, h - 0.28, anchor=MSO_ANCHOR.MIDDLE)
    p(tf, text, size=size, color=color, line=1.5)


def new_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, SW, SH, fill=PAPER)
    return slide


def footer(slide, label):
    hline(slide, L, 6.82, CW)
    tf = tb(slide, L, 6.95, CW * 0.6, 0.26)
    p(tf, DECK, size=9, color=MUTED, font=MONO_FONT)
    tf2 = tb(slide, L + CW * 0.4, 6.95, CW * 0.6, 0.26)
    p(tf2, label, size=9, color=MUTED, font=MONO_FONT, align=PP_ALIGN.RIGHT)


def head(slide, d):
    """畫 eyebrow / 標題 / 導言 / 分隔線，回傳內文起始 y。"""
    if d.get("sec") or d.get("kicker"):
        tf = tb(slide, L, 0.50, CW, 0.24)
        segs = []
        if d.get("sec"):
            segs.append((d["sec"] + "    ", {"font": MONO_FONT}))
        if d.get("kicker"):
            segs.append((d["kicker"], {}))
        p(tf, segs, size=10.5, color=MUTED, line=1.0)

    ts = d.get("title_size", 32)
    lines = d["title"].count("\n") + 1
    th = 0.46 * lines * (ts / 32.0) + 0.26
    tf = tb(slide, L, 0.80, CW, th)
    for i, ln in enumerate(d["title"].split("\n")):
        p(tf, ln, size=ts, bold=True, color=INK, line=1.18, before=0 if i == 0 else 2)
    y = 0.80 + th + 0.12

    if d.get("lede"):
        lh = 0.40 if len(d["lede"]) <= 52 else 0.66
        tf = tb(slide, L, y, min(CW, 10.9), lh)
        p(tf, d["lede"], size=13, color=MUTED, line=1.55)
        y += lh + 0.06

    hline(slide, L, y, CW)
    return y + 0.34


# ============================================================
# SLIDES — 全部文案都在這裡
# ============================================================
HEADLINE = "開發變容易了，維護沒有。\n四道關卡守的是維護。"

DISCIPLINE = "靠紀律"
ENFORCED = "機器強制"

SLIDES = [
    # ---------------------------------------------------------------- 1 封面
    {
        "type": "cover",
        "stamp": "事業處分享　2026.08",
        "title": "AI 寫的程式，誰在把關？",
        "sub": "從需求到推送的四道關卡",
        "meta": [
            ("場域", "商務後台（紅色後台）前後端"),
            ("關卡", "四道，從需求到推送"),
            ("現況", "189 條自動檢查，全數通過"),
        ],
    },

    # ---------------------------------------------------------------- 2 命題
    {
        "type": "statement",
        "kicker": "命題",
        "headline": "開發容易，維護難。",
        "sub": "AI 加速的是「把東西寫出來」那一段。寫完之後要被讀、被改、被接手的那一段，沒有跟著加速。",
        "keys": [
            {"k": "寫出來", "v": "變快了", "color": PASS},
            {"k": "讀、改、接手", "v": "沒有變快", "color": FAIL},
            {"k": "兩者的差額", "v": "之後分批付", "color": MUTED},
        ],
        "note": "這份分享講的是後面那一段：程式寫完之後，怎麼確保它之後每一次被改動，都還是對的。",
    },

    # ---------------------------------------------------------------- 3 現況
    {
        "type": "cards",
        "kicker": "現況",
        "title": "開發變容易了，維護沒有",
        "lede": "AI 讓「把功能做出來」的成本明顯下降。但程式寫完之後還要被讀、被改、被接手，這部分的成本沒有同步下降。",
        "cards": [
            {
                "lbl": "開發端",
                "h": "產出成本下降",
                "p": "同樣的時間可以完成更多功能。這是實際發生的變化，也是我們持續使用 AI 的原因。",
            },
            {
                "lbl": "維護端",
                "h": "成本沒有同步下降",
                "p": "程式寫完之後仍然要被閱讀、修改、接手。這些工作量隨程式碼總量增加，不會因為當初寫得快而減少。",
            },
            {
                "lbl": "兩者的落差",
                "h": "成本會延後出現",
                "p": "開發是一次性的，維護是持續的。前期省下的時間，會在後續每一次改動時分批付出。",
            },
        ],
        "note": "所以要處理的不是「這一次寫得對不對」，而是「之後每一次改動，還對不對」。四道關卡處理的是後者。",
    },

    # ---------------------------------------------------------------- 3 事故
    {
        "type": "flow",
        "sec": "§02",
        "kicker": "實例",
        "title": "一次沒有被攔截到的改動",
        "lede": "以下是實際發生過的狀況，用來說明上一頁的落差在維護階段長什麼樣子。",
        "flow": [
            {
                "lbl": "第一步",
                "h": "改了一個地方",
                "p": "我們調整了商務後台裡的一段邏輯。改動本身是對的，也做了驗證。",
            },
            {
                "lbl": "第二步",
                "h": "壞了另一個地方",
                "p": "那段邏輯被另一個功能共用著。那一邊的行為跟著變了——沒有人想到要去看它。",
            },
            {
                "lbl": "第三步",
                "h": "更新到了正式機",
                "p": "驗證的範圍沒有涵蓋到那裡，於是一路過關，跟著版本更新上了正式環境。",
            },
            {
                "lbl": "第四步",
                "h": "事後才發現",
                "p": "影響範圍有限，也已經處理完成。但發現的時間點，晚於它原本可以被發現的時間點。",
            },
        ],
        "note": "改動與驗證都照既有流程執行，仍然沒有涵蓋到受影響的部分。原因是「這次改動會波及哪些地方」需要逐一追溯，而改動數量增加之後，追溯的難度會同步上升。",
    },

    # ---------------------------------------------------------------- 4 人工的限制
    {
        "type": "two_col",
        "sec": "§03",
        "kicker": "限制",
        "title": "人工檢查做得到什麼、做不到什麼",
        "lede": "以下區分人工檢查適合處理的部分，以及不適合由人重複處理的部分。",
        "cols": [
            {
                "tag": "做得到",
                "h": "需要判斷的事，只有人做得到",
                "li": [
                    "畫面好不好懂、操作順不順",
                    "這個功能是不是真正要的那個",
                    "特殊情境合不合理、要不要放行",
                    "資料看起來對不對勁",
                ],
            },
            {
                "tag": "做不到",
                "h": "重複性的事，人做的成本太高",
                "li": [
                    "每次改動都把所有舊規則重驗一遍",
                    "記住很久以前訂下的每一個邊界值",
                    "確認「沒被列進清單的地方」也沒受影響",
                    "跟上 AI 產出的速度",
                ],
            },
        ],
        "note": "所以我們沒有取消人工檢查，而是把「重複性的部分」交給機器，人力留給需要判斷的部分。人做判斷，機器做重複。",
    },

    # ---------------------------------------------------------------- 5 四道關卡總覽
    {
        "type": "flow",
        "sec": "§04",
        "kicker": "做法",
        "title": "我們的答案：四道關卡",
        "lede": "從需求還沒動工，到程式要送出去為止，一共設了四個檢查點。",
        "flow": [
            {
                "lbl": "動手前 · /grill-me",
                "h": "先拷問需求",
                "p": "在寫任何程式之前，讓 AI 反過來質問我們：真正要解的是什麼、邊界在哪、哪裡還沒講清楚。",
                "meta": DISCIPLINE,
                "meta_color": MUTED,
            },
            {
                "lbl": "寫的時候 · TDD",
                "h": "人先寫驗收條件",
                "p": "把「應該得到什麼答案」先寫成一條檢查，AI 再照著這個答案寫實作。",
                "meta": DISCIPLINE,
                "meta_color": MUTED,
            },
            {
                "lbl": "提交前 · /pre-commit-review",
                "h": "跑一次自動審查",
                "p": "密鑰外洩、資安漏洞、debug 殘留、效能地雷，逐項掃過一遍再提交。",
                "meta": "靠紀律 → 已改成強制",
                "meta_color": PASS,
            },
            {
                "lbl": "推送前 · 自動測試",
                "h": "189 條全部重跑",
                "p": "程式要送進共用版本之前，所有檢查重跑一次。沒過，就送不出去。",
                "meta": ENFORCED,
                "meta_color": PASS,
            },
        ],
        "note": "原本四道之中只有最後一道由系統強制。最近用一個 hook 把「提交前」這道也變成強制的——後面會說明做法。剩下靠人執行的兩道，做法都寫入專案文件，成員與 AI 工具依據同一份。",
    },

    # ---------------------------------------------------------------- 6 關卡一 · 輸入
    {
        "type": "shots_wide",
        "sec": "§05",
        "kicker": "關卡一 · 動手前",
        "title": "動手前：用 /grill-me 追問需求",
        "lede": "grill-me 是開發工具裡的一個 skill：動手之前叫它一次，它會先反過來追問。以下是另一個專案的實際紀錄。",
        "shots": [
            {
                "state": "輸入　需求原句",
                "color": MUTED,
                "src": "grill-prompt.png",
                "w": 5.2,
                "cap": "這是全部的輸入。沒有規格、沒有驗收條件、沒有範圍定義——實務上很多需求就是這個樣子。",
            },
            {
                "state": "第一輪　三個問題",
                "color": FAIL,
                "src": "grill-round1.png",
                "cap": "追問集中在三件事：這件事真正的觸發點是什麼、改完之後誰維護、有沒有辦法在不上正式環境的情況下驗證。",
            },
        ],
    },

    # ---------------------------------------------------------------- 7 關卡一 · 第二輪
    {
        "type": "shots_wide",
        "sec": "§06",
        "kicker": "關卡一 · 動手前",
        "title": "追問到答得出來為止",
        "shots": [
            {
                "state": "第二輪 A　回到原問題",
                "color": FAIL,
                "src": "grill-round2a-crop.png",
                "cap": "第一輪的回答沒有回到問題本身，所以再問一次。這一輪出現關鍵發現：需要處理的檔案數，跟原本以為的差很多。",
            },
            {
                "state": "第二輪 B　驗收基準",
                "color": FAIL,
                "src": "grill-round2b-crop.png",
                "cap": "接著追問驗收基準：改完之後要拿什麼跟改之前比對。沒有基準，就沒有辦法判斷有沒有改壞。",
            },
        ],
    },

    # ---------------------------------------------------------------- 8 關卡一 · 產出
    {
        "type": "shot_split",
        "sec": "§07",
        "kicker": "關卡一 · 動手前",
        "title": "產出：一份定案的計畫",
        "lede": "兩輪之後需求才成案。輸出不是程式，是一份寫進專案的計畫文件。",
        "shot": {
            "src": "grill-end.png",
            "cap": "產出的計畫文件（節錄），共 120 行。",
        },
        "points": [
            ("原本的需求不成立", "一開始要的是「升級 264 個檔案」。追問後確認，真正需要處理的只有 1 個。"),
            ("結論出現在動手之前", "這個判斷不是寫程式寫出來的，是問出來的。寫下去之後才發現，成本是另一回事。"),
            ("完成標準先定義", "改前改後的回應必須逐 byte 相同。先有比對基準，才動第一行。"),
        ],
        "note": "這一關的產出不是程式，是一份「接下來照這個做」的共識。",
    },

    # ---------------------------------------------------------------- 7 關卡二
    {
        "type": "flow",
        "sec": "§08",
        "kicker": "關卡二 · 寫的時候",
        "title": "人先寫答案，AI 再照著寫",
        "lede": "AI 寫得對不對，不靠人逐行看，靠一條事先寫好的檢查來判定。",
        "flow": [
            {
                "lbl": "01",
                "h": "人先寫下答案",
                "p": "「輸入 Jin Gaming-Coin，應該得到 jin_gaming_coin」——把這句話寫成程式，就是一條檢查。",
                "meta": "規則由人決定",
            },
            {
                "lbl": "02",
                "h": "先確認它會失敗",
                "p": "功能還沒寫，這條檢查應該是紅的。若此時仍然通過，代表這條檢查沒有實際作用。",
                "meta": "先紅",
            },
            {
                "lbl": "03",
                "h": "AI 照著答案寫實作",
                "p": "實作完成，檢查轉綠。這條規則從此留在檢查集裡，之後每次改動都會自動重驗一次。",
                "meta": "後綠",
            },
        ],
        "note": "順序決定結果：驗收條件由人先定義，AI 的工作是讓實作通過這個條件。產出若與條件不符，在當下就會被判定不通過。",
    },

    # ---------------------------------------------------------------- 8 紅綠燈
    {
        "type": "shots",
        "sec": "§09",
        "kicker": "實際畫面",
        "title": "紅燈與綠燈",
        "lede": "這是關卡二在真實專案裡的樣子，兩張都是實際的執行畫面。",
        "shots": [
            {
                "state": "紅燈　功能還沒寫",
                "color": FAIL,
                "src": "redlight.png",
                "cap": "新寫的 7 條檢查，因為功能還不存在而失敗。先確認它真的抓得到錯，才開始動手寫。",
            },
            {
                "state": "綠燈　功能完成",
                "color": PASS,
                "src": "greenlight-summary.png",
                "cap": "實作完成後全部通過：這一輪 133 條檢查，0.54 秒跑完，程式格式檢查也一併過關。",
            },
        ],
        "note": "同一套檢查在之後每次改動時都會重新執行，涵蓋範圍不限於本次開發，這是它在維護階段的作用。",
    },

    # ---------------------------------------------------------------- 9 關卡三
    {
        "type": "flow",
        "sec": "§10",
        "kicker": "關卡三 · 提交前",
        "title": "提交前：用 /pre-commit-review 掃一遍",
        "lede": "另一個 skill：提交之前固定叫一次，把該掃的地方逐項掃過。它檢查的不是功能對不對，是有沒有留下不該留的東西。",
        "flow": [
            {
                "lbl": "最高優先",
                "h": "密鑰與敏感資料",
                "p": "API 金鑰、密碼、連線字串有沒有被寫進程式；使用者資料有沒有被印到日誌裡。",
            },
            {
                "lbl": "高",
                "h": "資安與功能破壞",
                "p": "注入風險、權限判斷寫漏、這次改動有沒有把既有行為改壞。",
            },
            {
                "lbl": "中",
                "h": "殘留與雜訊",
                "p": "debug 用的印出、臨時測試碼、不該進版控的檔案，有沒有跟著被提交。",
            },
            {
                "lbl": "中",
                "h": "效能與設定",
                "p": "資料庫查詢的寫法、環境設定、型別安全，這些容易在趕工時被略過的地方。",
            },
        ],
        "note": "但它有個先天問題：這是一個「要記得做」的動作。趕的時候最容易略過，而趕的時候最需要它。",
    },

    # ---------------------------------------------------------------- 關卡三 · 強制
    {
        "type": "flow",
        "kicker": "關卡三 · 補強",
        "title": "用一個 hook，把「要記得做」變成「不做就過不去」",
        "lede": "最近加的做法：讓開發工具在偵測到 git commit 的當下自己攔下來，不依賴人記得。",
        "flow": [
            {
                "lbl": "問題",
                "h": "紀律會被進度稀釋",
                "p": "做不做，取決於當下記不記得。越忙越容易跳過。",
                "meta": "靠紀律",
                "meta_color": MUTED,
            },
            {
                "lbl": "做法",
                "h": "在提交那一刻攔下來",
                "p": "凡是要執行 git commit，先被擋住，並指定去跑審查。",
                "meta": "20 行 shell",
                "meta_color": MUTED,
            },
            {
                "lbl": "流程",
                "h": "審完，重跑就過",
                "p": "AI 收到攔截後自己去審、回報發現；處理完重下同一個指令即放行。",
                "meta": "不用改 CI",
                "meta_color": MUTED,
            },
            {
                "lbl": "分寸",
                "h": "同一份內容只擋一次",
                "p": "以「這次連線＋這個專案＋這批內容」為單位記錄，不會變成干擾。",
                "meta": "機器強制",
                "meta_color": PASS,
            },
        ],
        "code": "攔截 git commit → deny：「這次 commit 還沒做提交前審查，請先呼叫 pre-commit-review」",
        "note": "不用改 CI、不用每個人記得。目前掛在我自己的環境，之後可直接複製成團隊共用設定。",
    },

    # ---------------------------------------------------------------- 10 關卡四
    {
        "type": "stats",
        "sec": "§11",
        "kicker": "關卡四 · 推送前",
        "title": "沒過，程式就送不出去",
        "lede": "前面三道靠紀律，這一道是機器強制的：所有檢查重跑一次，全過才放行。",
        "stats": [
            {"v": "189", "lbl": "條自動檢查", "sub": "後端 128 ／ 前端 61"},
            {"v": "20", "lbl": "個檢查檔案", "sub": "對應各自的功能模組"},
            {"v": "1", "u": "秒", "lbl": "內全部跑完", "sub": "後端 0.83 秒、前端 0.16 秒"},
            {"v": "0", "lbl": "條失敗", "sub": "目前全數通過"},
        ],
        "notes": [
            [("任何一條沒過，這份程式就", {}), ("送不進共用版本", {"color": INK, "bold": True}),
             ("，自然也不會被部署出去。", {})],
            [("涵蓋", {}), ("前端與後端兩個專案", {"color": INK, "bold": True}),
             ("。每加一個功能，這個數字就再往上長一點。", {})],
        ],
    },

    # ---------------------------------------------------------------- 畫面層 E2E
    {
        "type": "cards",
        "kicker": "缺口 · 畫面層",
        "title": "四道關卡蓋不到的地方：畫面",
        "lede": "189 條檢查驗的是邏輯與資料，不是「按鈕點下去有沒有反應」。這一塊原本只能靠人工點過一遍。",
        "cards": [
            {
                "lbl": "缺口",
                "h": "程式全綠，畫面仍可能是壞的",
                "p": "實際遇過：檢查與建置都通過，但有兩個地方沒被涵蓋到，是靠人開瀏覽器看畫面對不上才發現的。",
            },
            {
                "lbl": "做法",
                "h": "讓 AI 直接操作瀏覽器",
                "p": "Claude in Chrome 可以開真的頁面、點真的按鈕、讀 console 與網路請求。等於把人工要點的那一遍，交給它照著走。",
            },
            {
                "lbl": "現況",
                "h": "試作階段，已實際跑過幾次",
                "p": "目前是先確認它抓得到哪些問題，還沒固定成流程。下一步是挑幾條最常壞的操作路徑，變成每次都跑。",
            },
        ],
        "note": "這一關補的是「還會不會動」。畫面好不好用、順不順，仍然是判斷題，還是由人來看——分工跟前面一樣：人做判斷，機器做重複。",
    },

    # ---------------------------------------------------------------- 另一種驗證 · 方法
    {
        "type": "flow",
        "kicker": "另一種驗證",
        "title": "沒有新需求的改動，要怎麼驗？",
        "lede": "最近幫另一個專案做效能優化，26 個項目。這類改動的驗收條件是「行為完全不變」，先寫檢查那一套用不上，改用另外三段。",
        "flow": [
            {
                "lbl": "第一段",
                "h": "先量，再改",
                "p": "動手前先建立基準線，改完量同一個數字。用精確值不用估計值：JS 產物 5,758,513 → 4,827,230 byte。",
                "meta": "−16.2%",
                "meta_color": PASS,
            },
            {
                "lbl": "第二段",
                "h": "逐項列出可能波及誰",
                "p": "每一筆改動都寫成兩欄：可能波及哪些程式、實際查證結果是什麼。沒查過的不能寫「安全」。",
                "meta": "取代「應該沒問題」",
                "meta_color": MUTED,
            },
            {
                "lbl": "第三段",
                "h": "驗收清單寫成可勾選的",
                "p": "開哪一頁、看哪個面板、預期看到什麼數字，逐條列出。需要測試帳號才驗得了的，就標記為未完成。",
                "meta": "誰接手都能重跑",
                "meta_color": MUTED,
            },
        ],
        "note": "成果：導航阻塞 40ms → 26ms、banner 重複請求 18 → 4 次。但真正省下時間的不是這些數字，是下一頁。",
    },

    # ---------------------------------------------------------------- 另一種驗證 · 產出
    {
        "type": "two_col",
        "kicker": "另一種驗證",
        "title": "查證的產出，是推翻了幾件事",
        "lede": "研發部門的審查報告列了 26 項。逐項查證之後，有幾項的結論跟報告不一樣——這些都是「照著做就會出事」的項目。",
        "li_size": 13,
        "cols": [
            {
                "tag": "被推翻",
                "h": "照著做會壞掉的部分",
                "li": [
                    "「這個套件沒用到」——它是金流套件的相依，刪了會壞",
                    "「這段輪詢可以直接刪」——結論對、理由錯：刪了會顯示錯的法遵文案",
                    "「這兩支請求該並行」——後面那支要帶前面的結果，串行是必要的",
                ],
            },
            {
                "tag": "自我檢查",
                "h": "驗證方法本身也會出錯",
                "li": [
                    "用 HTTP 200 確認檔案還在不在，看起來一切正常",
                    "加一個對照組：拿一個不存在的檔名去要——回應一模一樣",
                    "代表這個方法沒有鑑別力。方法要先自證有效，結果才算數",
                ],
            },
        ],
        "note": "驗證不只是確認做對了，更多時候是問出「這件事到底該不該做」。細節整理成一份可逐項點開的網頁，等一下直接看。",
    },

    # ---------------------------------------------------------------- 11 規範
    {
        "type": "shot_split",
        "kicker": "支撐",
        "title": "四道關卡的做法，寫成專案內的文件",
        "lede": "四道關卡有三道由人執行。為了讓執行方式一致，做法統一寫成文件放在專案裡。",
        "shot": {
            "src": "readTDDrules.png",
            "cap": "後端專案的開發規範文件（節錄）。前端另有一份對應的規範。",
        },
        "points": [
            ("每一道關卡都寫成文字", "什麼時候做、怎麼做、做到什麼程度才算通過。"),
            ("新功能先寫檢查、修問題先寫重現", "順序固定下來，不用每次重新討論。"),
            ("檢查放哪裡、怎麼跑，都是固定的", "找得到程式，就找得到對應的檢查。"),
            ("成員與 AI 開發工具讀同一份", "AI 接手時依據一樣，不需要另外口頭交代。"),
        ],
        "note": "這份文件同時供成員與 AI 開發工具讀取，兩者依據相同。",
    },

    # ---------------------------------------------------------------- 12 對各位的差別
    {
        "type": "cards",
        "sec": "§13",
        "kicker": "影響",
        "title": "這對各位的實際差別",
        "cards": [
            {
                "lbl": "提需求的時候",
                "h": "我們會問得更多、更早",
                "p": "在還沒開始寫之前，我們會把不清楚的地方先問完。來回的次數不會變少，但會集中在最便宜的階段。",
            },
            {
                "lbl": "回報問題的時候",
                "h": "問題修好後會留下一條檢查",
                "p": "同一個問題如果之後又被改壞，那條檢查會立刻亮紅燈。修過的東西不容易重覆發生。",
            },
            {
                "lbl": "上線的時候",
                "h": "沒全過就送不進共用版本",
                "p": "這道關卡是自動的，不靠人記得要做。程式要被部署出去之前，一定跑過這一關。",
            },
        ],
        "note": "需要說明的是：這些關卡降低「改動波及其他功能」的機率，並讓問題盡量在上線前出現，但不保證零錯誤。畫面與操作情境目前仍以人工確認為主，正在用 Claude in Chrome 的 E2E 補上。",
    },

    # ---------------------------------------------------------------- 總結
    {
        "type": "matrix",
        "kicker": "總結",
        "title": "什麼時候，用哪一個",
        "lede": "不是每次改動都要全套走完。以下是實務上的取用方式。",
        "cols": [("工具", 0.22), ("什麼時候用", 0.26), ("怎麼執行", 0.34), ("強制程度", 0.18)],
        "rows": [
            {"t": "/grill-me", "mono": True,
             "when": "大需求、規格模糊",
             "how": "動手寫程式之前叫一次，追問到答得出來",
             "f": ("靠紀律", MUTED)},
            {"t": "TDD 先寫檢查",
             "when": "新需求、新規則、修 bug",
             "how": "人先寫下驗收條件，AI 再照著寫實作",
             "f": ("寫進規範", MUTED)},
            {"t": "/pre-commit-review", "mono": True,
             "when": "每一次提交之前",
             "how": "commit 前叫一次，或掛 hook 自動攔",
             "f": ("hook 強制", PASS)},
            {"t": "自動測試 189 條",
             "when": "每一次推送",
             "how": "推送前全部重跑，沒過就送不出去",
             "f": ("機器強制", PASS)},
            {"t": "E2E · Claude in Chrome",
             "when": "畫面與操作流程",
             "how": "前端改動後，開真的瀏覽器走一遍",
             "f": ("試作中", WARN)},
            {"t": "前後對照 ＋ 影響清單",
             "when": "效能、重構、刪碼",
             "how": "先量基準線，再逐項查證波及範圍",
             "f": ("靠紀律", MUTED)},
        ],
        "note": "一句話的原則：需求越大越模糊，越值得先問；會被重複驗證的規則，交給檢查；每次都該做的事，掛上 hook 讓它自己發生。",
    },

    # ---------------------------------------------------------------- 13 結語
    {
        "type": "closing",
        "title": "一句話收尾",
        "headline": HEADLINE.replace("\n", ""),
        "summary": [
            ("關卡", "四道，從需求到推送"),
            ("強制", "提交前 hook 擋、推送前全跑"),
            ("依據", "規範寫在專案，人與 AI 同一份"),
        ],
        "qa": "Q & A",
    },

]


# ============================================================
# renderers
# ============================================================
def r_cover(slide, d):
    rect(slide, L, 1.64, 0.11, 0.11, fill=FAIL)
    rect(slide, L + 0.17, 1.64, 0.11, 0.11, fill=PASS)
    tf = tb(slide, L + 0.42, 1.58, 6.0, 0.26)
    p(tf, d["stamp"], size=11, color=MUTED, font=MONO_FONT, line=1.2)

    tf = tb(slide, L, 2.00, CW, 1.05)
    p(tf, d["title"], size=52, bold=True, color=INK, line=1.1)

    tf = tb(slide, L, 3.18, CW, 0.42)
    p(tf, d["sub"], size=19, color=MUTED, line=1.3)

    hline(slide, L, 4.20, CW * 0.86)
    cw = (CW * 0.86) / len(d["meta"])
    for i, (k, v) in enumerate(d["meta"]):
        x = L + cw * i
        if i:
            vline(slide, x - 0.20, 4.44, 0.72)
        tf = tb(slide, x, 4.46, cw - 0.42, 0.22)
        p(tf, k, size=9.5, color=MUTED, font=MONO_FONT, line=1.1)
        tf = tb(slide, x, 4.74, cw - 0.42, 0.5)
        p(tf, v, size=15, bold=True, color=INK, line=1.35)


def _fill_box(slide, x, y, w, h, c, on_ink=False, pad=0.22):
    """CARD 底色的資訊方塊：lbl / h / p / meta。"""
    bg = INK if on_ink else CARD
    rect(slide, x, y, w, h, fill=bg)
    body_c = ON_INK_DIM if on_ink else MUTED
    title_c = ON_INK if on_ink else INK
    lbl_c = ACCENT_ON_INK if on_ink else MUTED

    tf = tb(slide, x + pad, y + pad, w - pad * 2, h - pad * 2)
    p(tf, c["lbl"], size=10, color=lbl_c, font=MONO_FONT, line=1.1)
    p(tf, c["h"], size=15.5, bold=True, color=title_c, line=1.3, before=6)
    p(tf, c["p"], size=12, color=body_c, line=1.6, before=7)
    if c.get("meta"):
        p(tf, c["meta"], size=10.5, bold=bool(c.get("meta_color")),
          color=c.get("meta_color", lbl_c), font=MONO_FONT, line=1.2, before=9)


def r_flow(slide, d):
    top = head(slide, d)
    bottom = BODY_BOTTOM

    if d.get("note"):
        nh = 0.92 if len(d["note"]) > 58 else 0.62
        note_band(slide, L, bottom - nh, CW, nh, d["note"],
                  color=d.get("note_color", MUTED))
        bottom -= nh + 0.26

    if d.get("code"):
        ch = 0.62
        cy = bottom - ch
        rect(slide, L, cy, CW, ch, fill=INK)
        tf = tb(slide, L + 0.26, cy, CW - 0.52, ch, anchor=MSO_ANCHOR.MIDDLE)
        p(tf, d["code"], size=11, color=ACCENT_ON_INK, font=MONO_FONT, line=1.4)
        bottom -= ch + 0.22

    if d.get("figs"):
        fh = 1.20
        fy = bottom - fh
        hline(slide, L, fy, CW)
        n = len(d["figs"])
        cw = CW / n
        for i, f in enumerate(d["figs"]):
            x = L + cw * i
            if i:
                vline(slide, x - 0.16, fy + 0.20, fh - 0.28)
            tf = tb(slide, x, fy + 0.22, cw - 0.34, 0.48)
            segs = [(f["v"], {})]
            if f.get("u"):
                segs.append((f["u"], {"size": 15}))
            p(tf, segs, size=34, bold=True, color=PASS, font=MONO_FONT, line=1.0)
            tf = tb(slide, x, fy + 0.74, cw - 0.34, 0.24)
            p(tf, f["k"], size=12.5, bold=True, color=INK, line=1.2)
            tf = tb(slide, x, fy + 0.99, cw - 0.34, 0.24)
            p(tf, f["s"], size=10.5, color=MUTED, line=1.2)
        bottom = fy - 0.26

    boxes = d["flow"]
    n = len(boxes)
    gap = 0.32
    w = (CW - gap * (n - 1)) / n
    h = bottom - top
    for i, c in enumerate(boxes):
        x = L + (w + gap) * i
        _fill_box(slide, x, top, w, h, c)
        if i:
            tf = tb(slide, x - gap, top + h / 2 - 0.16, gap, 0.32, anchor=MSO_ANCHOR.MIDDLE)
            p(tf, "→", size=14, color=MUTED, font=MONO_FONT, align=PP_ALIGN.CENTER, line=1.0)


def r_statement(slide, d):
    """開場命題頁：一句話撐滿版面，下面只留三組極短的對照。"""
    tf = tb(slide, L, 0.50, CW, 0.24)
    p(tf, [(d["sec"] + "    ", {"font": MONO_FONT}), (d["kicker"], {})],
      size=10.5, color=MUTED, line=1.0)

    by, bh = 1.02, 2.46
    rect(slide, L, by, CW, bh, fill=INK)
    tf = tb(slide, L + 0.70, by, CW - 1.40, bh, anchor=MSO_ANCHOR.MIDDLE)
    p(tf, d["headline"], size=54, bold=True, color=ON_INK, line=1.18)
    p(tf, d["sub"], size=14.5, color=ON_INK_DIM, line=1.65, before=18)

    nh = 0.62
    note_band(slide, L, BODY_BOTTOM - nh, CW, nh, d["note"])

    top = by + bh + 0.52
    rh = 0.92
    top += max(0.0, (BODY_BOTTOM - nh - 0.30 - top - rh) / 2)
    cw = CW / len(d["keys"])
    for i, c in enumerate(d["keys"]):
        x = L + cw * i
        if i:
            vline(slide, x - 0.22, top, rh)
        tf = tb(slide, x, top, cw - 0.44, 0.26)
        p(tf, c["k"], size=11, color=MUTED, font=MONO_FONT, line=1.1)
        tf = tb(slide, x, top + 0.36, cw - 0.44, 0.5)
        p(tf, c["v"], size=25, bold=True, color=c["color"], line=1.2)


def r_matrix(slide, d):
    """總結對照表：一列一個工具，最後一欄標強制程度。"""
    top = head(slide, d)
    bottom = BODY_BOTTOM
    if d.get("note"):
        nh = 0.92 if len(d["note"]) > 58 else 0.62
        note_band(slide, L, bottom - nh, CW, nh, d["note"])
        bottom -= nh + 0.26

    ws = [CW * f for _, f in d["cols"]]
    xs, x = [], L
    for w in ws:
        xs.append(x)
        x += w

    hh = 0.30
    for (title, _), x0, w in zip(d["cols"], xs, ws):
        tf = tb(slide, x0, top, w - 0.26, hh)
        p(tf, title, size=10, color=MUTED, font=MONO_FONT, line=1.1)
    hline(slide, L, top + hh, CW, color=INK)

    y = top + hh
    rh = (bottom - y) / len(d["rows"])
    for i, r in enumerate(d["rows"]):
        if i:
            hline(slide, L, y, CW)
        cy = y + 0.14
        ch = rh - 0.20
        tf = tb(slide, xs[0], cy, ws[0] - 0.26, ch, anchor=MSO_ANCHOR.MIDDLE)
        p(tf, r["t"], size=13, bold=True, color=INK, line=1.3,
          font=MONO_FONT if r.get("mono") else None)
        for key, x0, w in (("when", xs[1], ws[1]), ("how", xs[2], ws[2])):
            tf = tb(slide, x0, cy, w - 0.26, ch, anchor=MSO_ANCHOR.MIDDLE)
            p(tf, r[key], size=12, color=MUTED, line=1.45)
        txt, col = r["f"]
        tf = tb(slide, xs[3], cy, ws[3] - 0.26, ch, anchor=MSO_ANCHOR.MIDDLE)
        p(tf, txt, size=12, bold=True, color=col, font=MONO_FONT, line=1.3)
        y += rh


def r_cards(slide, d):
    top = head(slide, d)
    bottom = BODY_BOTTOM
    if d.get("note"):
        nh = 0.92 if len(d["note"]) > 58 else 0.62
        note_band(slide, L, bottom - nh, CW, nh, d["note"],
                  color=d.get("note_color", MUTED))
        bottom -= nh + 0.30

    n = len(d["cards"])
    cw = CW / n
    h = bottom - top
    for i, c in enumerate(d["cards"]):
        x = L + cw * i
        if i:
            vline(slide, x - 0.18, top, h)
        tf = tb(slide, x, top + 0.10, cw - 0.42, h - 0.10)
        p(tf, c["lbl"], size=10.5, color=MUTED, font=MONO_FONT, line=1.1)
        p(tf, c["h"], size=18, bold=True, color=INK, line=1.32, before=10)
        p(tf, c["p"], size=13, color=MUTED, line=1.75, before=12)


def r_two_col(slide, d):
    top = head(slide, d)
    bottom = BODY_BOTTOM

    if d.get("note"):
        nh = 0.92 if len(d["note"]) > 58 else 0.62
        note_band(slide, L, bottom - nh, CW, nh, d["note"],
                  color=d.get("note_color", MUTED))
        bottom -= nh + 0.28


    h = bottom - top
    cw = CW / 2
    for i, col in enumerate(d["cols"]):
        x = L + cw * i
        if i:
            vline(slide, x - 0.22, top, h)
        rect(slide, x, top, 1.02 if len(col["tag"]) <= 4 else 1.32, 0.28, fill=INK)
        tf = tb(slide, x, top + 0.045, (1.02 if len(col["tag"]) <= 4 else 1.32), 0.22,
                anchor=MSO_ANCHOR.MIDDLE)
        p(tf, col["tag"], size=10, bold=True, color=PAPER, font=MONO_FONT,
          align=PP_ALIGN.CENTER, line=1.0)
        tf = tb(slide, x, top + 0.44, cw - 0.48, 0.4)
        p(tf, col["h"], size=17, bold=True, color=INK, line=1.3)
        tf = tb(slide, x, top + 0.98, cw - 0.48, h - 1.0)
        for j, li in enumerate(col["li"]):
            p(tf, [("—　", {"color": MUTED}), (li, {})],
              size=d.get("li_size", 13.5), color=INK, line=1.6,
              before=0 if j == 0 else 9, hang=0.30)


def r_stats(slide, d):
    top = head(slide, d)

    # 註解列貼齊內文底部，數字區塊在剩下的空間置中，避免整頁下半空掉
    ny = BODY_BOTTOM - 1.08
    block_h = 2.18
    sy = top + max(0.0, (ny - 0.30 - top - block_h) / 2)

    n = len(d["stats"])
    cw = CW / n
    for i, s in enumerate(d["stats"]):
        x = L + cw * i
        if i:
            vline(slide, x - 0.22, sy, block_h)
        tf = tb(slide, x, sy, cw - 0.44, 1.00)
        segs = [(s["v"], {})]
        if s.get("u"):
            segs.append((s["u"], {"size": 26}))
        p(tf, segs, size=64, bold=True, color=PASS, font=MONO_FONT, line=1.0)
        tf = tb(slide, x, sy + 1.22, cw - 0.44, 0.3)
        p(tf, s["lbl"], size=16, bold=True, color=INK, line=1.25)
        tf = tb(slide, x, sy + 1.60, cw - 0.44, 0.5)
        p(tf, s["sub"], size=12.5, color=MUTED, line=1.45)

    hline(slide, L, ny, CW)
    cw2 = CW / len(d["notes"])
    for i, note in enumerate(d["notes"]):
        x = L + cw2 * i
        if i:
            vline(slide, x - 0.22, ny + 0.24, 0.72)
        tf = tb(slide, x, ny + 0.26, cw2 - 0.44, 0.8)
        p(tf, note, size=13, color=MUTED, line=1.7)


def r_shots(slide, d):
    """兩張終端機截圖上下排列：左邊放圖、右邊放說明，圖才夠大看得清楚。"""
    top = head(slide, d)
    bottom = BODY_BOTTOM
    nh = 0.92 if len(d["note"]) > 58 else 0.62
    note_band(slide, L, bottom - nh, CW, nh, d["note"])
    bottom -= nh + 0.26

    lbl_h, row_gap, cap_gap = 0.30, 0.34, 0.42
    img_w = CW * 0.60
    heights = [fit(s["src"], img_w, 99)[1] for s in d["shots"]]
    need = sum(heights) + lbl_h * len(d["shots"]) + row_gap * (len(d["shots"]) - 1)
    avail = bottom - top
    if need > avail:  # 等比縮到塞得下
        img_w *= (avail - lbl_h * len(d["shots"]) - row_gap * (len(d["shots"]) - 1)) / sum(heights)

    y = top
    for s in d["shots"]:
        rect(slide, L, y + 0.05, 0.11, 0.11, fill=s["color"])
        tf = tb(slide, L + 0.22, y, 5.0, 0.24)
        p(tf, s["state"], size=10.5, bold=True, color=s["color"], font=MONO_FONT, line=1.1)
        iw, ih = fit(s["src"], img_w, 99)
        picture(slide, s["src"], L, y + lbl_h, iw, ih)
        tf = tb(slide, L + iw + cap_gap, y + lbl_h, CW - iw - cap_gap, ih,
                anchor=MSO_ANCHOR.MIDDLE)
        p(tf, s["cap"], size=12.5, color=MUTED, line=1.7)
        y += lbl_h + ih + row_gap


def r_shots_wide(slide, d):
    """密集的終端機截圖：用整個內容寬度呈現，標題在上、說明在下。"""
    top = head(slide, d)
    bottom = BODY_BOTTOM
    if d.get("note"):
        nh = 0.92 if len(d["note"]) > 58 else 0.62
        note_band(slide, L, bottom - nh, CW, nh, d["note"])
        bottom -= nh + 0.24

    lbl_h, cap_h, gap = 0.28, 0.32, 0.26
    n = len(d["shots"])
    widths = [s.get("w", CW) for s in d["shots"]]
    heights = [fit(s["src"], w, 99)[1] for s, w in zip(d["shots"], widths)]
    slack = (bottom - top) - (lbl_h + cap_h) * n - gap * (n - 1)
    if sum(heights) > slack:  # 等比縮到塞得下
        widths = [w * slack / sum(heights) for w in widths]

    y = top
    for s, w in zip(d["shots"], widths):
        rect(slide, L, y + 0.05, 0.11, 0.11, fill=s["color"])
        tf = tb(slide, L + 0.22, y, CW - 0.22, 0.24)
        p(tf, s["state"], size=10.5, bold=True, color=s["color"], font=MONO_FONT, line=1.1)
        iw, ih = fit(s["src"], w, 99)
        picture(slide, s["src"], L, y + lbl_h, iw, ih)
        tf = tb(slide, L, y + lbl_h + ih + 0.10, CW, cap_h)
        p(tf, s["cap"], size=12, color=MUTED, line=1.5)
        y += lbl_h + ih + cap_h + gap


def r_shot_split(slide, d):
    top = head(slide, d)
    bottom = BODY_BOTTOM
    nh = 0.62
    note_band(slide, L, bottom - nh, CW, nh, d["note"])
    bottom -= nh + 0.26

    gap = 0.5
    lw = CW * 0.50
    rw = CW - lw - gap
    avail = bottom - top - 0.55
    iw, ih = fit(d["shot"]["src"], lw, avail)
    picture(slide, d["shot"]["src"], L, top, iw, ih)
    tf = tb(slide, L, top + ih + 0.16, lw, 0.5)
    p(tf, d["shot"]["cap"], size=11, color=MUTED, line=1.5)

    x = L + lw + gap
    tf = tb(slide, x, top, rw, bottom - top)
    for j, (t, dd) in enumerate(d["points"]):
        p(tf, [("—　", {"color": MUTED}), (t, {})], size=14, bold=True, color=INK,
          line=1.4, before=0 if j == 0 else 13, hang=0.32)
        p(tf, dd, size=12, color=MUTED, line=1.55, before=3, hang=0.32)


def r_closing(slide, d):
    top = head(slide, d)

    bh = 1.95
    rect(slide, L, top, CW, bh, fill=INK)
    tf = tb(slide, L + 0.60, top, CW - 1.20, bh, anchor=MSO_ANCHOR.MIDDLE)
    p(tf, d["headline"], size=32, bold=True, color=ON_INK, line=1.35)

    qa_h = 0.72
    y = BODY_BOTTOM - qa_h - 0.52 - 0.80

    cw = CW / len(d["summary"])
    for i, (k, v) in enumerate(d["summary"]):
        x = L + cw * i
        if i:
            vline(slide, x - 0.22, y, 0.80)
        tf = tb(slide, x, y, cw - 0.44, 0.22)
        p(tf, k, size=10, color=MUTED, font=MONO_FONT, line=1.1)
        tf = tb(slide, x, y + 0.32, cw - 0.44, 0.5)
        p(tf, v, size=15.5, bold=True, color=INK, line=1.35)

    tf = tb(slide, L, BODY_BOTTOM - qa_h, CW, qa_h)
    p(tf, d["qa"], size=38, bold=True, color=MUTED, font=MONO_FONT,
      align=PP_ALIGN.RIGHT, line=1.0)


RENDERERS = {
    "cover": r_cover,
    "statement": r_statement,
    "matrix": r_matrix,
    "flow": r_flow,
    "cards": r_cards,
    "two_col": r_two_col,
    "stats": r_stats,
    "shots": r_shots,
    "shots_wide": r_shots_wide,
    "shot_split": r_shot_split,
    "closing": r_closing,
}


# ============================================================
# build
# ============================================================
def main():
    prs = Presentation()
    prs.slide_width, prs.slide_height = In(SW), In(SH)

    total = len(SLIDES) - 1  # 封面不編號

    # 段落編號自動指派：有 kicker 的頁就是一個段落，插頁不用手動重編
    k = 0
    for d in SLIDES:
        if d.get("kicker"):
            k += 1
            d["sec"] = f"§{k:02d}"

    n = 0
    for d in SLIDES:
        slide = new_slide(prs)
        RENDERERS[d["type"]](slide, d)
        if d["type"] == "cover":
            continue
        n += 1
        footer(slide, f"{n:02d} / {total:02d}")

    prs.save(OUT)
    print(f"✓ {OUT.name}　共 {len(prs.slides)} 頁（封面 ＋ {total} 頁正文）")


if __name__ == "__main__":
    main()
