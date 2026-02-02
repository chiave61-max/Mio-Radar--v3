import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. Configurazione Centrale Operativa
st.set_page_config(page_title="V3 TOTAL SHIELD", layout="wide", page_icon="🛡️")
st.title("🛡️ V3 COMMANDER - Dashboard Integrata")

# --- SEZIONE 1: MONITOR PORTAFOGLIO CORE (I tuoi investimenti) ---
st.header("🚀 Monitor Portafoglio Real-Time")
col1, col2, col3 = st.columns(3)

# Apple (AAPL) - Carico 222$
try:
    aapl_data = yf.download("AAPL", period="5d", interval="1h", progress=False)
    if not aapl_data.empty:
        prezzo_aapl = float(aapl_data['Close'].iloc[-1])
        delta_aapl = prezzo_aapl - 222.0
        col1.metric("APPLE (AAPL)", f"{prezzo_aapl:.2f} $", f"{delta_aapl:.2f} $")
        if prezzo_aapl <= 211.0:
            st.sidebar.error("🚨 ALERT: Apple sotto Stop Loss!")
except: col1.error("Dati Apple non disp.")

# ENI Milano
try:
    eni = yf.download("ENI.MI", period="2d", progress=False)
    if not eni.empty:
        p_eni = eni['Close'].iloc[-1]
        col2.metric("ENI (MILANO)", f"{p_eni:.2f} €")
except: col2.error("Dati ENI non disp.")

# Oro (Gold)
try:
    gold = yf.download("GC=F", period="2d", progress=False)
    if not gold.empty:
        p_gold = gold['Close'].iloc[-1]
        col3.metric("ORO (GOLD)", f"{p_gold:.1f} $")
except: col3.error("Dati Oro non disp.")

st.divider()

# --- SEZIONE 2: V3 SMALL RADAR (Analisi per i 2500€) ---
st.header("📊 V3 Small Radar - Analisi di Mercato")

def v3_logic_engine(ticker):
    try:
        # Recupero dati 15gg (come foto 21)
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
            "PREZZO": round(prezzo, 2), 
            "RSI": round(rsi, 1), 
            "VOLAT": round(volat, 2), 
            "STATUS": status
        }
    except: return None

# Lista Ticker Completa (USA + EU)
tickers_radar = ["SPY", "AAPL", "NVDA", "MSFT", "ENI.MI", "ASML.AS", "GC=F", "PLTR", "RIVN", "SOFI", "RKLB", "MAIRE.MI"]
results = []

for t in tickers_radar:
    res = v3_logic_engine(t)
    if res: results.append(res)

if results:
    df = pd.DataFrame(results)
    # Visualizzazione Tabella Identica alla tua foto 21
    st.table(df)
    
    st.divider()
    
    # --- IL VERDETTO FINALE PER I 2500€ ---
    if any(df['STATUS'] == "🚀 BUY (Sano)"):
        st.success("✅ Esistono opportunità con rischio calcolato per i 2500€.")
    else:
        st.warning("🛡️ NESSUN INGRESSO SICURO - Mantenere Liquidità.")

st.sidebar.info("V3 COMMANDER\nProtocollo Prudenza Totale attivo.\nStop Loss Apple: 211$")



