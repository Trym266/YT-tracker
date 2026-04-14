import streamlit as st
import json
import os
from datetime import date, datetime

st.set_page_config(
    page_title="🍺 Kjøleskapet",
    page_icon="🍺",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Mono', monospace;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
}

.stApp {
    background-color: #0a0a0f;
    color: #f0ede6;
}

.big-number {
    font-family: 'Syne', sans-serif;
    font-size: 96px;
    font-weight: 800;
    color: #f5c542;
    line-height: 1;
    text-align: center;
    letter-spacing: -3px;
    margin: 0;
}

.unit-label {
    font-family: 'Space Mono', monospace;
    font-size: 14px;
    color: #888;
    text-align: center;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 32px;
}

.status-box {
    background: #13131a;
    border: 1px solid #2a2a3a;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
}

.log-entry {
    background: #13131a;
    border-left: 3px solid #f5c542;
    padding: 10px 16px;
    margin-bottom: 8px;
    border-radius: 0 8px 8px 0;
    font-size: 13px;
    color: #aaa;
}

.progress-bar-bg {
    background: #1e1e2e;
    border-radius: 100px;
    height: 12px;
    margin: 12px 0;
    overflow: hidden;
}

.progress-bar-fill {
    height: 100%;
    border-radius: 100px;
    transition: width 0.4s ease;
}

.stButton > button {
    background-color: #f5c542 !important;
    color: #0a0a0f !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 28px !important;
    font-size: 14px !important;
    letter-spacing: 1px !important;
    width: 100% !important;
}

.stButton > button:hover {
    background-color: #ffd966 !important;
}

.stNumberInput > div > div > input {
    background-color: #13131a !important;
    color: #f0ede6 !important;
    border: 1px solid #2a2a3a !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
}

.stSlider > div > div > div > div {
    background-color: #f5c542 !important;
}

hr {
    border-color: #2a2a3a !important;
}
</style>
""", unsafe_allow_html=True)

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "start_date": str(date.today()),
        "start_count": 30,
        "current_count": 30,
        "log": []
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()

st.markdown("# 🍺 Kjøleskapet")
st.markdown("---")

pct = data["current_count"] / data["start_count"]
bar_color = "#f5c542" if pct > 0.4 else "#f57c42" if pct > 0.2 else "#f54242"
pct_display = round(pct * 100)

st.markdown(f'<div class="big-number">{data["current_count"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="unit-label">øl igjen av {data["start_count"]}</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="progress-bar-bg">
    <div class="progress-bar-fill" style="width:{pct_display}%; background:{bar_color};"></div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class="status-box">
        <div style="font-size:11px;color:#888;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px">Startdato</div>
        <div style="font-size:14px;font-weight:700">{data['start_date']}</div>
    </div>""", unsafe_allow_html=True)

with col2:
    days_elapsed = (date.today() - date.fromisoformat(data["start_date"])).days + 1
    taken = data["start_count"] - data["current_count"]
    avg = round(taken / days_elapsed, 1) if days_elapsed > 0 else 0
    st.markdown(f"""<div class="status-box">
        <div style="font-size:11px;color:#888;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px">Snitt/dag</div>
        <div style="font-size:14px;font-weight:700">{avg} øl</div>
    </div>""", unsafe_allow_html=True)

with col3:
    days_left = round(data["current_count"] / avg) if avg > 0 else "∞"
    st.markdown(f"""<div class="status-box">
        <div style="font-size:11px;color:#888;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px">Holder til</div>
        <div style="font-size:14px;font-weight:700">{days_left} dager</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### Registrer dagens forbruk")

amount = st.number_input("Antall øl tatt i dag", min_value=1, max_value=data["current_count"] if data["current_count"] > 0 else 1, value=1, step=1)

if st.button("REGISTRER →"):
    if data["current_count"] >= amount:
        data["current_count"] -= amount
        log_entry = {
            "date": str(date.today()),
            "time": datetime.now().strftime("%H:%M"),
            "amount": amount,
            "remaining": data["current_count"]
        }
        data["log"].insert(0, log_entry)
        save_data(data)
        st.success(f"✓ Registrert {amount} øl. {data['current_count']} igjen.")
        st.rerun()
    else:
        st.error("Ikke nok øl igjen!")

if data["current_count"] == 0:
    st.error("🚨 Kjøleskapet er tomt! Tid for påfyll.")
elif data["current_count"] <= 5:
    st.warning(f"⚠️ Kun {data['current_count']} øl igjen – snart tomt!")

if data["log"]:
    st.markdown("---")
    st.markdown("### Logg")
    for entry in data["log"][:10]:
        st.markdown(f"""<div class="log-entry">
            📅 <strong>{entry['date']}</strong> kl. {entry['time']} &nbsp;—&nbsp; tok <strong>{entry['amount']} øl</strong> &nbsp;·&nbsp; {entry['remaining']} igjen
        </div>""", unsafe_allow_html=True)

with st.expander("⚙️ Tilbakestill"):
    new_count = st.number_input("Sett nytt antall øl i kjøleskapet", min_value=1, max_value=500, value=30)
    if st.button("TILBAKESTILL"):
        data = {
            "start_date": str(date.today()),
            "start_count": new_count,
            "current_count": new_count,
            "log": []
        }
        save_data(data)
        st.success(f"✓ Tilbakestilt til {new_count} øl fra i dag.")
        st.rerun()
