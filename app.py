import streamlit as st
import json
import os
from datetime import date, datetime, timedelta
import pandas as pd

st.set_page_config(
    page_title="YT Tracker – Ferd",
    page_icon="💪",
    layout="wide"
)

# ── Ferd farger ──────────────────────────────────────────────────────────────
NAVY   = "#1F2E4B"
BEIGE  = "#EFE7E0"
TEAL   = "#3B756A"
CHOC   = "#5C3317"
ORANGE = "#C8532A"
WHITE  = "#FFFFFF"
GOLD   = "#B8860B"
PURPLE = "#6B4F8A"
RED    = "#C0392B"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,500;0,700;1,500&family=Inter:wght@300;400;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
    background-color: {BEIGE} !important;
}}
.stApp {{ background-color: {BEIGE} !important; }}
.block-container {{
    padding-top: 0 !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    max-width: 1100px !important;
}}
#MainMenu, footer, header {{ visibility: hidden; }}

.stButton > button {{
    background-color: {NAVY} !important;
    color: {BEIGE} !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 12px 18px !important;
    width: 100% !important;
}}
.stButton > button:hover {{ background-color: {TEAL} !important; }}

div[data-baseweb="select"] > div {{
    background: {WHITE} !important;
    border: 1px solid #ccc7c0 !important;
    border-radius: 2px !important;
    font-family: 'Inter', sans-serif !important;
}}
.stNumberInput > div > div > input {{
    background: {WHITE} !important;
    border: 1px solid #ccc7c0 !important;
    border-radius: 2px !important;
    color: {NAVY} !important;
    font-family: 'Inter', sans-serif !important;
}}
label, .stSelectbox label, .stNumberInput label {{
    color: #555 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px !important;
}}
details summary {{
    color: {NAVY} !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
}}
</style>
""", unsafe_allow_html=True)

# ── DATA ─────────────────────────────────────────────────────────────────────
DATA_FILE = "yt_data.json"

FLAVORS = {
    "Sjokolade 🍫": "sjokolade",
    "Banan/Jordbær 🍌🍓": "banan-jordbaer"
}

# Matvarer med protein per enhet
FOOD_CONFIG = {
    "egg": {
        "label": "Egg 🥚",
        "unit": "egg",
        "protein_per_unit": 6,
        "color": GOLD,
        "desc": "6g protein per egg",
        "min": 1, "max": 20, "default": 2
    },
    "cottage_cheese": {
        "label": "Cottage Cheese 🧀",
        "unit": "gram",
        "protein_per_unit": 0.12,   # 12g per 100g
        "color": PURPLE,
        "desc": "12g protein per 100g",
        "min": 50, "max": 500, "default": 150
    },
    "ultraprosessert": {
        "label": "Ultraprosessert 🍔",
        "unit": "gang",
        "protein_per_unit": 0,
        "color": RED,
        "desc": "Sporer forbruk – ikke protein",
        "min": 1, "max": 10, "default": 1
    },
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
        if "user_goals" not in d:
            d["user_goals"] = {u: d.get("weekly_protein_goal", 200) for u in d.get("users", [])}
        if "food_log" not in d:
            d["food_log"] = []
        return d
    return {
        "start_date": str(date.today()),
        "start_count": 30,
        "current_count": 30,
        "weekly_protein_goal": 200,
        "user_goals": {"Erik": 200, "Trym": 200},
        "log": [],
        "food_log": [],
        "users": ["Erik", "Trym"]
    }

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

data = load_data()

# ── BEREGNINGER ───────────────────────────────────────────────────────────────
total_taken   = data["start_count"] - data["current_count"]
today_d       = date.today()
week_start    = today_d - timedelta(days=today_d.weekday())
days_elapsed  = max((today_d - date.fromisoformat(data["start_date"])).days + 1, 1)
avg_per_day   = round(total_taken / days_elapsed, 1)
pct_left      = round(data["current_count"] / data["start_count"] * 100)
weekly_goal   = data.get("weekly_protein_goal", 200)

week_log = [e for e in data["log"]
            if e.get("flavor") != "påfyll"
            and date.fromisoformat(e["date"]) >= week_start]

week_food_log = [e for e in data["food_log"]
                 if date.fromisoformat(e["date"]) >= week_start
                 and e.get("food") != "ultraprosessert"]

# Total protein inkludert alle matkilder
yt_protein_total   = total_taken * 20
food_protein_total = sum(e.get("protein", 0) for e in data["food_log"]
                         if e.get("food") != "ultraprosessert")
total_protein      = yt_protein_total + food_protein_total

week_protein_yt   = len(week_log) * 20
week_protein_food = sum(e.get("protein", 0) for e in week_food_log)
week_protein      = week_protein_yt + week_protein_food
week_pct          = min(round(week_protein / weekly_goal * 100), 100)

# ── HJELPEFUNKSJONER ──────────────────────────────────────────────────────────
def calc_streak(user, log):
    days_with_log = set(
        e["date"] for e in log
        if e.get("user") == user and e.get("flavor") != "påfyll"
    )
    streak = 0
    check = today_d
    while str(check) in days_with_log:
        streak += 1
        check -= timedelta(days=1)
    return streak

def user_logged_today(user, log):
    return any(
        e.get("user") == user and e.get("flavor") != "påfyll"
        and e["date"] == str(today_d)
        for e in log
    )

def section_title(title):
    return f"""<div style="font-family:'EB Garamond',serif;font-size:22px;
        color:{NAVY};border-bottom:1px solid #d4cdc6;padding-bottom:10px;
        margin-bottom:20px;">{title}</div>"""

