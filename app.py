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

/* Knapper */
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
.stButton > button:hover {{
    background-color: {TEAL} !important;
}}

/* Select og inputs */
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

/* Expander */
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

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "start_date": str(date.today()),
        "start_count": 30,
        "current_count": 30,
        "weekly_protein_goal": 200,
        "log": [],
        "users": ["Erik", "Trym"]
    }

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

data = load_data()

# ── BEREGNINGER ───────────────────────────────────────────────────────────────
total_taken  = data["start_count"] - data["current_count"]
total_protein = total_taken * 20
days_elapsed = max((date.today() - date.fromisoformat(data["start_date"])).days + 1, 1)
avg_per_day  = round(total_taken / days_elapsed, 1)
days_left    = round(data["current_count"] / avg_per_day) if avg_per_day > 0 else "–"
pct_left     = round(data["current_count"] / data["start_count"] * 100)

today_d    = date.today()
week_start = today_d - timedelta(days=today_d.weekday())
week_log   = [e for e in data["log"]
              if e.get("flavor") != "påfyll"
              and date.fromisoformat(e["date"]) >= week_start]
week_protein = len(week_log) * 20
weekly_goal  = data.get("weekly_protein_goal", 200)
week_pct     = min(round(week_protein / weekly_goal * 100), 100)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{NAVY};padding:18px 32px 12px;margin-bottom:0;display:flex;
            justify-content:space-between;align-items:center;">
    <span style="font-family:'EB Garamond',serif;font-size:24px;font-weight:700;
                 letter-spacing:5px;color:{BEIGE};text-transform:uppercase;">
        FERD<span style="color:{TEAL}">.</span>
    </span>
    <span style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#7a90aa;">
        YT &middot; Kjøleskapstracker
    </span>
</div>
<div style="background:{NAVY};padding:20px 32px 28px;margin-bottom:32px;">
    <div style="font-family:'EB Garamond',serif;font-size:42px;font-weight:500;
                color:{BEIGE};line-height:1.1;margin-bottom:8px;">
        YT-oversikt &nbsp;<em style="color:{TEAL};font-style:italic;">Kjøleskap</em>
    </div>
    <div style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#7a90aa;">
        20g protein per enhet &nbsp;&middot;&nbsp; Sjokolade &nbsp;&middot;&nbsp; Banan/Jordbær
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

c1, c2, c3, c4 = st.columns(4)
warn_color = ORANGE if pct_left < 25 else NAVY

with c1:
    st.markdown(kpi_card("YT igjen", data["current_count"],
        f"av {data['start_count']} totalt", pct_left, warn_color),
        unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("Total protein", f"{total_protein}g",
        f"{total_taken} enheter · siden {data['start_date']}", 100, TEAL),
        unsafe_allow_html=True)
with c3:
    w_color = TEAL if week_pct >= 100 else NAVY
    st.markdown(kpi_card("Protein denne uken", f"{week_protein}g",
        f"mål {weekly_goal}g · {week_pct}% nådd", week_pct, w_color),
        unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("Holder til (est.)", str(days_left),
        f"dager · {avg_per_day} snitt/dag", 55, NAVY),
        unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if data["current_count"] == 0:
    st.error("🚨 Kjøleskapet er tomt – tid for påfyll!")
elif data["current_count"] <= 5:
    st.warning(f"⚠️ Kun {data['current_count']} YT igjen.")

st.markdown(f"<hr style='border:none;border-top:1px solid #d4cdc6;margin:24px 0'>",
            unsafe_allow_html=True)

# ── REGISTRER + STATISTIKK ────────────────────────────────────────────────────
col_l, col_r = st.columns([1, 1.6])

with col_l:
    st.markdown(f"""<div style="font-family:'EB Garamond',serif;font-size:22px;
        color:{NAVY};border-bottom:1px solid #d4cdc6;padding-bottom:10px;
        margin-bottom:20px;">Registrer inntak</div>""", unsafe_allow_html=True)

    user   = st.selectbox("Hvem er du?", data.get("users", ["Erik", "Trym"]))
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
                        "date": str(date.today()),
                        "time": datetime.now().strftime("%H:%M"),
                        "user": user,
                        "flavor": flavor,
                        "protein": 20
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
                "date": str(date.today()),
                "time": datetime.now().strftime("%H:%M"),
                "user": "System", "flavor": "påfyll", "protein": 0
            })
            save_data(data)
            st.session_state["show_refill"] = False
            st.success(f"✓ Lagt til {refill} YT. Nå: {data['current_count']}")
            st.rerun()

    st.markdown(f"<hr style='border:none;border-top:1px solid #d4cdc6;margin:20px 0'>",
                unsafe_allow_html=True)
    st.markdown(f"""<div style="font-family:'EB Garamond',serif;font-size:22px;
        color:{NAVY};border-bottom:1px solid #d4cdc6;padding-bottom:10px;
        margin-bottom:20px;">Smaksfordeling</div>""", unsafe_allow_html=True)

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
    st.markdown(f"""<div style="font-family:'EB Garamond',serif;font-size:22px;
        color:{NAVY};border-bottom:1px solid #d4cdc6;padding-bottom:10px;
        margin-bottom:20px;">Statistikk per person</div>""", unsafe_allow_html=True)

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

    if user_stats:
        max_t = max(s["total"] for s in user_stats.values()) or 1
        for uname, stats in sorted(user_stats.items(), key=lambda x: -x[1]["total"]):
            bw = round(stats["total"] / max_t * 100)
            st.markdown(f"""
            <div style="background:{BEIGE};border-left:4px solid {TEAL};
                        border-radius:2px;padding:16px 18px;margin-bottom:12px;">
                <div style="font-weight:600;font-size:15px;color:{NAVY};margin-bottom:8px;">
                    {uname}
                </div>
                <div style="background:#d4cdc6;height:3px;border-radius:2px;
                            overflow:hidden;margin-bottom:8px;">
                    <div style="width:{bw}%;height:100%;background:{TEAL};border-radius:2px;"></div>
                </div>
                <div style="font-size:11px;color:#777;">
                    {stats['total']} YT totalt &nbsp;·&nbsp;
                    {stats['protein']}g protein &nbsp;·&nbsp;
                    🍫 {stats['sjokolade']} &nbsp;·&nbsp;
                    🍌🍓 {stats['banan-jordbaer']}
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#aaa;font-size:13px;'>Ingen registreringer ennå.</p>",
                    unsafe_allow_html=True)

st.markdown(f"<hr style='border:none;border-top:1px solid #d4cdc6;margin:24px 0'>",
            unsafe_allow_html=True)

# ── GRAF ──────────────────────────────────────────────────────────────────────
st.markdown(f"""<div style="font-family:'EB Garamond',serif;font-size:22px;
    color:{NAVY};border-bottom:1px solid #d4cdc6;padding-bottom:10px;
    margin-bottom:20px;">Daglig forbruk – siste 14 dager</div>""", unsafe_allow_html=True)

