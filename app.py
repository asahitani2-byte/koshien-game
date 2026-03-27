"""
センバツ2026 甲子園ゲーム
第98回選抜高等学校野球大会 スコア管理サイト
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
    page_title="センバツ2026 甲子園ゲーム",
    page_icon="⚾",
    layout="wide",
)

# =============================================
# データ定義
# =============================================

TEAMS = {
    1:"帝京", 2:"沖縄尚学", 3:"阿南光", 4:"中京大中京",
    5:"八戸学院光星", 6:"崇徳", 7:"滋賀学園", 8:"長崎西",
    9:"横浜", 10:"神村学園", 11:"花巻東", 12:"智辯学園",
    13:"東洋大姫路", 14:"花咲徳栄", 15:"高知農", 16:"日本文理",
    17:"北照", 18:"専大松戸", 19:"神戸国際大附", 20:"九州国際大附",
    21:"近江", 22:"大垣日大", 23:"山梨学院", 24:"長崎日大",
    25:"東北", 26:"帝京長岡", 27:"高川学園", 28:"英明",
    29:"三重", 30:"佐野日大", 31:"熊本工", 32:"大阪桐蔭",
}

SCORES = {
    "バウンサー": [13,17,29,18,23, 4,24,31, 9, 7, 8, 3, 6,20,32,26,22,16,14, 1,25,19,12,10,27,30,11,21, 5,28,15, 2],
    "タメオ":     [ 8, 9,31,17,10, 7,23,32, 5,11, 6,13,24,14,26,27,15,16, 3, 2,21,19, 1,20,22,29,30, 4,18,28,25,12],
    "パワーズ":   [18, 3,20,13,11,12, 8,32,10, 6, 1,16,14,23,31,29,30,24, 4, 5,15,25, 2,21,19,28,17, 9,27,26,22, 7],
    "紫雷":       [23, 8,28,10,24, 5,20,31,14,12, 9, 7,11,13,32,29,30,16, 2, 4,26,15, 1,27,19,18, 3,17,22,21,25, 6],
    "甘味部":     [10,11,25,14, 8, 2,26,32,20, 5, 1, 6, 9,17,31,30,15,16, 7, 4,18,23, 3,22,28,29,21,19,24,27,12,13],
    "まなりくと": [13, 8,27,11,16,12,19,30, 6,15, 9,10,22, 1,31,28,18,32, 4, 3,20, 7, 2,21,24,17,29,14,23,25,26, 5],
    "邪神ちゃん": [16,12,31,25, 4, 2,29,28, 7, 8,15,24,30,20,32,27, 1,22, 3, 9,17,19, 5,11,23,21,14,13,18,26,10, 6],
    "マカDX":     [ 9, 1,28,15,18,19, 6,32, 8, 2,17, 5,11,22,31,21,29,24, 4, 3,12,16, 7,14,25,30,26,20,27,23,13,10],
}

FIRST_ROUND = {
    1:(1,2), 2:(3,4), 3:(5,6), 4:(7,8),
    5:(9,10), 6:(11,12), 7:(13,14), 8:(15,16),
    9:(17,18), 10:(19,20), 11:(21,22), 12:(23,24),
    13:(25,26), 14:(27,28), 15:(29,30), 16:(31,32),
}

BRACKET = {
    17:(1,2), 18:(3,4), 19:(5,6), 20:(7,8),
    21:(9,10), 22:(11,12), 23:(13,14), 24:(15,16),
    25:(17,18), 26:(19,20), 27:(21,22), 28:(23,24),
    29:(25,26), 30:(27,28),
    31:(29,30),
}

ROUND_NAMES = {
    **{i:"1回戦" for i in range(1,17)},
    **{i:"2回戦" for i in range(17,25)},
    **{i:"準々決勝" for i in range(25,29)},
    **{i:"準決勝" for i in range(29,31)},
    31:"決勝",
}

MATCH_SCHEDULE = {
    1:"第1日①", 2:"第1日②", 3:"第1日③",
    4:"第2日①", 5:"第2日②", 6:"第2日③",
    7:"第3日①", 8:"第3日②", 9:"第3日③",
    10:"第4日①", 11:"第4日②", 12:"第4日③",
    13:"第5日①", 14:"第5日②", 15:"第5日③",
    16:"第6日①", 17:"第6日②", 18:"第6日③",
    19:"第7日①", 20:"第7日②", 21:"第7日③",
    22:"第8日①", 23:"第8日②", 24:"第8日③",
    25:"第9日①", 26:"第9日②", 27:"第9日③", 28:"第9日④",
    29:"第10日①", 30:"第10日②",
    31:"第11日",
}

PRIZE = {1: 15000, 2: 7000, 3: 2000, 4: -2000, 7: -3000, 8: -1000}

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
    for i, pat in enumerate([
        rf"{re.escape(team_a)}\D{{0,6}}(\d+)[－\-ー](\d+)\D{{0,6}}{re.escape(team_b)}",
        rf"{re.escape(team_b)}\D{{0,6}}(\d+)[－\-ー](\d+)\D{{0,6}}{re.escape(team_a)}",
    ]):
        m = re.search(pat, text)
        if m:
            s1, s2 = int(m.group(1)), int(m.group(2))
            if s1 == s2:
                continue
            return (ta if s1 > s2 else tb) if i == 0 else (tb if s1 > s2 else ta)
    return None

@st.cache_data(ttl=300)  # 5分キャッシュ
def fetch_results():
    # 手動登録結果を最優先で読み込む
    results = load_saved_results()

    # Wikipedia テキスト取得
    wiki_text = ""
    try:
        url = "https://ja.wikipedia.org/wiki/%E7%AC%AC98%E5%9B%9E%E9%81%B8%E6%8A%9C%E9%AB%98%E7%AD%89%E5%AD%A6%E6%A0%A1%E9%87%8E%E7%90%83%E5%A4%A7%E4%BC%9A"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        wiki_text = BeautifulSoup(resp.text, "html.parser").get_text()
    except Exception:
        pass

    # baseball-channel テキスト取得
    bc_text = ""
    try:
        resp = requests.get("https://www.baseballchannel.jp/etc/252405/", timeout=8,
                            headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            bc_text = BeautifulSoup(resp.text, "html.parser").get_text()
    except Exception:
        pass

    # 全試合を順番にスクレイピング（1回戦→2回戦→…と進める）
    # まず1回戦の対戦カードは固定
    all_matchups = dict(FIRST_ROUND)  # {mid: (ta, tb)}

    # 2回戦以降はその時点の結果から対戦カードを動的構築
    for mid in sorted(BRACKET.keys()):
        prev_a, prev_b = BRACKET[mid]
        wa = results.get(prev_a)
        wb = results.get(prev_b)
        if wa and wb:
            all_matchups[mid] = (wa, wb)

    # 各試合をスクレイピング（手動登録済みはスキップ）
    for mid, (ta, tb) in sorted(all_matchups.items()):
        if mid in results:
            continue
        winner = _search_score(wiki_text, ta, tb) or _search_score(bc_text, ta, tb)
        if winner:
            results[mid] = winner

    return results

# =============================================
# ゲームロジック
# =============================================

def build_matches(results):
    matches = {}
    for mid, (ta, tb) in FIRST_ROUND.items():
        matches[mid] = {"teams": (ta, tb), "winner": results.get(mid)}

    for mid in sorted(BRACKET.keys()):
        prev_a, prev_b = BRACKET[mid]
        wa = matches[prev_a]["winner"] if prev_a in matches else None
        wb = matches[prev_b]["winner"] if prev_b in matches else None
        matches[mid] = {"teams": (wa, wb), "winner": results.get(mid)}

    return matches

def calc_totals(matches):
    totals = {n: 0 for n in SCORES}
    for mid in sorted(matches):
        w = matches[mid]["winner"]
        if w:
            for n in SCORES:
                totals[n] += SCORES[n][w - 1]
    return totals

def calc_expected(matches, totals):
    exp_add = {n: 0.0 for n in SCORES}
    for mid in sorted(matches):
        w = matches[mid]["winner"]
        ta, tb = matches[mid]["teams"]
        if w is None and ta and tb:
            for n in SCORES:
                exp_add[n] += (SCORES[n][ta-1] + SCORES[n][tb-1]) / 2.0
    return {n: totals[n] + exp_add[n] for n in SCORES}

# =============================================
# UI
# =============================================

st.title("⚾ センバツ2026 甲子園ゲーム")
st.caption(f"第98回選抜高等学校野球大会 ｜ 3/19〜3/31 阪神甲子園球場 ｜ 更新: {datetime.now().strftime('%m/%d %H:%M')}")

# 更新ボタン
col_btn, col_info = st.columns([1, 4])
with col_btn:
    if st.button("🔄 最新結果を取得", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col_info:
    st.info("5分ごとに自動更新 | 大会開幕: 3月19日（木）")

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
    for tid in range(1, 33):
        vals = [SCORES[name][tid-1] for name in PARTICIPANT_NAMES]
        avg = sum(vals) / len(vals)
        row = {"#": tid, "チーム": TEAMS[tid]}
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
        st.info("大会開幕後に結果が表示されます（3/19〜）")
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
            st.info("全16試合の1回戦対戦カードが表示されます")
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
                "点差（影響度）", min_value=0, max_value=32, format="%d"
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
        all_matchups = dict(FIRST_ROUND)
        for mid in sorted(BRACKET.keys()):
            prev_a, prev_b = BRACKET[mid]
            wa = results.get(prev_a)
            wb = results.get(prev_b)
            if wa and wb:
                all_matchups[mid] = (wa, wb)

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