def food_mini_stat(label, value, color):
    return f"""
    <div style="background:{WHITE};border-left:3px solid {color};border-radius:2px;
                padding:10px 14px;text-align:center;flex:1;">
        <div style="font-size:9px;font-weight:600;letter-spacing:2px;text-transform:uppercase;
                    color:#999;margin-bottom:4px;">{label}</div>
        <div style="font-family:'EB Garamond',serif;font-size:28px;font-weight:700;
                    color:{color};line-height:1;">{value}</div>
    </div>"""

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{NAVY};padding:18px 32px 12px;margin-bottom:0;display:flex;
            justify-content:space-between;align-items:center;">
    <span style="font-family:'EB Garamond',serif;font-size:24px;font-weight:700;
                 letter-spacing:5px;color:{BEIGE};text-transform:uppercase;">
        FERD<span style="color:{TEAL}">.</span>
    </span>
    <span style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#7a90aa;">
        Protein &middot; Kjøleskapstracker
    </span>
</div>
<div style="background:{NAVY};padding:20px 32px 28px;margin-bottom:32px;">
    <div style="font-family:'EB Garamond',serif;font-size:42px;font-weight:500;
                color:{BEIGE};line-height:1.1;margin-bottom:8px;">
        Proteinoversikt &nbsp;<em style="color:{TEAL};font-style:italic;">Kjøleskap</em>
    </div>
    <div style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#7a90aa;">
        YT &nbsp;&middot;&nbsp; Egg &nbsp;&middot;&nbsp; Cottage Cheese &nbsp;&middot;&nbsp; Ultraprosessert
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI-KORT ─────────────────────────────────────────────────────────────────
def kpi_card(label, value, unit, bar_pct, color=NAVY):
    bar_pct = max(0, min(bar_pct, 100))
    return f"""
    <div style="background:{WHITE};border-top:4px solid {color};border-radius:2px;
                padding:22px 20px 18px;height:100%;">
        <div style="font-size:9px;font-weight:600;letter-spacing:2.5px;
                    text-transform:uppercase;color:#999;margin-bottom:10px;">{label}</div>
        <div style="font-family:'EB Garamond',serif;font-size:50px;font-weight:700;
                    color:{color};line-height:1;margin-bottom:4px;">{value}</div>
        <div style="font-size:11px;color:#aaa;margin-bottom:14px;">{unit}</div>
        <div style="background:{BEIGE};height:3px;border-radius:2px;overflow:hidden;">
            <div style="width:{bar_pct}%;height:100%;background:{color};border-radius:2px;"></div>
        </div>
    </div>"""

# Beste streak
best_streak_user, best_streak_val = "–", 0
for u in data.get("users", []):
    s = calc_streak(u, data["log"])
    if s > best_streak_val:
        best_streak_val, best_streak_user = s, u

# Ukens leder (inkl. mat-protein)
week_leader, week_leader_protein = "–", 0
for u in data.get("users", []):
    u_yt    = sum(20 for e in week_log if e.get("user") == u)
    u_food  = sum(e.get("protein", 0) for e in week_food_log if e.get("user") == u)
    u_total = u_yt + u_food
    if u_total > week_leader_protein:
        week_leader_protein, week_leader = u_total, u

c1, c2, c3, c4 = st.columns(4)
with c1:
    streak_unit = f"dag{'er' if best_streak_val != 1 else ''} på rad" if best_streak_val > 0 else "ingen streak ennå"
    streak_pct = min(best_streak_val * 10, 100)
    st.markdown(kpi_card("Beste streak", f"🔥 {best_streak_val}" if best_streak_val > 0 else "–",
        f"{best_streak_user} · {streak_unit}", streak_pct, ORANGE), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("Total protein", f"{total_protein}g",
        f"YT + egg + cottage cheese", 100, TEAL), unsafe_allow_html=True)
