"""
夏の甲子園2026 甲子園ゲーム
第108回全国高等学校野球選手権大会 スコア管理サイト
"""

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="夏の甲子園2026 甲子園ゲーム",
    page_icon="⚾",
    layout="wide",
)

# =============================================
# データ定義
# =============================================

TEAMS = {
    1: "白樺学園",
    2: "札幌日大",
    3: "青森山田",
    4: "横手",
    5: "花巻東",
    6: "鶴岡東",
    7: "仙台育英",
    8: "東日大昌平",
    9: "霞ケ浦",
    10: "佐野日大",
    11: "健大高崎",
    12: "花咲徳栄",
    13: "拓大紅陵",
    14: "関東第一",
    15: "八王子実践",
    16: "横浜",
    17: "日本文理",
    18: "松商学園",
    19: "東海大甲府",
    20: "聖隷クリストファー",
    21: "享栄",
    22: "中京",
    23: "三重",
    24: "高岡商",
    25: "遊学館",
    26: "敦賀気比",
    27: "八幡商",
    28: "立命館宇治",
    29: "履正社",
    30: "社",
    31: "天理",
    32: "智辯和歌山",
    33: "岡山学芸館",
    34: "福山",
    35: "鳥取城北",
    36: "立正大淞南",
    37: "高川学園",
    38: "英明",
    39: "鳴門渦潮",
    40: "新田",
    41: "明徳義塾",
    42: "東筑",
    43: "佐賀商",
    44: "長崎日大",
    45: "有明",
    46: "大分商",
    47: "日南学園",
    48: "神村学園",
    49: "沖縄尚学",
}

PREFS = {
    1: "北北海道",
    2: "南北海道",
    3: "青森",
    4: "秋田",
    5: "岩手",
    6: "山形",
    7: "宮城",
    8: "福島",
    9: "茨城",
    10: "栃木",
    11: "群馬",
    12: "埼玉",
    13: "千葉",
    14: "東東京",
    15: "西東京",
    16: "神奈川",
    17: "新潟",
    18: "長野",
    19: "山梨",
    20: "静岡",
    21: "愛知",
    22: "岐阜",
    23: "三重",
    24: "富山",
    25: "石川",
    26: "福井",
    27: "滋賀",
    28: "京都",
    29: "大阪",
    30: "兵庫",
    31: "奈良",
    32: "和歌山",
    33: "岡山",
    34: "広島",
    35: "鳥取",
    36: "島根",
    37: "山口",
    38: "香川",
    39: "徳島",
    40: "愛媛",
    41: "高知",
    42: "福岡",
    43: "佐賀",
    44: "長崎",
    45: "熊本",
    46: "大分",
    47: "宮崎",
    48: "鹿児島",
    49: "沖縄",
}

SCORES = {
    "バウンサー": [28,47,24,49,27,29, 4,48,36,33, 8,10,11,32,40, 1, 9,15,30,20, 2,34, 6,26,44,21,43,17,14,37, 7,22,35,42,38,46,16,23,39,12,31,41,45,18,19,25,13, 3, 5],
    "タメオ": [36,26,11,44, 7,28, 1,47,37,12,10,13,16, 8,38, 2,17,43,19, 5,14,22,31,42,39,24,49,32, 9,21, 6,15,29,41,35,48,18,25,46,23,20,33,45,30,40,27,34, 3, 4],
    "パワーズ": [47,48, 7,46, 1,33, 5,31,32,24,12,18,23, 3,45, 2,16,40,30, 8,19,17,25,39,43, 9,26,27,13,28,10,11,29,34,35,36,20,14,41,22,15,21,42,38,49,37,44, 6, 4],
    "シーラ": [26,46,20,47,11,30, 5,42,31,25, 3, 4,15,12,16, 1,37,17,18, 6,14,32,27,43,24,23,28,21,13,33, 8, 7,38,29,44,48, 2,22,45,39,19,34,36,40,49,41,35,10, 9],
    "甘味部": [33,32,20,49,11,39, 9,34,26,27,15, 7,24, 2,36, 4,40,45,29,14, 1,13,28,44,48,23,38,18,10,22, 6, 8,37,31,30,46,19,12,41,17,16,25,43,35,47,21,42, 3, 5],
    "まなりくと": [33,34,17,47,11,45,12,41,30,26,13, 1,35,10, 8, 5,28,42,19, 2,14, 4,29,44,36,23,46,16, 7,20,15, 3,39,38,22,43,24,18,37,27,21,25,48,32,49,31,40, 9, 6],
    "邪神ちゃん": [44,39,29,49, 4,37, 7,28,32,36,24,13,31, 5,43, 2,23,48,33, 1,11,30,12,42,10,22,41,35, 8,16,27,14,38,47,46,26,25,15,34, 9,21,18,45,17,40,20,19, 3, 6],
    "マカＡＩ": [ 9,33,42,34,23,20, 3,13,12,36,38,14,43, 4,49, 5,46,47,31, 1,28,11,15,41,48, 7,39, 8,21,30,19,32,44,25,29,37,17,24,18,26,10,35,22,45,16,27,40, 6, 2],
}

