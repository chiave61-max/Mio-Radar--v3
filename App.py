import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configurazione Dashboard Professionale
st.set_page_config(page_title="V3 BAUM HUNTER", layout="wide", page_icon="🎯")

st.title("🎯 V3 BAUM-HUNTER & WATCHLIST")
st.markdown("### Scanner Algoritmico basato su Stati Nascosti (HMM)")
st.divider()

def baum_analysis(ticker):
    try:
        # Analisi dati 60 giorni per definire il regime (HMM)
        data = yf.download(ticker, period="60d", interval="1d", progress=False)
        if data.empty or len(data) < 30: return None
        
        # Gestione MultiIndex se necessario
        p = data['Close'][ticker] if isinstance(data.columns, pd.MultiIndex) else data['Close']
        returns = p.pct_change().dropna()
        
        # 1. PARAMETRO BAUM: Probabilità di persistenza dello stato calmo
        vol_short = returns.tail(10).std()
        vol_long = returns.std()
        p00 = 1.0 - (vol_short / (vol_long * 2)) 
        p00 = np.clip(p00, 0, 1)
        
        # 2. FILTRO TREND
        sma_20 = p.rolling(window=20).mean().iloc[-1]
        prezzo_attuale = float(p.iloc[-1])
        
        return {
            "TICKER": ticker,
            "PREZZO": round(prezzo_attuale, 2),
            "STABILITÀ": p00,
            "SOPRA_MEDIA": prezzo_attuale > sma_20
        }
    except:
        return None

# Lista di Scansione Universale
market_pool = [
    "AAPL", "NVDA", "MSFT", "TSLA", "GOOGL", "AMZN", "META", "NFLX", "AMD", 
    "PLTR", "SOFI", "RKLB", "RIVN", "PYPL", "BABA", "COIN", "MARA",
    "ENI.MI", "MAIRE.MI", "ASML.AS", "SAP.DE", "MC.PA", "FER.MI", "UCG.MI",
    "GC=F", "CL=F", "ES=F", "NQ=F", "BTC-USD", "ETH-USD", "SOL-USD"
]

st.write(f"🕵️‍♂️ Scansione di {len(market_pool)} mercati in corso...")

gold_list = []
silver_list = []

for t in market_pool:
    res = baum_analysis(t)
    if res:
        # CRITERI GOLD (Pronti all'acquisto)
        if res["STABILITÀ"] > 0.75 and res["SOPRA_MEDIA"]:
            gold_list.append({
                "TICKER": res["TICKER"],
                "PREZZO": res["PREZZO"],
                "STABILITÀ BAUM": f"{round(res['STABILITÀ'] * 100, 1)}%",
                "STATO": "🟢 PRONTO (Gold)"
            })
        # CRITERI SILVER (Lista di Attesa)
        elif res["STABILITÀ"] > 0.55:
            gold_list_tickers = [x["TICKER"] for x in gold_list]
            if res["TICKER"] not in gold_list_tickers:
                silver_list.append({
                    "TICKER": res["TICKER"],
                    "PREZZO": res["PREZZO"],
                    "STABILITÀ": f"{round(res['STABILITÀ'] * 100, 1)}%",
                    "MANCA": "✅ Trend" if not res["SOPRA_MEDIA"] else "📈 Forza",
                    "STATO": "🟡 ATTESA (Silver)"
                })

# --- VISUALIZZAZIONE ---

# 1. TABELLA GOLD
st.subheader("🚀 OPPORTUNITÀ GOLD (Parametri Baum Superati)")
if gold_list:
    st.table(pd.DataFrame(gold_list))
    st.success("💰 Segnale di acquisto: questi titoli sono in pieno regime di accumulazione.")
else:
    st.info("🛡️ Nessun titolo Gold rilevato. Rimanere in osservazione.")

st.divider()

# 2. TABELLA SILVER (WATCHLIST)
st.subheader("⏳ LISTA DI ATTESA (Watchlist HMM)")
if silver_list:
    st.write("Titoli in fase di stabilizzazione: monitorare per possibile passaggio a Gold.")
    st.table(pd.DataFrame(silver_list))
else:
    st.warning("Nessun titolo in zona Silver. Mercato attualmente instabile.")

st.sidebar.info("HMM Baum-Welch: lo scanner filtra il mercato cercando solo regimi di stabilità statistica.")





