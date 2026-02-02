
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configurazione Dashboard "Hunter Mark-II"
st.set_page_config(page_title="V3 BAUM HUNTER MK2", layout="wide", page_icon="🛡️")

st.title("🛡️ V3 BAUM-HUNTER MK2: Classificazione Asset")
st.divider()

# Dizionario per marchiare la razza dei titoli
asset_class = {
    "BTC-USD": "🪙 CRYPTO", "ETH-USD": "🪙 CRYPTO", "SOL-USD": "🪙 CRYPTO",
    "GC=F": "🔱 FUTURE (ORO)", "ES=F": "🔱 FUTURE (S&P500)", "NQ=F": "🔱 FUTURE (NASDAQ)", "CL=F": "🔱 FUTURE (OIL)",
    "ENI.MI": "🇮🇹 AZIONE IT", "MAIRE.MI": "🇮🇹 AZIONE IT", "FER.MI": "🇮🇹 AZIONE IT", "UCG.MI": "🇮🇹 AZIONE IT",
    "AAPL": "🇺🇸 AZIONE US", "NVDA": "🇺🇸 AZIONE US", "MSFT": "🇺🇸 AZIONE US", "TSLA": "🇺🇸 AZIONE US", 
    "PLTR": "🇺🇸 AZIONE US", "RIVN": "🇺🇸 AZIONE US", "COIN": "🇺🇸 AZIONE US", "AMZN": "🇺🇸 AZIONE US"
}

def baum_analysis(ticker):
    try:
        data = yf.download(ticker, period="60d", interval="1d", progress=False)
        if data.empty or len(data) < 30: return None
        p = data['Close'][ticker] if isinstance(data.columns, pd.MultiIndex) else data['Close']
        returns = p.pct_change().dropna()
        vol_short, vol_long = returns.tail(10).std(), returns.std()
        p00 = np.clip(1.0 - (vol_short / (vol_long * 2)), 0, 1)
        sma_20 = p.rolling(window=20).mean().iloc[-1]
        prezzo_attuale = float(p.iloc[-1])
        
        # Identifica la categoria o metti "Generic"
        categoria = asset_class.get(ticker, "📈 AZIONE")
        
        return {
            "TICKER": ticker, 
            "CATEGORIA": categoria,
            "PREZZO": round(prezzo_attuale, 2), 
            "STABILITÀ": p00, 
            "SOPRA_MEDIA": prezzo_attuale > sma_20
        }
    except: return None

market_pool = list(asset_class.keys())
gold_list, silver_list = [], []

for t in market_pool:
    res = baum_analysis(t)
    if res:
        if res["STABILITÀ"] > 0.75 and res["SOPRA_MEDIA"]:
            gold_list.append(res)
        elif res["STABILITÀ"] > 0.50:
            silver_list.append(res)

# --- RADAR DEI FINALISTI (TOP 3) ---
if silver_list:
    st.subheader("📡 Radar Finalisti: Prossimi al segnale Gold")
    sorted_silver = sorted(silver_list, key=lambda x: x['STABILITÀ'], reverse=True)[:3]
    cols = st.columns(3)
    for i, stock in enumerate(sorted_silver):
        with cols[i]:
            st.metric(label=f"{stock['CATEGORIA']} - {stock['TICKER']}", 
                      value=f"{stock['PREZZO']} $", 
                      delta=f"{round(stock['STABILITÀ']*100, 1)}% Stabilità")
            st.progress(stock['STABILITÀ'])

st.divider()

# Tabella Gold
st.subheader("🚀 OPPORTUNITÀ GOLD (Segnali Confermati)")
if gold_list:
    st.table(pd.DataFrame(gold_list).drop(columns=["STABILITÀ", "SOPRA_MEDIA"]))
else:
    st.info("🛡️ Nessun segnale Gold rilevato. Baum-Welch consiglia attesa.")

# Tabella Watchlist
with st.expander("📂 Lista di Attesa Completa (Classificata)"):
    if silver_list:
        st.table(pd.DataFrame(silver_list))