# 各試合の定義。("T", チームID) = 出場校確定 / ("W", 試合番号) = その試合の勝者
MATCH_DEFS = {
    # ---- 1回戦（試合1〜17）----
    1: (("T", 2), ("T", 7)),    # 札幌日大 vs 仙台育英
    2: (("T", 42), ("T", 48)),  # 東筑 vs 神村学園
    3: (("T", 20), ("T", 10)),  # 聖隷クリストファー vs 佐野日大
    4: (("T", 19), ("T", 6)),   # 東海大甲府 vs 鶴岡東
    5: (("T", 27), ("T", 11)),  # 八幡商 vs 健大高崎
    6: (("T", 28), ("T", 45)),  # 立命館宇治 vs 有明
    7: (("T", 36), ("T", 44)),  # 立正大淞南 vs 長崎日大
    8: (("T", 25), ("T", 3)),   # 遊学館 vs 青森山田
    9: (("T", 1), ("T", 8)),    # 白樺学園 vs 東日大昌平
    10: (("T", 17), ("T", 46)), # 日本文理 vs 大分商
    11: (("T", 38), ("T", 14)), # 英明 vs 関東第一
    12: (("T", 40), ("T", 5)),  # 新田 vs 花巻東
    13: (("T", 33), ("T", 35)), # 岡山学芸館 vs 鳥取城北
    14: (("T", 39), ("T", 15)), # 鳴門渦潮 vs 八王子実践
    15: (("T", 22), ("T", 9)),  # 中京 vs 霞ケ浦
    16: (("T", 41), ("T", 47)), # 明徳義塾 vs 日南学園
    17: (("T", 16), ("T", 49)), # 横浜 vs 沖縄尚学
    # ---- 2回戦（試合18〜33）----
    18: (("T", 24), ("T", 37)), # 高岡商 vs 高川学園
    19: (("T", 31), ("T", 34)), # 天理 vs 福山
    20: (("T", 4), ("T", 26)),  # 横手 vs 敦賀気比
    21: (("T", 32), ("T", 30)), # 智辯和歌山 vs 社
    22: (("T", 29), ("T", 21)), # 履正社 vs 享栄
    23: (("T", 18), ("T", 23)), # 松商学園 vs 三重
    24: (("T", 13), ("T", 43)), # 拓大紅陵 vs 佐賀商
    25: (("T", 12), ("W", 1)),  # 花咲徳栄 vs 試合1勝者
    26: (("W", 2), ("W", 3)),
    27: (("W", 4), ("W", 5)),
    28: (("W", 6), ("W", 7)),
    29: (("W", 8), ("W", 9)),
    30: (("W", 10), ("W", 11)),
    31: (("W", 12), ("W", 13)),
    32: (("W", 14), ("W", 15)),
    33: (("W", 16), ("W", 17)),
    # ---- 3回戦（試合34〜41）----
    34: (("W", 18), ("W", 19)),
    35: (("W", 20), ("W", 21)),
    36: (("W", 22), ("W", 23)),
    37: (("W", 24), ("W", 25)),
    38: (("W", 26), ("W", 27)),
    39: (("W", 28), ("W", 29)),
    40: (("W", 30), ("W", 31)),
    41: (("W", 32), ("W", 33)),
    # ---- 準々決勝（試合42〜45）----
    # 3回戦以降は抽選で組み合わせが決まるため、当初の「隣接試合勝者同士」という
    # 仮定は誤り（2026-08-18判明）。実際の抽選結果に合わせて修正:
    # 第1試合 天理vs三重、第2試合 仙台育英vs智辯和歌山、第3試合 花巻東vs横浜、第4試合 健大高崎vs有明
    42: (("W", 34), ("W", 36)),  # 天理 vs 三重
    43: (("W", 35), ("W", 37)),  # 智辯和歌山 vs 仙台育英
    44: (("W", 38), ("W", 39)),  # 健大高崎 vs 有明
    45: (("W", 40), ("W", 41)),  # 花巻東 vs 横浜
    # ---- 準決勝（試合46〜47）----
    # 準々決勝と同じく抽選のため要確認。実際の抽選結果に合わせて修正（2026-08-18）:
    # 横浜vs智辯和歌山、健大高崎vs天理
    46: (("W", 45), ("W", 43)),  # 横浜 vs 智辯和歌山
    47: (("W", 44), ("W", 42)),  # 健大高崎 vs 天理
    # ---- 決勝（試合48）----
    48: (("W", 46), ("W", 47)),
}