with c3:
    w_color = TEAL if week_pct >= 100 else NAVY
    st.markdown(kpi_card("Protein denne uken", f"{week_protein}g",
        f"mål {weekly_goal}g · {week_pct}% nådd", week_pct, w_color), unsafe_allow_html=True)
with c4:
    leader_pct = min(round(week_leader_protein / weekly_goal * 100), 100) if weekly_goal > 0 else 0
    leader_unit = f"{week_leader_protein}g denne uken" if week_leader != "–" else "ingen registreringer"
    st.markdown(kpi_card("Ukens leder", week_leader,
        leader_unit, leader_pct, TEAL), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"<hr style='border:none;border-top:1px solid #d4cdc6;margin:24px 0'>", unsafe_allow_html=True)

# ── REGISTRER YT + STATISTIKK ────────────────────────────────────────────────
col_l, col_r = st.columns([1, 1.6])

with col_l:
    st.markdown(section_title("Registrer YT 💪"), unsafe_allow_html=True)

    user = st.selectbox("Hvem er du?", data.get("users", ["Erik", "Trym"]))

    if not user_logged_today(user, data["log"]):
        st.markdown(f"""
        <div style="background:#fff3cd;border-left:4px solid {ORANGE};
                    border-radius:2px;padding:10px 14px;margin-bottom:12px;
                    font-size:12px;color:#856404;">
            ⏰ <strong>Påminnelse:</strong> Du har ikke registrert noen YT i dag, {user}!
        </div>""", unsafe_allow_html=True)
    else:
        streak = calc_streak(user, data["log"])
        streak_text = f"🔥 {streak} dager på rad!" if streak > 1 else "✓ Registrert i dag"
        st.markdown(f"""
        <div style="background:#e8f5e9;border-left:4px solid {TEAL};
                    border-radius:2px;padding:10px 14px;margin-bottom:12px;
                    font-size:12px;color:#2e7d32;">{streak_text}</div>""",
        unsafe_allow_html=True)

    flavor_display = st.selectbox("Smak", list(FLAVORS.keys()))
    flavor = FLAVORS[flavor_display]
    amount = st.number_input("Antall YT", min_value=1,
                             max_value=max(data["current_count"], 1), value=1)

    st.markdown(f"""
    <div style="background:{BEIGE};border-radius:2px;padding:10px 14px;
                margin:4px 0 16px;font-size:12px;color:#555;">
        💪 Dette gir <strong style="color:{TEAL};">{amount * 20}g protein</strong>
    </div>""", unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    with b1:
        if st.button("REGISTRER →"):
            if data["current_count"] >= amount:
                data["current_count"] -= amount
                for _ in range(amount):
                    data["log"].insert(0, {
                        "date": str(today_d),
                        "time": datetime.now().strftime("%H:%M"),
                        "user": user, "flavor": flavor, "protein": 20
                    })
                save_data(data)
                st.success(f"✓ {user}: {amount}× registrert. {data['current_count']} igjen.")
                st.rerun()
            else:
                st.error("Ikke nok YT igjen!")
    with b2:
        if st.button("PÅFYLL +"):
            st.session_state["show_refill"] = not st.session_state.get("show_refill", False)

    if st.session_state.get("show_refill"):
        refill = st.number_input("Antall å legge til", min_value=1, max_value=200, value=30)
        if st.button("BEKREFT PÅFYLL"):
            data["current_count"] += refill
            data["log"].insert(0, {
                "date": str(today_d), "time": datetime.now().strftime("%H:%M"),
                "user": "System", "flavor": "påfyll", "protein": 0
            })
            save_data(data)
            st.session_state["show_refill"] = False
            st.success(f"✓ Lagt til {refill} YT. Nå: {data['current_count']}")
            st.rerun()

    st.markdown(f"<hr style='border:none;border-top:1px solid #d4cdc6;margin:20px 0'>", unsafe_allow_html=True)
    st.markdown(section_title("Smaksfordeling"), unsafe_allow_html=True)

    flavor_counts = {"sjokolade": 0, "banan-jordbaer": 0}
    for e in data["log"]:
        f = e.get("flavor", "")
        if f in flavor_counts:
            flavor_counts[f] += 1

    total_f = sum(flavor_counts.values()) or 1
    flavor_cfg = {
        "sjokolade":      {"label": "Sjokolade 🍫",       "color": CHOC},
        "banan-jordbaer": {"label": "Banan/Jordbær 🍌🍓",  "color": TEAL},
    }
    for fkey, cnt in flavor_counts.items():
        pf = round(cnt / total_f * 100)
        cfg = flavor_cfg[fkey]
        st.markdown(f"""
        <div style="margin-bottom:16px;">
            <div style="display:flex;justify-content:space-between;
                        font-size:12px;color:#555;margin-bottom:5px;">
                <span style="font-weight:600;color:{NAVY};">{cfg['label']}</span>
                <span>{cnt} stk · {pf}%</span>
            </div>
            <div style="background:{BEIGE};height:4px;border-radius:2px;overflow:hidden;">
                <div style="width:{pf}%;height:100%;background:{cfg['color']};border-radius:2px;"></div>
            </div>
        </div>""", unsafe_allow_html=True)

with col_r:
    st.markdown(section_title("Statistikk per person"), unsafe_allow_html=True)

    user_stats = {}
    for e in data["log"]:
        u = e.get("user", "Ukjent")
        if u == "System":
            continue
        if u not in user_stats:
            user_stats[u] = {"total": 0, "sjokolade": 0, "banan-jordbaer": 0, "protein": 0}
        user_stats[u]["total"] += 1
        f = e.get("flavor", "")
        if f in user_stats[u]:
            user_stats[u][f] += 1
        user_stats[u]["protein"] += 20

    # Legg til mat-protein
    for e in data.get("food_log", []):
        u = e.get("user", "Ukjent")
        if u not in user_stats:
            user_stats[u] = {"total": 0, "sjokolade": 0, "banan-jordbaer": 0, "protein": 0}
        user_stats[u]["protein"] += e.get("protein", 0)

    if user_stats:
        max_t = max(s["total"] for s in user_stats.values()) or 1
        for uname, stats in sorted(user_stats.items(), key=lambda x: -x[1]["protein"]):
            bw = round(stats["total"] / max_t * 100)
            streak = calc_streak(uname, data["log"])
            streak_badge = (
                f'<span style="background:#fff3cd;color:#856404;padding:2px 8px;'
                f'border-radius:2px;font-size:10px;font-weight:700;margin-left:8px;">'
                f'🔥 {streak}d streak</span>'
            ) if streak > 0 else ""

            user_weekly_goal = data.get("user_goals", {}).get(uname, weekly_goal)
            u_week_yt   = sum(20 for e in week_log if e.get("user") == uname)
            u_week_food = sum(e.get("protein", 0) for e in week_food_log if e.get("user") == uname)
            user_week_protein = u_week_yt + u_week_food
            user_week_pct = (
                min(round(user_week_protein / user_weekly_goal * 100), 100)
                if user_weekly_goal > 0 else 0
            )
            uw_color = TEAL if user_week_pct >= 100 else NAVY

            st.markdown(f"""
            <div style="background:{BEIGE};border-left:4px solid {TEAL};
                        border-radius:2px;padding:16px 18px;margin-bottom:12px;">
                <div style="font-weight:600;font-size:15px;color:{NAVY};margin-bottom:4px;
                            display:flex;align-items:center;">
                    {uname}{streak_badge}
                </div>
                <div style="font-size:11px;color:#777;margin-bottom:8px;">
                    Denne uken:
                    <strong style="color:{uw_color};">{user_week_protein}g</strong>
                    av mål {user_weekly_goal}g ({user_week_pct}%)
                </div>
                <div style="background:#d4cdc6;height:3px;border-radius:2px;
                            overflow:hidden;margin-bottom:8px;">
                    <div style="width:{bw}%;height:100%;background:{TEAL};border-radius:2px;"></div>
                </div>
                <div style="font-size:11px;color:#777;">
                    {stats['total']} YT totalt &nbsp;·&nbsp;
                    {stats['protein']}g protein (alle kilder) &nbsp;·&nbsp;
                    🍫 {stats['sjokolade']} &nbsp;·&nbsp;
                    🍌🍓 {stats['banan-jordbaer']}
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#aaa;font-size:13px;'>Ingen registreringer ennå.</p>",
                    unsafe_allow_html=True)

st.markdown(f"<hr style='border:none;border-top:1px solid #d4cdc6;margin:24px 0'>", unsafe_allow_html=True)

# ── MAT-TRACKER: EGG ─────────────────────────────────────────────────────────
st.markdown(section_title("Egg 🥚"), unsafe_allow_html=True)

egg_col_l, egg_col_r = st.columns([1, 1.6])
egg_log = [e for e in data.get("food_log", []) if e.get("food") == "egg"]
cfg_egg = FOOD_CONFIG["egg"]

with egg_col_l:
    egg_user  = st.selectbox("Hvem?", data.get("users", []), key="egg_user")
    egg_amt   = st.number_input("Antall egg", min_value=1, max_value=20, value=2, key="egg_amt")
    egg_prot  = round(egg_amt * cfg_egg["protein_per_unit"])
    st.markdown(f"""
    <div style="background:{BEIGE};border-radius:2px;padding:10px 14px;
                margin:4px 0 16px;font-size:12px;color:#555;">
        🥚 Dette gir <strong style="color:{GOLD};">{egg_prot}g protein</strong>
    </div>""", unsafe_allow_html=True)
    if st.button("REGISTRER EGG →", key="egg_btn"):
        data["food_log"].insert(0, {
            "date": str(today_d), "time": datetime.now().strftime("%H:%M"),
            "user": egg_user, "food": "egg",
            "amount": egg_amt, "protein": egg_prot
        })
        save_data(data)
        st.success(f"✓ {egg_user}: {egg_amt} egg registrert ({egg_prot}g protein)")
        st.rerun()

with egg_col_r:
    egg_today  = sum(e["amount"] for e in egg_log if e["date"] == str(today_d))
    egg_week   = sum(e["amount"] for e in egg_log if date.fromisoformat(e["date"]) >= week_start)
    egg_total  = sum(e["amount"] for e in egg_log)
    egg_prot_w = sum(e.get("protein", 0) for e in egg_log if date.fromisoformat(e["date"]) >= week_start)

    st.markdown(f"""
    <div style="display:flex;gap:12px;margin-bottom:16px;">
        {food_mini_stat("I dag", egg_today, GOLD)}
        {food_mini_stat("Denne uken", egg_week, GOLD)}
        {food_mini_stat("Totalt", egg_total, GOLD)}
    </div>
    <div style="background:{BEIGE};border-left:3px solid {GOLD};border-radius:2px;
                padding:10px 14px;font-size:12px;color:#555;">
        Protein denne uken fra egg: <strong style="color:{GOLD};">{egg_prot_w}g</strong>
    </div>""", unsafe_allow_html=True)

    if egg_log:
        st.markdown("<br>", unsafe_allow_html=True)
        for e in egg_log[:5]:
            st.markdown(f"""
            <div style="background:{WHITE};border-left:3px solid {GOLD};border-radius:0 2px 2px 0;
                        padding:8px 14px;margin-bottom:4px;font-size:12px;
                        display:flex;justify-content:space-between;">
                <span><strong style="color:{NAVY};">{e.get('user','–')}</strong>
                      <span style="color:#bbb;margin-left:8px;">{e['date']} · {e.get('time','–')}</span></span>
                <span style="color:{GOLD};font-weight:600;">{e['amount']} egg · +{e.get('protein',0)}g</span>
            </div>""", unsafe_allow_html=True)

st.markdown(f"<hr style='border:none;border-top:1px solid #d4cdc6;margin:24px 0'>", unsafe_allow_html=True)

# ── MAT-TRACKER: COTTAGE CHEESE ──────────────────────────────────────────────
st.markdown(section_title("Cottage Cheese 🧀"), unsafe_allow_html=True)

cc_col_l, cc_col_r = st.columns([1, 1.6])
cc_log = [e for e in data.get("food_log", []) if e.get("food") == "cottage_cheese"]
cfg_cc = FOOD_CONFIG["cottage_cheese"]

with cc_col_l:
    cc_user = st.selectbox("Hvem?", data.get("users", []), key="cc_user")
    cc_amt  = st.number_input("Gram cottage cheese", min_value=50, max_value=500, value=150, step=25, key="cc_amt")
    cc_prot = round(cc_amt * cfg_cc["protein_per_unit"])
    st.markdown(f"""
    <div style="background:{BEIGE};border-radius:2px;padding:10px 14px;
                margin:4px 0 16px;font-size:12px;color:#555;">
        🧀 Dette gir <strong style="color:{PURPLE};">{cc_prot}g protein</strong>
        <span style="color:#aaa;"> (12g/100g)</span>
    </div>""", unsafe_allow_html=True)
    if st.button("REGISTRER COTTAGE CHEESE →", key="cc_btn"):
        data["food_log"].insert(0, {
            "date": str(today_d), "time": datetime.now().strftime("%H:%M"),
            "user": cc_user, "food": "cottage_cheese",
            "amount": cc_amt, "protein": cc_prot
        })
        save_data(data)
        st.success(f"✓ {cc_user}: {cc_amt}g cottage cheese registrert ({cc_prot}g protein)")
        st.rerun()

with cc_col_r:
    cc_today  = sum(e["amount"] for e in cc_log if e["date"] == str(today_d))
    cc_week   = sum(e["amount"] for e in cc_log if date.fromisoformat(e["date"]) >= week_start)
    cc_total  = sum(e["amount"] for e in cc_log)
    cc_prot_w = sum(e.get("protein", 0) for e in cc_log if date.fromisoformat(e["date"]) >= week_start)

    st.markdown(f"""
    <div style="display:flex;gap:12px;margin-bottom:16px;">
        {food_mini_stat("I dag (g)", cc_today, PURPLE)}
        {food_mini_stat("Denne uken (g)", cc_week, PURPLE)}
        {food_mini_stat("Totalt (g)", cc_total, PURPLE)}
    </div>
    <div style="background:{BEIGE};border-left:3px solid {PURPLE};border-radius:2px;
                padding:10px 14px;font-size:12px;color:#555;">
        Protein denne uken fra cottage cheese: <strong style="color:{PURPLE};">{cc_prot_w}g</strong>
    </div>""", unsafe_allow_html=True)

    if cc_log:
        st.markdown("<br>", unsafe_allow_html=True)
        for e in cc_log[:5]:
            st.markdown(f"""
            <div style="background:{WHITE};border-left:3px solid {PURPLE};border-radius:0 2px 2px 0;
                        padding:8px 14px;margin-bottom:4px;font-size:12px;
                        display:flex;justify-content:space-between;">
                <span><strong style="color:{NAVY};">{e.get('user','–')}</strong>
                      <span style="color:#bbb;margin-left:8px;">{e['date']} · {e.get('time','–')}</span></span>
                <span style="color:{PURPLE};font-weight:600;">{e['amount']}g · +{e.get('protein',0)}g prot</span>
            </div>""", unsafe_allow_html=True)

st.markdown(f"<hr style='border:none;border-top:1px solid #d4cdc6;margin:24px 0'>", unsafe_allow_html=True)

# ── MAT-TRACKER: ULTRAPROSESSERT ─────────────────────────────────────────────
st.markdown(f"""<div style="font-family:'EB Garamond',serif;font-size:22px;
    color:{RED};border-bottom:2px solid {RED};padding-bottom:10px;
    margin-bottom:20px;">Ultraprosessert mat 🍔</div>""", unsafe_allow_html=True)

up_col_l, up_col_r = st.columns([1, 1.6])
up_log = [e for e in data.get("food_log", []) if e.get("food") == "ultraprosessert"]

with up_col_l:
    st.markdown(f"""
    <div style="background:#fdf0ee;border-left:4px solid {RED};border-radius:2px;
                padding:10px 14px;margin-bottom:14px;font-size:12px;color:#7b2d26;">
        ⚠️ Logg hver gang du spiser ultraprosessert mat for å holde oversikt.
    </div>""", unsafe_allow_html=True)

    up_user = st.selectbox("Hvem?", data.get("users", []), key="up_user")
    up_amt  = st.number_input("Antall ganger", min_value=1, max_value=10, value=1, key="up_amt")
    if st.button("REGISTRER 🍔", key="up_btn"):
        data["food_log"].insert(0, {
            "date": str(today_d), "time": datetime.now().strftime("%H:%M"),
            "user": up_user, "food": "ultraprosessert",
            "amount": up_amt, "protein": 0
        })
        save_data(data)
        st.warning(f"Registrert – prøv å kutte ned!")
        st.rerun()

with up_col_r:
    up_today = sum(e["amount"] for e in up_log if e["date"] == str(today_d))
    up_week  = sum(e["amount"] for e in up_log if date.fromisoformat(e["date"]) >= week_start)
    up_total = sum(e["amount"] for e in up_log)

    up_today_color = RED if up_today > 1 else ("#e67e22" if up_today == 1 else TEAL)

    st.markdown(f"""
    <div style="display:flex;gap:12px;margin-bottom:16px;">
        {food_mini_stat("I dag", up_today, up_today_color)}
        {food_mini_stat("Denne uken", up_week, RED)}
        {food_mini_stat("Totalt", up_total, RED)}
    </div>""", unsafe_allow_html=True)

    # Per-person ultraprosessert denne uken
    if data.get("users"):
        st.markdown(f"<div style='font-size:11px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#999;margin-bottom:8px;'>Fordeling denne uken</div>", unsafe_allow_html=True)
        for u in data["users"]:
            u_up = sum(e["amount"] for e in up_log
                       if e.get("user") == u and date.fromisoformat(e["date"]) >= week_start)
            u_pct = min(u_up * 20, 100)
            u_color = RED if u_up > 3 else ("#e67e22" if u_up > 1 else TEAL)
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;font-size:12px;
                            color:#555;margin-bottom:4px;">
                    <span style="font-weight:600;color:{NAVY};">{u}</span>
                    <span style="color:{u_color};font-weight:600;">{u_up} ganger</span>
                </div>
                <div style="background:{BEIGE};height:3px;border-radius:2px;overflow:hidden;">
                    <div style="width:{u_pct}%;height:100%;background:{u_color};border-radius:2px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

    if up_log:
        st.markdown("<br>", unsafe_allow_html=True)
        for e in up_log[:5]:
            st.markdown(f"""
            <div style="background:{WHITE};border-left:3px solid {RED};border-radius:0 2px 2px 0;
                        padding:8px 14px;margin-bottom:4px;font-size:12px;
                        display:flex;justify-content:space-between;">
                <span><strong style="color:{NAVY};">{e.get('user','–')}</strong>
                      <span style="color:#bbb;margin-left:8px;">{e['date']} · {e.get('time','–')}</span></span>
                <span style="color:{RED};font-weight:600;">{e['amount']}× 🍔</span>
            </div>""", unsafe_allow_html=True)

st.markdown(f"<hr style='border:none;border-top:1px solid #d4cdc6;margin:24px 0'>", unsafe_allow_html=True)

# ── GRAF ──────────────────────────────────────────────────────────────────────
st.markdown(section_title("Daglig forbruk – siste 14 dager"), unsafe_allow_html=True)

chart_view = st.radio("Vis etter:", ["YT-smak", "Person", "Matkilde"], horizontal=True)

chart_data = {}
for i in range(13, -1, -1):
    d = str(today_d - timedelta(days=i))
    if chart_view == "YT-smak":
        chart_data[d] = {"Sjokolade": 0, "Banan/Jordbær": 0}
    elif chart_view == "Person":
        chart_data[d] = {u: 0 for u in data.get("users", [])}
    else:
        chart_data[d] = {"YT": 0, "Egg": 0, "Cottage Cheese": 0}

for e in data["log"]:
    d = e.get("date")
    if d not in chart_data:
        continue
    if chart_view == "YT-smak":
        f = e.get("flavor", "")
        if f == "sjokolade":       chart_data[d]["Sjokolade"] += 1
        elif f == "banan-jordbaer": chart_data[d]["Banan/Jordbær"] += 1
    elif chart_view == "Person":
        u = e.get("user", "")
        if u in chart_data[d]: chart_data[d][u] += 1
    else:
        chart_data[d]["YT"] += 1

if chart_view in ("Matkilde",):
    for e in data.get("food_log", []):
        d = e.get("date")
        if d not in chart_data:
            continue
        food = e.get("food", "")
        if food == "egg"            and "Egg" in chart_data[d]:            chart_data[d]["Egg"] += e.get("amount", 0)
        elif food == "cottage_cheese" and "Cottage Cheese" in chart_data[d]: chart_data[d]["Cottage Cheese"] += round(e.get("amount", 0) / 100)

df = pd.DataFrame.from_dict(chart_data, orient="index")
df.index = [d[5:] for d in df.index]

if chart_view == "YT-smak":
    st.bar_chart(df, color=[CHOC, TEAL])
elif chart_view == "Person":
    user_palette = [NAVY, TEAL, ORANGE, CHOC, "#7a90aa", "#9c6b4e"]
    st.bar_chart(df, color=user_palette[:len(df.columns)])
else:
    st.bar_chart(df, color=[TEAL, GOLD, PURPLE])

st.markdown(f"<hr style='border:none;border-top:1px solid #d4cdc6;margin:24px 0'>", unsafe_allow_html=True)

# ── LOGG + CSV-EKSPORT ────────────────────────────────────────────────────────
log_col, export_col = st.columns([3, 1])
with log_col:
    st.markdown(section_title("Siste registreringer"), unsafe_allow_html=True)
with export_col:
    all_log = [e for e in data["log"] if e.get("flavor") != "påfyll"]
    all_log += data.get("food_log", [])
    if all_log:
        csv = pd.DataFrame(all_log).to_csv(index=False).encode("utf-8")
        st.markdown("<div style='padding-top:28px;'>", unsafe_allow_html=True)
        st.download_button("LAST NED CSV", data=csv,
                           file_name=f"logg_{today_d}.csv", mime="text/csv")
        st.markdown("</div>", unsafe_allow_html=True)

visible = [e for e in data["log"] if e.get("flavor") != "påfyll"][:20]
if visible:
    for e in visible:
        f       = e.get("flavor", "")
        is_choc = f == "sjokolade"
        border  = CHOC if is_choc else TEAL
        label   = "Sjokolade 🍫" if is_choc else "Banan/Jordbær 🍌🍓"
        bg_b    = "#f0e8e2" if is_choc else "#e4f0ee"
        col_b   = CHOC if is_choc else TEAL
        st.markdown(f"""
        <div style="background:{WHITE};border-left:3px solid {border};
                    border-radius:0 2px 2px 0;padding:11px 16px;margin-bottom:6px;
                    display:flex;justify-content:space-between;align-items:center;font-size:13px;">
            <div>
                <strong style="color:{NAVY};">{e.get('user','–')}</strong>
                <span style="color:#bbb;font-size:11px;margin-left:10px;">
                    {e['date']} · {e.get('time','–')}
                </span>
            </div>
            <div style="display:flex;gap:12px;align-items:center;">
                <span style="background:{bg_b};color:{col_b};padding:2px 10px;border-radius:2px;
                             font-size:10px;font-weight:700;letter-spacing:1px;
                             text-transform:uppercase;">{label}</span>
                <span style="font-size:11px;color:#aaa;">+20g protein</span>
            </div>
        </div>""", unsafe_allow_html=True)
else:
    st.markdown("<p style='color:#aaa;font-size:13px;'>Ingen registreringer ennå.</p>",
                unsafe_allow_html=True)

st.markdown(f"<hr style='border:none;border-top:1px solid #d4cdc6;margin:24px 0'>", unsafe_allow_html=True)

# ── INNSTILLINGER ─────────────────────────────────────────────────────────────
with st.expander("⚙️  Innstillinger"):
    tab1, tab2, tab3 = st.tabs(["Proteinmål", "Brukere", "Tilbakestill"])

    with tab1:
        st.markdown("**Ukentlig proteinmål per person**")
        user_goals   = data.get("user_goals", {})
        updated_goals = {}
        users_list   = data.get("users", [])
        goal_cols    = st.columns(max(len(users_list), 1))
        for i, u in enumerate(users_list):
            with goal_cols[i]:
                updated_goals[u] = st.number_input(
                    f"{u}", min_value=20, max_value=2000,
                    value=user_goals.get(u, weekly_goal), step=20, key=f"goal_{u}"
                )
        if st.button("LAGRE MÅL"):
            data["user_goals"] = updated_goals
            data["weekly_protein_goal"] = max(updated_goals.values()) if updated_goals else weekly_goal
            save_data(data)
            st.success("✓ Mål lagret")
            st.rerun()

    with tab2:
        st.markdown("**Legg til bruker**")
        new_user = st.text_input("Navn på ny bruker", key="new_user_input")
        if st.button("LEGG TIL BRUKER") and new_user.strip():
            name = new_user.strip()
            if name not in data["users"]:
                data["users"].append(name)
                data.setdefault("user_goals", {})[name] = weekly_goal
                save_data(data)
                st.success(f"✓ {name} lagt til")
                st.rerun()
            else:
                st.warning(f"{name} finnes allerede")

        st.markdown("<br>**Fjern bruker**", unsafe_allow_html=True)
        if len(data["users"]) > 1:
            remove_user = st.selectbox("Velg bruker å fjerne", data["users"], key="remove_user_select")
            if st.button("FJERN BRUKER"):
                data["users"].remove(remove_user)
                data.get("user_goals", {}).pop(remove_user, None)
                save_data(data)
                st.success(f"✓ {remove_user} fjernet")
                st.rerun()
        else:
            st.markdown("<p style='color:#aaa;font-size:12px;'>Må ha minst én bruker.</p>",
                        unsafe_allow_html=True)

    with tab3:
        st.markdown("**Tilbakestill data**")
        new_count = st.number_input("Nytt antall YT", min_value=1, max_value=500, value=30)
        if st.button("TILBAKESTILL"):
            data = {
                "start_date": str(today_d),
                "start_count": new_count,
                "current_count": new_count,
                "weekly_protein_goal": weekly_goal,
                "user_goals": {u: weekly_goal for u in data.get("users", [])},
                "log": [], "food_log": [],
                "users": data.get("users", ["Erik", "Trym"])
            }
            save_data(data)
            st.success(f"✓ Tilbakestilt til {new_count} YT")
            st.rerun()

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:48px;padding:20px 0;border-top:1px solid #d4cdc6;
            display:flex;justify-content:space-between;align-items:center;">
    <span style="font-family:'EB Garamond',serif;font-size:18px;letter-spacing:4px;
                 color:{NAVY};text-transform:uppercase;">FERD.</span>
    <span style="font-size:10px;letter-spacing:1.5px;color:#bbb;text-transform:uppercase;">
        Vi vil skape varige verdier og sette tydelige spor.
    </span>
</div>""", unsafe_allow_html=True)
