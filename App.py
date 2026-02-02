import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configurazione Dashboard
st.set_page_config(page_title="V3 SCANNER - Mercati", layout="wide", page_icon="📊")

st.title("📊 V3 COMMANDER - Radar Opportunità")
st.write("Analisi tecnica basata sul Protocollo Prudenza")
st.divider()

def v3_logic_engine(ticker):
    try:
        # Recupero dati 15 giorni (come nel tuo script Colab)
        data = yf.download(ticker, period="15d", interval="1h", progress=False)
        if data.empty: return None
        
        prezzo = data['Close'].iloc[-1]
        
        # Calcolo RSI Protocollo V3
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=7).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        # Volatilità annualizzata
        volat = data['Close'].pct_change().std() * np.sqrt(252)
        
        # Status Protocollo
        if rsi > 65: status = "🚀 BUY (Sano)"
        elif rsi < 35: status = "🔥 IPERVENDUTO"
        else: status = "⚖️ HOLD (Debole)"
        
        return {
            "TICKER": ticker, 
            "PREZZO": round(float(prezzo), 2), 
            "RSI": round(float(rsi), 1), 
            "VOLAT": round(float(volat), 2), 
            "STATUS": status
        }
    except Exception: return None

# Lista Ticker monitorata (la tua lista completa)
tickers_radar = [
    "SPY", "AAPL", "NVDA", "MSFT", "ENI.MI", 
    "ASML.AS", "GC=F", "PLTR", "RIVN", 
    "SOFI", "RKLB", "MAIRE.MI"
]

results = []
for t in tickers_radar:
    res = v3_logic_engine(t)
    if res: results.append(res)

if results:
    df = pd.DataFrame(results)
    
    # Mostra la tabella tecnica (esattamente come la volevi)
    st.table(df)
    
    st.divider()
    
    # --- IL VERDETTO FINALE PER L'INVESTIMENTO ---
    if any(df['STATUS'] == "🚀 BUY (Sano)"):
        st.success("✅ Esistono opportunità con rischio calcolato per nuove posizioni.")
    else:
        st.warning("🛡️ NESSUN INGRESSO SICURO - Mantenere Liquidità.")
else:
    st.error("Errore nel recupero dati dai mercati.")

st.sidebar.info("V3 SCANNER\nSolo monitoraggio tecnico attivo.")