ROUND_NAMES = {
    **{i: "1回戦" for i in range(1, 18)},
    **{i: "2回戦" for i in range(18, 34)},
    **{i: "3回戦" for i in range(34, 42)},
    **{i: "準々決勝" for i in range(42, 46)},
    **{i: "準決勝" for i in range(46, 48)},
    48: "決勝",
}

MATCH_SCHEDULE = {
    1: "第1日① 8/5",
    2: "第2日① 8/6", 3: "第2日② 8/6",
    4: "第3日① 8/7", 5: "第3日② 8/7", 6: "第3日③ 8/7", 7: "第3日④ 8/7",
    8: "第4日① 8/8", 9: "第4日② 8/8", 10: "第4日③ 8/8", 11: "第4日④ 8/8",
    12: "第5日① 8/9", 13: "第5日② 8/9", 14: "第5日③ 8/9", 15: "第5日④ 8/9",
    16: "第6日① 8/10", 17: "第6日② 8/10", 18: "第6日③ 8/10", 19: "第6日④ 8/10",
    20: "第7日① 8/11", 21: "第7日② 8/11", 22: "第7日③ 8/11", 23: "第7日④ 8/11",
    24: "第8日① 8/12", 25: "第8日② 8/12", 26: "第8日③ 8/12", 27: "第8日④ 8/12",
    28: "第9日① 8/13", 29: "第9日② 8/13", 30: "第9日③ 8/13",
    31: "第10日① 8/14", 32: "第10日② 8/14", 33: "第10日③ 8/14",
    34: "第11日① 8/15", 35: "第11日② 8/15", 36: "第11日③ 8/15", 37: "第11日④ 8/15",
    38: "第12日① 8/16", 39: "第12日② 8/16", 40: "第12日③ 8/16", 41: "第12日④ 8/16",
    42: "第13日① 8/18", 43: "第13日② 8/18", 44: "第13日③ 8/18", 45: "第13日④ 8/18",
    46: "第14日① 8/20", 47: "第14日② 8/20",
    48: "第15日 8/22",
}

def get_prize(rank):
    if rank == 1: return 15000
    if rank == 2: return 7000
    if rank == 3: return 2000
    if rank == 4: return -2000
    if rank <= 6: return 0
    if rank == 7: return -3000
    return -1000

# =============================================
# 試合結果取得
# =============================================

JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "koshien_results.json")

def load_saved_results() -> dict:
    """koshien_results.json から手動登録結果を読み込む"""
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            saved = json.load(f)
        return {int(k): int(v) for k, v in saved.get("results", {}).items()}
    except Exception:
        return {}

def save_results(results: dict):
    """koshien_results.json へ書き込む"""
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.now().isoformat(),
                   "results": {str(k): v for k, v in sorted(results.items())}},
                  f, ensure_ascii=False, indent=2)

