import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

# 🛡️ V3 BAUM HUNTER MK2 - DEFINITIVE VERSION
st.set_page_config(page_title="V3 BAUM HUNTER MK2", layout="wide", page_icon="🛡️")
st.title("🛡️ V3 BAUM-HUNTER MK2: Analisi Regimi")

# 1. SIDEBAR
st.sidebar.header("⚙️ Opzioni di Analisi")
intervallo = "1d"
periodo = "60d"
if st.sidebar.button("⚡ Esegui Quick Test (1 Ora)"):
    intervallo, periodo = "1h", "7d"
    st.sidebar.warning("Analisi 1h attiva: Sensibilità Massima.")

# 2. ASSET E LOGICA
asset_class = {
    "BTC-USD": "🪙 CRYPTO", "ETH-USD": "🪙 CRYPTO", "SOL-USD": "🪙 CRYPTO",
    "GC=F": "🔱 FUTURE (ORO)", "ES=F": "🔱 FUTURE (S&P500)", "NQ=F": "🔱 FUTURE (NASDAQ)",
    "ENI.MI": "🇮🇹 AZIONE IT", "MAIRE.MI": "🇮🇹 AZIONE IT", "FER.MI": "🇮🇹 AZIONE IT",
    "AAPL": "🇺🇸 AZIONE US", "NVDA": "🇺🇸 AZIONE US", "MSFT": "🇺🇸 AZIONE US", "TSLA": "🇺🇸 AZIONE US", 
    "PLTR": "🇺🇸 AZIONE US", "RIVN": "🇺🇸 AZIONE US", "COIN": "🇺🇸 AZIONE US"
}

def baum_analysis(ticker, timeframe, span):
    try:
        data = yf.download(ticker, period=span, interval=timeframe, progress=False)
        if data.empty: return None
        p = data['Close'][ticker] if isinstance(data.columns, pd.MultiIndex) else data['Close']
        returns = p.pct_change().dropna()
        p00 = np.clip(1.0 - (returns.tail(10).std() / (returns.std() * 2)), 0, 1)
        sma_20 = p.rolling(window=20).mean().iloc[-1]
        prezzo = float(p.iloc[-1])
        return {"TICKER": ticker, "CATEGORIA": asset_class.get(ticker, "📈"), "PREZZO": round(prezzo, 2), "STABILITÀ": p00, "SOPRA_MEDIA": prezzo > sma_20}
    except: return None

# 3. SCANSIONE
gold_list, silver_list = [], []
for t in asset_class.keys():
    res = baum_analysis(t, intervallo, periodo)
    if res:
        if res["STABILITÀ"] > 0.75 and res["SOPRA_MEDIA"]: gold_list.append(res)
        elif res["STABILITÀ"] > 0.50: silver_list.append(res)

# 4. RADAR
if silver_list:
    st.subheader(f"📡 Radar Finalisti ({intervallo})")
    sorted_silver = sorted(silver_list, key=lambda x: x['STABILITÀ'], reverse=True)[:3]
    cols = st.columns(3)
    for i, stock in enumerate(sorted_silver):
        with cols[i]:
            st.metric(label=f"{stock['CATEGORIA']} - {stock['TICKER']}", value=f"{stock['PREZZO']} $", delta=f"{round(stock['STABILITÀ']*100, 1)}% Stab.")
            st.progress(stock['STABILITÀ'])

st.divider()

# 5. TABELLE
c1, c2 = st.columns(2)
with c1:
    st.subheader("🚀 GOLD")
    if gold_list: st.table(pd.DataFrame(gold_list)[["TICKER", "CATEGORIA", "PREZZO"]])
    else: st.info("🛡️ Nessun segnale Gold.")
with c2:
    st.subheader("📂 WATCHLIST")
    if silver_list: st.table(pd.DataFrame(silver_list)[["TICKER", "STABILITÀ", "SOPRA_MEDIA"]])

st.divider()
st.caption(f"🕒 Update: {datetime.datetime.now().strftime('%H:%M:%S')} | Mode: {intervallo}")