chart_data = {}
for i in range(13, -1, -1):
    d = str(today_d - timedelta(days=i))
    chart_data[d] = {"Sjokolade": 0, "Banan/Jordbær": 0}

for e in data["log"]:
    d = e.get("date")
    f = e.get("flavor", "")
    if d in chart_data:
        if f == "sjokolade":
            chart_data[d]["Sjokolade"] += 1
        elif f == "banan-jordbaer":
            chart_data[d]["Banan/Jordbær"] += 1

df = pd.DataFrame.from_dict(chart_data, orient="index")
df.index = [d[5:] for d in df.index]
st.bar_chart(df, color=[CHOC, TEAL])

st.markdown(f"<hr style='border:none;border-top:1px solid #d4cdc6;margin:24px 0'>",
            unsafe_allow_html=True)

# ── LOGG ──────────────────────────────────────────────────────────────────────
st.markdown(f"""<div style="font-family:'EB Garamond',serif;font-size:22px;
    color:{NAVY};border-bottom:1px solid #d4cdc6;padding-bottom:10px;
    margin-bottom:20px;">Siste registreringer</div>""", unsafe_allow_html=True)

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
                    display:flex;justify-content:space-between;align-items:center;
                    font-size:13px;">
            <div>
                <strong style="color:{NAVY};">{e.get('user','–')}</strong>
                <span style="color:#bbb;font-size:11px;margin-left:10px;">
                    {e['date']} · {e.get('time','–')}
                </span>
            </div>
            <div style="display:flex;gap:12px;align-items:center;">
                <span style="background:{bg_b};color:{col_b};padding:2px 10px;
                             border-radius:2px;font-size:10px;font-weight:700;
                             letter-spacing:1px;text-transform:uppercase;">{label}</span>
                <span style="font-size:11px;color:#aaa;">+20g protein</span>
            </div>
        </div>""", unsafe_allow_html=True)
else:
    st.markdown("<p style='color:#aaa;font-size:13px;'>Ingen registreringer ennå.</p>",
                unsafe_allow_html=True)

st.markdown(f"<hr style='border:none;border-top:1px solid #d4cdc6;margin:24px 0'>",
            unsafe_allow_html=True)

# ── INNSTILLINGER ─────────────────────────────────────────────────────────────
with st.expander("⚙️  Innstillinger"):
    s1, s2 = st.columns(2)
    with s1:
        st.markdown("**Ukentlig proteinmål**")
        new_goal = st.number_input("Gram protein per uke", min_value=20,
                                   max_value=2000, value=weekly_goal, step=20)
        if st.button("LAGRE MÅL"):
            data["weekly_protein_goal"] = new_goal
            save_data(data)
            st.success("✓ Mål lagret")
            st.rerun()
    with s2:
        st.markdown("**Tilbakestill data**")
        new_count = st.number_input("Nytt antall YT", min_value=1, max_value=500, value=30)
        if st.button("TILBAKESTILL"):
            data = {
                "start_date": str(date.today()),
                "start_count": new_count,
                "current_count": new_count,
                "weekly_protein_goal": weekly_goal,
                "log": [],
                "users": ["Erik", "Trym"]
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
