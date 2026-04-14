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

# ─── FERD DESIGN SYSTEM ───────────────────────────────────────────────────────
# Farger hentet direkte fra Ferd Konsern-presentasjon og merkevareprofil:
# Marineblå #1F2E4B · Beige #EFE7E0 · Teal #3B756A · Hvit #FFFFFF · Mørk tekst #1a1a1a

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap');

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #EFE7E0 !important;
}

.stApp { background-color: #EFE7E0 !important; }

/* ── Topplinje ── */
.ferd-topbar {
    background: #1F2E4B;
    padding: 0 40px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0;
}
.ferd-wordmark {
    font-family: 'EB Garamond', serif;
    font-size: 26px;
    font-weight: 600;
    letter-spacing: 5px;
    color: #EFE7E0;
    text-transform: uppercase;
}
.ferd-wordmark em { color: #3B756A; font-style: normal; }
.ferd-topbar-right {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #8fa0b8;
}

/* ── Hero-stripe ── */
.ferd-hero {
    background: #1F2E4B;
    padding: 36px 40px 32px;
    margin-bottom: 32px;
}
.ferd-hero-title {
    font-family: 'EB Garamond', serif;
    font-size: 48px;
    font-weight: 400;
    color: #EFE7E0;
    line-height: 1.1;
    margin: 0 0 6px;
}
.ferd-hero-title em {
    font-style: italic;
    color: #3B756A;
}
.ferd-hero-sub {
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #7a90aa;
    margin: 0;
}

/* ── KPI-kort ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}
.kpi-card {
    background: #ffffff;
    border-radius: 2px;
    padding: 24px 22px 20px;
    border-top: 4px solid #1F2E4B;
    position: relative;
    overflow: hidden;
}
.kpi-card.teal { border-top-color: #3B756A; }
.kpi-card.warn  { border-top-color: #C8532A; }
.kpi-label {
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #8a8a8a;
    margin-bottom: 10px;
}
.kpi-number {
    font-family: 'EB Garamond', serif;
    font-size: 52px;
    font-weight: 600;
    color: #1F2E4B;
    line-height: 1;
    margin-bottom: 4px;
}
.kpi-number.teal { color: #3B756A; }
.kpi-number.warn  { color: #C8532A; }
.kpi-unit {
    font-size: 11px;
    color: #aaa;
    margin-bottom: 14px;
}
.kpi-bar-bg {
    background: #EFE7E0;
    height: 3px;
    border-radius: 2px;
    overflow: hidden;
}
.kpi-bar-fill {
    height: 100%;
    border-radius: 2px;
    background: #1F2E4B;
    transition: width .5s ease;
}
.kpi-bar-fill.teal { background: #3B756A; }
.kpi-bar-fill.warn  { background: #C8532A; }

/* ── Seksjonsoverskrift ── */
.sec-head {
    font-family: 'EB Garamond', serif;
    font-size: 22px;
    font-weight: 400;
    color: #1F2E4B;
    margin: 0 0 18px;
    padding-bottom: 10px;
    border-bottom: 1px solid #d4cdc6;
}

/* ── Panel (hvit boks) ── */
.panel {
    background: #ffffff;
    border-radius: 2px;
    padding: 28px 26px;
    margin-bottom: 20px;
}

/* ── Smaksbar ── */
.flavor-row {
    margin-bottom: 16px;
}
.flavor-meta {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #555;
    margin-bottom: 5px;
}
.flavor-name { font-weight: 600; color: #1F2E4B; }

/* ── Person-kort ── */
.person-card {
    background: #EFE7E0;
    border-radius: 2px;
    padding: 16px 18px;
    margin-bottom: 10px;
    border-left: 4px solid #3B756A;
}
.person-name { font-weight: 600; font-size: 14px; color: #1F2E4B; margin-bottom: 6px; }
.person-stats { font-size: 11px; color: #777; }

/* ── Logg-rad ── */
.log-row {
    background: #fff;
    border-left: 3px solid #3B756A;
    padding: 11px 16px;
    margin-bottom: 6px;
    border-radius: 0 2px 2px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
}
.log-row.choc { border-left-color: #5C3317; }

/* ── Badge ── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 2px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-sjokolade { background: #f0e8e2; color: #5C3317; }
.badge-banan-jordbaer { background: #e4f0ee; color: #2a5e54; }

/* ── Knapper ── */
.stButton > button {
    background-color: #1F2E4B !important;
    color: #EFE7E0 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 13px 20px !important;
    width: 100% !important;
    transition: background .2s !important;
}
.stButton > button:hover { background-color: #3B756A !important; }

/* ── Inputs ── */
div[data-baseweb="select"] > div {
    background: #fff !important;
    border: 1px solid #ccc7c0 !important;
    border-radius: 2px !important;
}
.stNumberInput > div > div > input,
.stTextInput > div > div > input {
    background: #fff !important;
    border: 1px solid #ccc7c0 !important;
    border-radius: 2px !important;
    color: #1F2E4B !important;
}
label { color: #444 !important; font-size: 12px !important; font-weight: 500 !important; }

/* ── Layout ── */
.block-container { padding-top: 0 !important; max-width: 1200px !important; }
#MainMenu, footer, header { visibility: hidden; }

.divider { border: none; border-top: 1px solid #d4cdc6; margin: 28px 0; }

/* ── Varseltekst ── */
.stAlert { border-radius: 2px !important; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────────────────────
DATA_FILE = "yt_data.json"

FLAVORS = {
    "Sjokolade 🍫": "sjokolade",
    "Banan/Jordbær 🍌🍓": "banan-jordbaer"
}

USERS = ["Erik", "Trym"]

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

# ─── TOPPLINJE ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ferd-topbar">
    <div class="ferd-wordmark">FERD<em>.</em></div>
    <div class="ferd-topbar-right">YT · Kjøleskapstracker</div>
</div>
<div class="ferd-hero">
    <p class="ferd-hero-title">YT-oversikt<br><em>Kjøleskap</em></p>
    <p class="ferd-hero-sub">20g protein per enhet &nbsp;·&nbsp; Sjokolade &nbsp;·&nbsp; Banan/Jordbær</p>
</div>
""", unsafe_allow_html=True)

# ─── BEREGNINGER ──────────────────────────────────────────────────────────────
total_taken = data["start_count"] - data["current_count"]
total_protein = total_taken * 20
days_elapsed = max((date.today() - date.fromisoformat(data["start_date"])).days + 1, 1)
avg_per_day = round(total_taken / days_elapsed, 1)
days_left_est = round(data["current_count"] / avg_per_day) if avg_per_day > 0 else "–"

today_d = date.today()
week_start = today_d - timedelta(days=today_d.weekday())
week_log = [e for e in data["log"] if e.get("flavor") != "påfyll"
            and date.fromisoformat(e["date"]) >= week_start]
week_protein = len(week_log) * 20
weekly_goal = data.get("weekly_protein_goal", 200)
week_pct = min(round(week_protein / weekly_goal * 100), 100)
pct_left = round(data["current_count"] / data["start_count"] * 100)

# ─── KPI-KORT ─────────────────────────────────────────────────────────────────
warn_class = "warn" if pct_left < 25 else ""

st.markdown(f"""
<div class="kpi-grid">

    <div class="kpi-card {warn_class}">
        <div class="kpi-label">YT igjen</div>
        <div class="kpi-number {warn_class}">{data['current_count']}</div>
        <div class="kpi-unit">av {data['start_count']} totalt</div>
        <div class="kpi-bar-bg"><div class="kpi-bar-fill {warn_class}" style="width:{pct_left}%"></div></div>
    </div>

    <div class="kpi-card teal">
        <div class="kpi-label">Total protein</div>
        <div class="kpi-number teal">{total_protein}<span style="font-size:22px;color:#aaa"> g</span></div>
        <div class="kpi-unit">{total_taken} enheter · siden {data['start_date']}</div>
        <div class="kpi-bar-bg"><div class="kpi-bar-fill teal" style="width:100%"></div></div>
    </div>

    <div class="kpi-card {'teal' if week_pct >= 100 else ''}">
        <div class="kpi-label">Protein denne uken</div>
        <div class="kpi-number {'teal' if week_pct >= 100 else ''}">{week_protein}<span style="font-size:22px;color:#aaa"> g</span></div>
        <div class="kpi-unit">mål {weekly_goal}g &nbsp;·&nbsp; {week_pct}% nådd</div>
        <div class="kpi-bar-bg"><div class="kpi-bar-fill {'teal' if week_pct >= 100 else ''}" style="width:{week_pct}%"></div></div>
    </div>

    <div class="kpi-card">
        <div class="kpi-label">Holder til (est.)</div>
        <div class="kpi-number">{days_left_est}</div>
        <div class="kpi-unit">dager &nbsp;·&nbsp; {avg_per_day} snitt/dag</div>
        <div class="kpi-bar-bg"><div class="kpi-bar-fill" style="width:55%"></div></div>
    </div>

</div>
""", unsafe_allow_html=True)

if data["current_count"] == 0:
    st.error("🚨 Kjøleskapet er tomt – tid for påfyll!")
elif data["current_count"] <= 5:
    st.warning(f"⚠️ Kun {data['current_count']} YT igjen.")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─── REGISTRERING + STATISTIKK ────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1.65])

with col_left:
    st.markdown('<div class="sec-head">Registrer inntak</div>', unsafe_allow_html=True)

    user = st.selectbox("Hvem er du?", USERS)
    flavor_display = st.selectbox("Smak", list(FLAVORS.keys()))
    flavor = FLAVORS[flavor_display]
    amount = st.number_input("Antall YT", min_value=1,
        max_value=max(data["current_count"], 1), value=1, step=1)

    protein_preview = amount * 20
    st.markdown(f"""
    <div style="background:#EFE7E0;border-radius:2px;padding:10px 14px;margin:4px 0 16px;font-size:12px;color:#555">
        💪 Dette gir <strong style="color:#3B756A">{protein_preview}g protein</strong>
    </div>
    """, unsafe_allow_html=True)

    btn1, btn2 = st.columns(2)
    with btn1:
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
    with btn2:
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

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="sec-head">Smaksfordeling</div>', unsafe_allow_html=True)

    flavor_counts = {"sjokolade": 0, "banan-jordbaer": 0}
    for e in data["log"]:
        f = e.get("flavor", "")
        if f in flavor_counts:
            flavor_counts[f] += 1

    total_f = sum(flavor_counts.values()) or 1
    flavor_cfg = {
        "sjokolade":     {"label": "Sjokolade 🍫",      "color": "#5C3317"},
        "banan-jordbaer":{"label": "Banan/Jordbær 🍌🍓", "color": "#3B756A"},
    }
    for fkey, cnt in flavor_counts.items():
        pct_f = round(cnt / total_f * 100)
        cfg = flavor_cfg[fkey]
        st.markdown(f"""
        <div class="flavor-row">
            <div class="flavor-meta">
                <span class="flavor-name">{cfg['label']}</span>
                <span>{cnt} stk · {pct_f}%</span>
            </div>
            <div class="kpi-bar-bg">
                <div class="kpi-bar-fill" style="width:{pct_f}%;background:{cfg['color']}"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="sec-head">Statistikk per person</div>', unsafe_allow_html=True)

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
            bar_w = round(stats["total"] / max_t * 100)
            st.markdown(f"""
            <div class="person-card">
                <div class="person-name">{uname}</div>
                <div class="kpi-bar-bg" style="margin-bottom:8px">
                    <div class="kpi-bar-fill teal" style="width:{bar_w}%"></div>
                </div>
                <div class="person-stats">
                    {stats['total']} YT totalt &nbsp;·&nbsp;
                    {stats['protein']}g protein &nbsp;·&nbsp;
                    🍫 {stats['sjokolade']} sjokolade &nbsp;·&nbsp;
                    🍌🍓 {stats['banan-jordbaer']} banan/jordbær
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#aaa;font-size:13px'>Ingen registreringer ennå.</p>",
                    unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─── GRAF ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-head">Daglig forbruk – siste 14 dager</div>', unsafe_allow_html=True)

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
st.bar_chart(df, color=["#5C3317", "#3B756A"])

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─── LOGG ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-head">Siste registreringer</div>', unsafe_allow_html=True)

visible = [e for e in data["log"] if e.get("flavor") != "påfyll"][:20]

if visible:
    for e in visible:
        f = e.get("flavor", "")
        is_choc = f == "sjokolade"
        badge_class = "badge-sjokolade" if is_choc else "badge-banan-jordbaer"
        label = "Sjokolade 🍫" if is_choc else "Banan/Jordbær 🍌🍓"
        row_class = "log-row choc" if is_choc else "log-row"
        st.markdown(f"""
        <div class="{row_class}">
            <div>
                <strong style="color:#1F2E4B">{e.get('user','–')}</strong>
                <span style="color:#bbb;font-size:11px;margin-left:10px">
                    {e['date']} · {e.get('time','–')}
                </span>
            </div>
            <div style="display:flex;gap:12px;align-items:center">
                <span class="badge {badge_class}">{label}</span>
                <span style="font-size:11px;color:#aaa">+20g protein</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<p style='color:#aaa;font-size:13px'>Ingen registreringer ennå.</p>",
                unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─── INNSTILLINGER ────────────────────────────────────────────────────────────
with st.expander("⚙️  Innstillinger"):
    s1, s2 = st.columns(2)

    with s1:
        st.markdown("**Ukentlig proteinmål**")
        new_goal = st.number_input("Gram protein per uke", min_value=20, max_value=2000,
            value=data.get("weekly_protein_goal", 200), step=20)
        if st.button("LAGRE MÅL"):
            data["weekly_protein_goal"] = new_goal
            save_data(data)
            st.success("✓ Mål lagret")
            st.rerun()

    with s2:
        st.markdown("**Tilbakestill data**")
        new_count = st.number_input("Nytt antall YT i kjøleskap", min_value=1, max_value=500, value=30)
        if st.button("TILBAKESTILL"):
            data = {
                "start_date": str(date.today()),
                "start_count": new_count,
                "current_count": new_count,
                "weekly_protein_goal": data.get("weekly_protein_goal", 200),
                "log": [],
                "users": ["Erik", "Trym"]
            }
            save_data(data)
            st.success(f"✓ Tilbakestilt til {new_count} YT fra i dag")
            st.rerun()

# ─── BUNNTEKST ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:48px;padding:20px 0;border-top:1px solid #d4cdc6;
    display:flex;justify-content:space-between;align-items:center">
    <div style="font-family:'EB Garamond',serif;font-size:18px;
        letter-spacing:4px;color:#1F2E4B;text-transform:uppercase">FERD.</div>
    <div style="font-size:10px;letter-spacing:2px;color:#bbb;text-transform:uppercase">
        Vi vil skape varige verdier og sette tydelige spor.
    </div>
</div>
""", unsafe_allow_html=True)
