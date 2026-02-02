import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="V3 BAUM HUNTER", layout="wide", page_icon="🎯")
st.title("🎯 V3 BAUM-HUNTER: Scansione Regimi")

# --- DATABASE ASSET ---
asset_class = {
    "BTC-USD": "🪙 CRYPTO", "ETH-USD": "🪙 CRYPTO", "SOL-USD": "🪙 CRYPTO",
    "GC=F": "🔱 FUTURE (ORO)", "ES=F": "🔱 FUTURE (S&P500)", "NQ=F": "🔱 FUTURE (NASDAQ)",
    "AAPL": "🇺🇸 AZIONE US", "NVDA": "🇺🇸 AZIONE US", "MSFT": "🇺🇸 AZIONE US", 
    "TSLA": "🇺🇸 AZIONE US", "PLTR": "🇺🇸 AZIONE US", "RIVN": "🇺🇸 AZIONE US", "COIN": "🇺🇸 AZIONE US",
    "ENI.MI": "🇮🇹 AZIONE IT", "MAIRE.MI": "🇮🇹 AZIONE IT", "UCG.MI": "🇮🇹 AZIONE IT"
}

# --- LOGICA DI ANALISI ---
def baum_analysis(ticker, timeframe="1d"):
    try:
        data = yf.download(ticker, period="60d", interval=timeframe, progress=False)
        if data.empty: return None
        p = data['Close'][ticker] if isinstance(data.columns, pd.MultiIndex) else data['Close']
        returns = p.pct_change().dropna()
        # Stabilità (Baum-Welch Proxy)
        p00 = np.clip(1.0 - (returns.tail(10).std() / (returns.std() * 2)), 0, 1)
        sma_20 = p.rolling(window=20).mean().iloc[-1]
        prezzo = float(p.iloc[-1])
        return {
            "TICKER": ticker, 
            "CATEGORIA": asset_class.get(ticker, "📈"),
            "PREZZO": round(prezzo, 2), 
            "STABILITÀ": p00, 
            "TREND": "✅ SOPRA MEDIA" if prezzo > sma_20 else "❌ SOTTO MEDIA"
        }
    except: return None

# --- CONTROLLI ---
st.sidebar.header("⚙️ Filtri")
intervallo = "1d"
if st.sidebar.button("⚡ Quick Test (1 Ora)"):
    intervallo = "1h"
    st.sidebar.warning("Analisi rapida 1h attiva")

# --- ESECUZIONE ---
gold_list, silver_list = [], []
for t in asset_class.keys():
    res = baum_analysis(t, intervallo)
    if res:
        if res["STABILITÀ"] > 0.75 and "✅" in res["TREND"]:
            gold_list.append(res)
        elif res["STABILITÀ"] > 0.50:
            silver_list.append(res)

# --- VISUALIZZAZIONE ---
if silver_list:
    st.subheader(f"📡 Radar Finalisti ({intervallo})")
    sorted_silver = sorted(silver_list, key=lambda x: x['STABILITÀ'], reverse=True)[:3]
    cols = st.columns(3)
    for i, stock in enumerate(sorted_silver):
        with cols[i]:
            st.metric(label=f"{stock['TICKER']}", value=f"{stock['PREZZO']} $", delta=f"{round(stock['STABILITÀ']*100, 1)}% Stab.")
            st.progress(stock['STABILITÀ'])

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("🚀 GOLD (Massima Prudenza)")
    if gold_list:
        st.table(pd.DataFrame(gold_list)[["TICKER", "CATEGORIA", "PREZZO"]])
    else:
        st.info("Nessun asset in regime stabile rialzista.")

with col2:
    st.subheader("📂 WATCHLIST (In Osservazione)")
    if silver_list:
        st.table(pd.DataFrame(silver_list)[["TICKER", "STABILITÀ", "TREND"]])

# --- FOOTER ---
st.divider()
st.caption(f"🕒 Aggiornato: {datetime.datetime.now().strftime('%H:%M:%S')} | Timeframe: {intervallo}")