def _search_score(text: str, ta: int, tb: int):
    """テキスト中でチームA vs チームBのスコアを検索し勝者チームIDを返す"""
    team_a, team_b = TEAMS[ta], TEAMS[tb]
    sep = r"\s*[－\-ー―−–—]\s*"
    for i, pat in enumerate([
        rf"{re.escape(team_a)}\D{{0,6}}(\d+){sep}(\d+)\D{{0,6}}{re.escape(team_b)}",
        rf"{re.escape(team_b)}\D{{0,6}}(\d+){sep}(\d+)\D{{0,6}}{re.escape(team_a)}",
    ]):
        m = re.search(pat, text)
        if m:
            s1, s2 = int(m.group(1)), int(m.group(2))
            if s1 == s2:
                continue
            return (ta if s1 > s2 else tb) if i == 0 else (tb if s1 > s2 else ta)
    return None

def resolve_matchups(results: dict) -> dict:
    """結果を元に、出場校が確定している試合の対戦カード {mid: (ta, tb)} を返す"""
    matchups = {}
    for mid, (slot_a, slot_b) in sorted(MATCH_DEFS.items()):
        pair = []
        for kind, ref in (slot_a, slot_b):
            if kind == "T":
                pair.append(ref)
            else:
                pair.append(results.get(ref))
        if pair[0] and pair[1]:
            matchups[mid] = (pair[0], pair[1])
    return matchups

