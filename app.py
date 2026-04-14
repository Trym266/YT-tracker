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

# ─── FERD DESIGN ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif !important; }

.stApp { background-color: #f5f5f3 !important; }

.ferd-header {
    background-color: #1a1a1a;
    color: #fff;
    padding: 20px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
    border-radius: 4px;
}
.ferd-logo { font-size: 20px; font-weight: 700; letter-spacing: 4px; color: #fff; text-transform: uppercase; }
.ferd-logo span { color: #c8102e; }
.ferd-subtitle { font-size: 11px; color: #999; letter-spacing: 2px; text-transform: uppercase; margin-top: 2px; }

.kpi-card {
    background: #fff;
    border: 1px solid #e8e8e8;
    border-top: 3px solid #c8102e;
    border-radius: 4px;
    padding: 22px 24px;
    margin-bottom: 16px;
}
.kpi-label { font-size: 10px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: #999; margin-bottom: 6px; }
.kpi-value { font-size: 40px; font-weight: 700; color: #1a1a1a; line-height: 1; }
.kpi-unit { font-size: 12px; color: #999; margin-top: 4px; }

.prog-bg { background: #f0f0f0; border-radius: 2px; height: 6px; margin: 10px 0 3px; overflow: hidden; }
.prog-fill { height: 100%; border-radius: 2px; background: #c8102e; }
.prog-green { background: #2d7a2d !important; }

.section-title {
    font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;
    color: #1a1a1a; border-bottom: 2px solid #1a1a1a; padding-bottom: 8px; margin-bottom: 18px;
}

.log-row {
    background: #fff; border: 1px solid #f0f0f0; border-left: 3px solid #c8102e;
    padding: 11px 16px; margin-bottom: 6px; border-radius: 0 4px 4px 0;
    font-size: 13px; display: flex; justify-content: space-between; align-items: center;
}

.flavor-badge {
    display: inline-block; padding: 2px 10px; border-radius: 2px;
    font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
}
.badge-sjokolade { background: #f5ede8; color: #5c3317; }
.badge-banan     { background: #fef9e6; color: #a07000; }
.badge-jordbær   { background: #fce8ec; color: #9e1030; }

.stButton > button {
    background-color: #1a1a1a !important; color: #fff !important;
    font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
    font-size: 11px !important; letter-spacing: 2px !important; text-transform: uppercase !important;
    border: none !important; border-radius: 2px !important; padding: 13px 24px !important; width: 100% !important;
}
.stButton > button:hover { background-color: #c8102e !important; }

.block-container { padding-top: 0 !important; max-width: 1200px !important; }
#MainMenu, footer, header { visibility: hidden; }
hr { border: none; border-top: 1px solid #e8e8e8; margin: 24px 0; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────────────────────
DATA_FILE = "yt_data.json"

FLAVORS = {
    "Sjokolade 🍫": "sjokolade",
    "Banan 🍌": "banan",
    "Jordbær 🍓": "jordbær"
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
        "users": ["Magnus", "Kari", "Ole"]
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

data = load_data()

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ferd-header">
    <div>
        <div class="ferd-logo">FERD<span>.</span></div>
        <div class="ferd-subtitle">YT Tracker – Kjøleskapsoversikt</div>
    </div>
    <div style="color:#888;font-size:11px;letter-spacing:1px;text-align:right">
        20g protein per enhet<br>
        <span style="color:#666">Sjokolade · Banan · Jordbær</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── BEREGNINGER ──────────────────────────────────────────────────────────────
total_taken = data["start_count"] - data["current_count"]
total_protein = total_taken * 20
days_elapsed = max((date.today() - date.fromisoformat(data["start_date"])).days + 1, 1)
avg_per_day = round(total_taken / days_elapsed, 1)
days_left_est = round(data["current_count"] / avg_per_day) if avg_per_day > 0 else "–"

today = date.today()
week_start = today - timedelta(days=today.weekday())
week_log = [e for e in data["log"] if e.get("flavor") != "påfyll" and date.fromisoformat(e["date"]) >= week_start]
week_protein = len(week_log) * 20
weekly_goal = data.get("weekly_protein_goal", 200)
week_pct = min(round(week_protein / weekly_goal * 100), 100)

# ─── KPI-RAD ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    pct = round(data["current_count"] / data["start_count"] * 100)
    color = "#c8102e" if pct < 25 else "#1a1a1a"
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">YT igjen</div>
        <div class="kpi-value" style="color:{color}">{data['current_count']}</div>
        <div class="kpi-unit">av {data['start_count']} totalt</div>
        <div class="prog-bg"><div class="prog-fill" style="width:{pct}%"></div></div>
        <div style="font-size:11px;color:#bbb">{pct}% gjenstår</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Total protein</div>
        <div class="kpi-value">{total_protein}g</div>
        <div class="kpi-unit">{total_taken} enheter totalt</div>
        <div class="prog-bg"><div class="prog-fill prog-green" style="width:100%"></div></div>
        <div style="font-size:11px;color:#bbb">Siden {data['start_date']}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    bar_class = "prog-green" if week_pct >= 100 else ""
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Protein denne uken</div>
        <div class="kpi-value">{week_protein}g</div>
        <div class="kpi-unit">mål {weekly_goal}g · {week_pct}%</div>
        <div class="prog-bg"><div class="prog-fill {bar_class}" style="width:{week_pct}%"></div></div>
        <div style="font-size:11px;color:#bbb">{len(week_log)} YT registrert</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Holder til (est.)</div>
        <div class="kpi-value">{days_left_est}</div>
        <div class="kpi-unit">dager · {avg_per_day} snitt/dag</div>
        <div class="prog-bg"><div class="prog-fill" style="width:50%"></div></div>
        <div style="font-size:11px;color:#bbb">Startet {data['start_date']}</div>
    </div>""", unsafe_allow_html=True)

if data["current_count"] == 0:
    st.error("🚨 Kjøleskapet er tomt! Tid for påfyll.")
elif data["current_count"] <= 5:
    st.warning(f"⚠️ Kun {data['current_count']} YT igjen – snart tomt!")

st.markdown("<hr>", unsafe_allow_html=True)

# ─── REGISTRER + STATISTIKK ───────────────────────────────────────────────────
left, right = st.columns([1, 1.6])

with left:
    st.markdown('<div class="section-title">Registrer inntak</div>', unsafe_allow_html=True)

    user_list = data.get("users", ["Magnus", "Kari", "Ole"])
    user = st.selectbox("Hvem er du?", user_list)
    flavor_display = st.selectbox("Smak", list(FLAVORS.keys()))
    flavor = FLAVORS[flavor_display]
    amount = st.number_input("Antall YT", min_value=1, max_value=max(data["current_count"], 1), value=1, step=1)

    col_a, col_b = st.columns(2)
    with col_a:
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
                st.success(f"✓ {user}: {amount}× {flavor_display}. {data['current_count']} igjen.")
                st.rerun()
            else:
                st.error("Ikke nok YT igjen!")

    with col_b:
        if st.button("PÅFYLL +"):
            st.session_state["show_refill"] = not st.session_state.get("show_refill", False)

    if st.session_state.get("show_refill"):
        refill = st.number_input("Antall å legge til", min_value=1, max_value=200, value=30)
        if st.button("BEKREFT PÅFYLL"):
            data["current_count"] += refill
            data["log"].insert(0, {
                "date": str(date.today()),
                "time": datetime.now().strftime("%H:%M"),
                "user": "System",
                "flavor": "påfyll",
                "protein": 0
            })
            save_data(data)
            st.session_state["show_refill"] = False
            st.success(f"✓ Lagt til {refill} YT. Nå: {data['current_count']}")
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Smaksfordeling</div>', unsafe_allow_html=True)

    flavor_counts = {"sjokolade": 0, "banan": 0, "jordbær": 0}
    for e in data["log"]:
        if e.get("flavor") in flavor_counts:
            flavor_counts[e["flavor"]] += 1

    total_f = sum(flavor_counts.values()) or 1
    flavor_colors = {"sjokolade": "#5c3317", "banan": "#f0a500", "jordbær": "#c8102e"}
    flavor_emoji  = {"sjokolade": "🍫", "banan": "🍌", "jordbær": "🍓"}

    for fname, count in flavor_counts.items():
        pct_f = round(count / total_f * 100)
        st.markdown(f"""
        <div style="margin-bottom:14px">
            <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
                <span>{flavor_emoji[fname]} {fname.capitalize()}</span>
                <span style="color:#999">{count} stk · {pct_f}%</span>
            </div>
            <div class="prog-bg"><div class="prog-fill" style="width:{pct_f}%;background:{flavor_colors[fname]}"></div></div>
        </div>
        """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-title">Statistikk per person</div>', unsafe_allow_html=True)

    user_stats = {}
    for e in data["log"]:
        u = e.get("user", "Ukjent")
        if u == "System":
            continue
        if u not in user_stats:
            user_stats[u] = {"total": 0, "sjokolade": 0, "banan": 0, "jordbær": 0, "protein": 0}
        user_stats[u]["total"] += 1
        f = e.get("flavor", "")
        if f in user_stats[u]:
            user_stats[u][f] += 1
        user_stats[u]["protein"] += 20

    if user_stats:
        max_total = max(s["total"] for s in user_stats.values()) or 1
        for uname, stats in sorted(user_stats.items(), key=lambda x: -x[1]["total"]):
            bar_w = round(stats["total"] / max_total * 100)
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #e8e8e8;border-radius:4px;padding:16px 20px;margin-bottom:10px">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                    <div style="font-weight:600;font-size:14px">{uname}</div>
                    <div style="font-size:12px;color:#999">{stats['total']} YT &nbsp;·&nbsp; {stats['protein']}g protein</div>
                </div>
                <div class="prog-bg"><div class="prog-fill" style="width:{bar_w}%"></div></div>
                <div style="font-size:11px;color:#bbb;margin-top:6px">
                    🍫 {stats['sjokolade']} &nbsp;·&nbsp; 🍌 {stats['banan']} &nbsp;·&nbsp; 🍓 {stats['jordbær']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#bbb;font-size:13px'>Ingen registreringer ennå.</p>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─── GRAF – SISTE 14 DAGER ────────────────────────────────────────────────────
st.markdown('<div class="section-title">Daglig forbruk – siste 14 dager</div>', unsafe_allow_html=True)

chart_data = {}
for i in range(13, -1, -1):
    d = str(today - timedelta(days=i))
    chart_data[d] = {"Sjokolade": 0, "Banan": 0, "Jordbær": 0}

for e in data["log"]:
    d = e.get("date")
    f = e.get("flavor", "")
    if d in chart_data:
        key = f.capitalize() if f in ["sjokolade", "banan", "jordbær"] else None
        if key:
            chart_data[d][key] += 1

df = pd.DataFrame.from_dict(chart_data, orient="index")
df.index = [d[5:] for d in df.index]  # MM-DD format
st.bar_chart(df, color=["#5c3317", "#f0a500", "#c8102e"])

st.markdown("<hr>", unsafe_allow_html=True)

# ─── LOGG ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Siste 20 registreringer</div>', unsafe_allow_html=True)

visible_log = [e for e in data["log"] if e.get("flavor") != "påfyll"][:20]

if visible_log:
    for e in visible_log:
        f = e.get("flavor", "")
        border = {"sjokolade": "#5c3317", "banan": "#f0a500", "jordbær": "#c8102e"}.get(f, "#ccc")
        emoji  = {"sjokolade": "🍫", "banan": "🍌", "jordbær": "🍓"}.get(f, "")
        st.markdown(f"""
        <div class="log-row" style="border-left-color:{border}">
            <div>
                <strong>{e.get('user','–')}</strong>
                <span style="color:#bbb;font-size:12px;margin-left:10px">{e['date']} kl. {e.get('time','–')}</span>
            </div>
            <div style="display:flex;gap:12px;align-items:center">
                <span class="flavor-badge badge-{f}">{emoji} {f.capitalize()}</span>
                <span style="font-size:12px;color:#999">+20g protein</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<p style='color:#bbb;font-size:13px'>Ingen registreringer ennå.</p>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─── INNSTILLINGER ────────────────────────────────────────────────────────────
with st.expander("⚙️  Innstillinger"):
    s1, s2, s3 = st.columns(3)

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
        st.markdown("**Brukere**")
        current_users = ", ".join(data.get("users", []))
        new_users_str = st.text_input("Navn (kommaseparert)", value=current_users)
        if st.button("LAGRE BRUKERE"):
            data["users"] = [u.strip() for u in new_users_str.split(",") if u.strip()]
            save_data(data)
            st.success("✓ Brukere oppdatert")
            st.rerun()

    with s3:
        st.markdown("**Tilbakestill data**")
        new_count = st.number_input("Nytt antall YT", min_value=1, max_value=500, value=30)
        if st.button("TILBAKESTILL"):
            data = {
                "start_date": str(date.today()),
                "start_count": new_count,
                "current_count": new_count,
                "weekly_protein_goal": data.get("weekly_protein_goal", 200),
                "log": [],
                "users": data.get("users", ["Magnus", "Kari", "Ole"])
            }
            save_data(data)
            st.success(f"✓ Tilbakestilt til {new_count} YT")
            st.rerun()
