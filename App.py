import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

# Configurazione Dashboard "Hunter Mark-II"
st.set_page_config(page_title="V3 BAUM HUNTER MK2", layout="wide", page_icon="🛡️")

st.title("🛡️ V3 BAUM-HUNTER MK2: Analisi Regimi")

# 1. SIDEBAR - CONTROLLI E TEST
st.sidebar.header("⚙️ Opzioni di Analisi")
intervallo = "1d"
periodo = "60d"

if st.sidebar.button("⚡ Esegui Quick Test (1 Ora)"):
    intervallo = "1h"
    periodo = "7d"
    st.sidebar.warning("Analisi rapida attiva (Dati 1h). Maggiore sensibilità, minor sicurezza.")

# 2. LOGICA E ASSET
asset_class = {
    "BTC-USD": "🪙 CRYPTO", "ETH-USD": "🪙 CRYPTO", "SOL-USD": "🪙 CRYPTO",
    "GC=F": "🔱 FUTURE (ORO)", "ES=F": "🔱 FUTURE (S&P500)", "NQ=F": "🔱 FUTURE (NASDAQ)", "CL=F": "🔱 FUTURE (OIL)",
    "ENI.MI": "🇮🇹 AZIONE IT", "MAIRE.MI": "🇮🇹 AZIONE IT", "FER.MI": "🇮🇹 AZIONE IT", "UCG.MI": "🇮🇹 AZIONE IT",
    "AAPL": "🇺🇸 AZIONE US", "NVDA": "🇺🇸 AZIONE US", "MSFT": "🇺🇸 AZIONE US", "TSLA": "🇺🇸 AZIONE US", 
    "PLTR": "🇺🇸 AZIONE US", "RIVN": "🇺🇸 AZIONE US", "COIN": "🇺🇸 AZIONE US"
}

def baum_analysis(ticker, timeframe, span):
    try:
        data = yf.download(ticker, period=span, interval=timeframe, progress=False)
        if data.empty: return None
        p = data['Close'][ticker] if isinstance(data.columns, pd.MultiIndex) else data['Close']
        returns = p.pct_change().dropna()
        vol_short, vol_long = returns.tail(10).std(), returns.std()
        p00 = np.clip(1.0 - (vol_short / (vol_long * 2)), 0, 1)
        sma_20 = p.rolling(window=20).mean().iloc[-1]
        prezzo_attuale = float(p.iloc[-1])
        categoria = asset_class.get(ticker, "📈 AZIONE")
        return {"TICKER": ticker, "CATEGORIA": categoria, "PREZZO": round(prezzo_attuale, 2), "STABILITÀ": p00, "SOPRA_MEDIA": prezzo_attuale > sma_20}
    except: return None

# 3. SCANSIONE
gold_list, silver_list = [], []
for t in asset_class.keys():
    res = baum_analysis(t, intervallo, periodo)
    if res:
        if res["STABILITÀ"] > 0.75 and res["SOPRA_MEDIA"]:
            gold_list.append(res)
        elif res["STABILITÀ"] > 0.50:
            silver_list.append(res)

# --- RADAR DEI FINALISTI (TOP 3) ---
if silver_list:
    st.subheader(f"📡 Radar Finalisti (Basato su {intervallo})")
    sorted_silver = sorted(silver_list, key=lambda x: x['STABILITÀ'], reverse=True)[:3]
    cols = st.columns(3)
    for i, stock in enumerate(sorted_silver):
        with cols[i]:
            st.metric(label=f"{stock['CATEGORIA']} - {stock['TICKER']}", value=f"{stock['PREZZO']} $", delta=f"{round(stock['STABILITÀ']*100, 1)}% Stabilità")
            st.progress(stock['STABILITÀ'])

st.divider()

# Tabella Gold e Watchlist
col_left, col_right = st.columns([1, 1])
with col_left:
    st.subheader("🚀 OPPORTUNITÀ GOLD")
    if gold_list: st.table(pd.DataFrame(gold_list).drop(columns=["STABILITÀ", "SOPRA_MEDIA"]))
    else: st.info("🛡️ Nessun segnale Gold confermato.")

with col_right:
    st.subheader("📂 WATCHLIST")
    if silver_list: st.table(pd.DataFrame(silver_list).drop(columns=["SOPRA_MEDIA"]))

# Footer con Timestamp
st.divider()
now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
st.caption(f"🕒 Timeframe attuale: **{intervallo}** | Ultimo aggiornamento: {now}")