@st.cache_data(ttl=300)  # 5分キャッシュ
def fetch_results():
    # 手動登録結果を最優先で読み込む
    results = load_saved_results()

    # Wikipedia テキスト取得
    wiki_text = ""
    try:
        url = "https://ja.wikipedia.org/wiki/%E7%AC%AC108%E5%9B%9E%E5%85%A8%E5%9B%BD%E9%AB%98%E7%AD%89%E5%AD%A6%E6%A0%A1%E9%87%8E%E7%90%83%E9%81%B8%E6%89%8B%E6%A8%A9%E5%A4%A7%E4%BC%9A"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        wiki_text = BeautifulSoup(resp.text, "html.parser").get_text()
    except Exception:
        pass

    # baseball-channel テキスト取得
    bc_text = ""
    try:
        resp = requests.get("https://www.baseballchannel.jp/etc/279216/", timeout=8,
                            headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            bc_text = BeautifulSoup(resp.text, "html.parser").get_text()
    except Exception:
        pass

    # 対戦カードが確定している試合を順にスクレイピング
    # （勝者が決まると次のラウンドのカードが確定するため、確定が増えなくなるまで反復）
    for _ in range(6):
        matchups = resolve_matchups(results)
        found_new = False
        for mid, (ta, tb) in sorted(matchups.items()):
            if mid in results:
                continue
            winner = _search_score(wiki_text, ta, tb) or _search_score(bc_text, ta, tb)
            if winner:
                results[mid] = winner
                found_new = True
        if not found_new:
            break

    return results

# =============================================
# ゲームロジック
# =============================================

def build_matches(results):
    matches = {}
    for mid, (slot_a, slot_b) in sorted(MATCH_DEFS.items()):
        pair = []
        for kind, ref in (slot_a, slot_b):
            if kind == "T":
                pair.append(ref)
            else:
                pair.append(matches[ref]["winner"] if ref in matches else None)
        matches[mid] = {"teams": (pair[0], pair[1]), "winner": results.get(mid)}
    return matches

def match_multiplier(mid):
    """準々決勝・準決勝は加点2倍、決勝は3倍（2026-08-18ルール追加）"""
    if mid == 48:
        return 3
    if 42 <= mid <= 47:
        return 2
    return 1

def calc_totals(matches):
    totals = {n: 0 for n in SCORES}
    for mid in sorted(matches):
        w = matches[mid]["winner"]
        if w:
            mult = match_multiplier(mid)
            for n in SCORES:
                totals[n] += SCORES[n][w - 1] * mult
    return totals

def calc_expected(matches, totals):
    exp_add = {n: 0.0 for n in SCORES}
    for mid in sorted(matches):
        w = matches[mid]["winner"]
        ta, tb = matches[mid]["teams"]
        if w is None and ta and tb:
            mult = match_multiplier(mid)
            for n in SCORES:
                exp_add[n] += (SCORES[n][ta-1] + SCORES[n][tb-1]) / 2.0 * mult
    return {n: totals[n] + exp_add[n] for n in SCORES}

# =============================================
# UI
# =============================================

st.title("⚾ 夏の甲子園2026 甲子園ゲーム")
st.caption(f"第108回全国高等学校野球選手権大会 ｜ 8/5〜8/22 阪神甲子園球場 ｜ 更新: {datetime.now().strftime('%m/%d %H:%M')}")

# 更新ボタン
col_btn, col_info = st.columns([1, 4])
with col_btn:
    if st.button("🔄 最新結果を取得", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col_info:
    st.info("5分ごとに自動更新 | 大会期間: 8月5日（水）〜8月22日（土）")

st.divider()

# 結果取得
with st.spinner("試合結果を取得中..."):
    results = fetch_results()
    matches = build_matches(results)
    totals = calc_totals(matches)
    expected = calc_expected(matches, totals)

completed = [(mid, m) for mid, m in sorted(matches.items()) if m["winner"]]
pending_known = [(mid, m) for mid, m in sorted(matches.items())
                 if not m["winner"] and m["teams"][0] and m["teams"][1]]

# =============================================
# ランキングテーブル
# =============================================

st.subheader("🏆 現在のランキング（合計点が低い順）")

sorted_now = sorted(totals.items(), key=lambda x: x[1])
sorted_exp = sorted(expected.items(), key=lambda x: x[1])
exp_rank = {n: r+1 for r, (n, _) in enumerate(sorted_exp)}

rank_data = []
medals = ["🥇", "🥈", "🥉", "4位", "5位", "6位", "7位", "8位"]
for rank, (name, total) in enumerate(sorted_now, 1):
    exp_r = exp_rank[name]
    exp_v = expected[name]
    arrow = "↑" if exp_r < rank else ("↓" if exp_r > rank else "→")
    prize = get_prize(rank)
    prize_str = f"+{prize:,}P" if prize > 0 else (f"{prize:,}P" if prize < 0 else "±0P")
    rank_data.append({
        "順位": medals[rank-1] if rank <= 3 else f"{rank}位",
        "参加者": name,
        "現在合計": f"{total}点",
        "期待合計": f"{exp_v:.1f}点",
        "期待順位": f"{arrow}{exp_r}位",
        "賞金(現在)": prize_str,
    })

df_rank = pd.DataFrame(rank_data)
st.dataframe(df_rank, use_container_width=True, hide_index=True,
             column_config={
                 "順位": st.column_config.TextColumn(width="small"),
                 "参加者": st.column_config.TextColumn(width="small"),
                 "現在合計": st.column_config.TextColumn(width="small"),
                 "期待合計": st.column_config.TextColumn(width="small"),
                 "期待順位": st.column_config.TextColumn(width="small"),
                 "賞金(現在)": st.column_config.TextColumn(width="small"),
             })

st.caption("※ 期待合計 = 現在 + 残り試合すべてを50/50で計算した予想加算点")

# =============================================
# 各参加者の点数割り当て表
# =============================================

with st.expander("📋 各参加者のチームへの点数割り当て（クリックで開く）"):
    PARTICIPANT_NAMES = list(SCORES.keys())
    score_data = []
    for tid in range(1, 50):
        vals = [SCORES[name][tid-1] for name in PARTICIPANT_NAMES]
        avg = sum(vals) / len(vals)
        row = {"#": tid, "都道府県": PREFS[tid], "チーム": TEAMS[tid]}
        for name in PARTICIPANT_NAMES:
            row[name] = SCORES[name][tid-1]
        row["平均"] = round(avg, 1)
        score_data.append(row)
    df_scores = pd.DataFrame(score_data)

    def color_row(row):
        avg = row["平均"]
        styles = []
        for col in row.index:
            if col in PARTICIPANT_NAMES:
                diff = row[col] - avg
                if diff <= -8:
                    styles.append("background-color: #1a7a1a; color: white")   # 濃い緑
                elif diff <= -3:
                    styles.append("background-color: #90EE90; color: black")   # 薄い緑
                elif diff >= 8:
                    styles.append("background-color: #cc0000; color: white")   # 濃い赤
                elif diff >= 3:
                    styles.append("background-color: #FFB6B6; color: black")   # 薄い赤
                else:
                    styles.append("")
            else:
                styles.append("")
        return styles

    styled = df_scores.style.apply(color_row, axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # 凡例
    st.markdown(
        "　"
        "<span style='background:#1a7a1a;color:white;padding:2px 8px;border-radius:3px'>■ 平均より8以上低い</span>　"
        "<span style='background:#90EE90;color:black;padding:2px 8px;border-radius:3px'>■ 平均より3〜7低い</span>　"
        "<span style='background:#f0f0f0;color:black;padding:2px 8px;border-radius:3px'>■ ±3未満</span>　"
        "<span style='background:#FFB6B6;color:black;padding:2px 8px;border-radius:3px'>■ 平均より3〜7高い</span>　"
        "<span style='background:#cc0000;color:white;padding:2px 8px;border-radius:3px'>■ 平均より8以上高い</span>",
        unsafe_allow_html=True,
    )
    st.caption("低い = 他の参加者より高く評価（優勝候補）　高い = 他より低く評価")

st.divider()

# =============================================
# 試合結果
# =============================================

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"✅ 完了済み ({len(completed)}試合)")
    if not completed:
        st.info("大会開幕後に結果が表示されます（8/5〜）")
    else:
        for mid, m in completed:
            w = m["winner"]
            ta, tb = m["teams"]
            loser = tb if w == ta else ta
            st.write(f"**試合{mid}** {MATCH_SCHEDULE[mid]} ({ROUND_NAMES[mid]}) "
                     f"　◯ **{TEAMS[w]}** vs {TEAMS[loser]} ✕")

with col2:
    st.subheader(f"⏳ 対戦待ち ({len(pending_known)}試合)")
    if not pending_known:
        if not completed:
            st.info("1回戦17試合＋2回戦の確定カードが表示されます")
        else:
            st.success("全試合完了！")
    else:
        for mid, m in pending_known:
            ta, tb = m["teams"]
            st.write(f"**試合{mid}** {MATCH_SCHEDULE[mid]} ({ROUND_NAMES[mid]}) "
                     f"　{TEAMS[ta]} vs {TEAMS[tb]}")

st.divider()

# =============================================
# バウンサー向け期待値分析
# =============================================

st.subheader("🎯 バウンサー向け 期待値分析")
st.caption("どちらのチームが勝つと有利か（点差が大きいほど重要）")

bouncer = "バウンサー"
current_rank = next(i+1 for i,(n,_) in enumerate(sorted_now) if n==bouncer)
exp_r = exp_rank[bouncer]

m1, m2, m3, m4 = st.columns(4)
m1.metric("現在合計", f"{totals[bouncer]}点")
m2.metric("現在順位", f"{current_rank}位")
m3.metric("期待合計", f"{expected[bouncer]:.1f}点")
m4.metric("期待順位", f"{exp_r}位", delta=f"{current_rank-exp_r:+d}" if current_rank!=exp_r else None,
          delta_color="inverse")

# 未確定試合の分析
analysis = []
for mid in sorted(matches):
    m = matches[mid]
    if m["winner"] is None and m["teams"][0] and m["teams"][1]:
        ta, tb = m["teams"]
        pa = SCORES[bouncer][ta-1]
        pb = SCORES[bouncer][tb-1]
        preferred = ta if pa < pb else tb
        other = tb if preferred == ta else ta
        analysis.append({
            "試合": f"試合{mid}",
            "日程": MATCH_SCHEDULE[mid],
            "ラウンド": ROUND_NAMES[mid],
            "対戦": f"{TEAMS[ta]} vs {TEAMS[tb]}",
            "バウンサー推し": f"✅ {TEAMS[preferred]}",
            "有利チームの点数": min(pa, pb),
            "不利チームの点数": max(pa, pb),
            "点差": abs(pa - pb),
            "期待加算": (pa + pb) / 2,
            "_preferred_id": preferred,
            "_other_id": other,
        })

if not analysis:
    st.info("現在、分析対象の試合がありません。")
else:
    # 影響度順ソート
    analysis.sort(key=lambda x: x["点差"], reverse=True)

    # 最重要試合ハイライト
    top = analysis[0]
    if top["点差"] >= 5:
        st.warning(
            f"⚡ **最重要試合: {top['試合']} ({top['ラウンド']})**　"
            f"{top['対戦']}　→ **{top['バウンサー推し']}** が勝つと有利！　点差: **{top['点差']}点**"
        )

    df_analysis = pd.DataFrame([{
        "試合": a["試合"],
        "日程": a["日程"],
        "ラウンド": a["ラウンド"],
        "対戦カード": a["対戦"],
        "バウンサー推し": a["バウンサー推し"],
        "有利点数": a["有利チームの点数"],
        "不利点数": a["不利チームの点数"],
        "点差": a["点差"],
        "期待加算": f"{a['期待加算']:.1f}点",
    } for a in analysis])

    st.dataframe(
        df_analysis, use_container_width=True, hide_index=True,
        column_config={
            "点差": st.column_config.ProgressColumn(
                "点差（影響度）", min_value=0, max_value=49, format="%d"
            ),
        }
    )

st.divider()

# =============================================
# スコア内訳（試合が始まったら）
# =============================================

if completed:
    with st.expander(f"📊 スコア内訳（各チームの勝利による加算点）"):
        for rank, (name, total) in enumerate(sorted_now, 1):
            win_list = []
            for mid, m in sorted(matches.items()):
                if m["winner"]:
                    w = m["winner"]
                    pts = SCORES[name][w-1]
                    win_list.append(f"{TEAMS[w]}(+{pts})")
            st.write(f"**{medals[rank-1] if rank<=3 else str(rank)+'位'} {name}** — 合計{total}点")
            if win_list:
                st.caption("  →  " + "、".join(win_list))

st.divider()

# =============================================
# 賞金テーブル
# =============================================

with st.expander("💰 賞金テーブル"):
    prize_df = pd.DataFrame([
        {"順位": "1位", "賞金": "+15,000P"},
        {"順位": "2位", "賞金": "+7,000P"},
        {"順位": "3位", "賞金": "+2,000P"},
        {"順位": "4位", "賞金": "-2,000P"},
        {"順位": "5〜6位", "賞金": "±0P"},
        {"順位": "7位", "賞金": "-3,000P"},
        {"順位": "8位", "賞金": "-1,000P"},
    ])
    st.dataframe(prize_df, use_container_width=False, hide_index=True)

st.caption("データは画像より入力。誤りがある場合はお知らせください。")

st.divider()

# =============================================
# 管理者：結果手動入力
# =============================================

with st.expander("🔧 管理者：結果を手動入力"):
    pwd = st.text_input("管理者コード", type="password", key="admin_pwd")
    if pwd == "koshien2026":
        st.success("管理者モード")

        saved = load_saved_results()

        # 入力対象の試合一覧（対戦カードが確定しているもの）
        all_matchups = resolve_matchups(results)

        # 試合選択
        match_options = {
            mid: f"試合{mid} {MATCH_SCHEDULE.get(mid,'')} ({ROUND_NAMES.get(mid,'')}) "
                 f"　{TEAMS[ta]} vs {TEAMS[tb]}"
                 + (f"　→ 登録済: {TEAMS[results[mid]]}" if mid in results else "")
            for mid, (ta, tb) in sorted(all_matchups.items())
        }

        selected_mid = st.selectbox(
            "試合を選択",
            options=list(match_options.keys()),
            format_func=lambda x: match_options[x],
        )

        if selected_mid:
            ta, tb = all_matchups[selected_mid]
            winner_choice = st.radio(
                "勝者チーム",
                options=[ta, tb],
                format_func=lambda x: TEAMS[x],
                horizontal=True,
            )

            col_save, col_del = st.columns(2)
            with col_save:
                if st.button("✅ 結果を保存", use_container_width=True):
                    saved[selected_mid] = winner_choice
                    save_results(saved)
                    st.cache_data.clear()
                    st.success(f"試合{selected_mid}の結果を保存しました：{TEAMS[winner_choice]}")
                    st.rerun()
            with col_del:
                if selected_mid in saved:
                    if st.button("🗑 この試合の結果を削除", use_container_width=True):
                        del saved[selected_mid]
                        save_results(saved)
                        st.cache_data.clear()
                        st.warning(f"試合{selected_mid}の結果を削除しました")
                        st.rerun()

        # 登録済み一覧
        st.markdown("**現在の登録済み結果**")
        if saved:
            for mid, winner_id in sorted(saved.items()):
                ta, tb = all_matchups.get(mid, (winner_id, winner_id))
                loser = tb if winner_id == ta else ta
                st.write(f"試合{mid} ({ROUND_NAMES.get(mid,'')})　◯ **{TEAMS[winner_id]}** vs {TEAMS.get(loser, '?')} ✕")
        else:
            st.info("登録なし")
    elif pwd:
        st.error("コードが違います")
