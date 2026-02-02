import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configurazione Dashboard
st.set_page_config(page_title="V3 COMMANDER - FINAL RUN", layout="wide")

st.title("🛡️ V3 COMMANDER - PROTOCOLLO PRUDENZA")
st.write("---")

def v3_logic(ticker):
    try:
        # Recupero dati per Protocollo Prudenza (10 giorni)
        data = yf.download(ticker, period="10d", interval="1h", progress=False)
        if data.empty: return None
        
        prezzo = float(data['Close'].iloc[-1])
        
        # Calcolo RSI (V3 Style)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=7).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        # Volatilità
        volat = data['Close'].pct_change().std() * np.sqrt(252)

        # Logica di Verdetto
        if rsi > 65:
            status = "🚀 BUY (Sano)"
        elif rsi < 35:
            status = "🔥 IPERVENDUTO"
        else:
            status = "⚖️ HOLD (Debole)"
            
        return {
            "TICKER": ticker,
            "PREZZO": round(prezzo, 2),
            "RSI": round(rsi, 1),
            "VOLAT": round(volat, 2),
            "STATUS": status
        }
    except:
        return None

# --- ESECUZIONE RADAR ---
tickers = ["SPY", "AAPL", "NVDA", "MSFT", "ENI.MI", "ASML.AS", "GC=F", "PLTR", "RIVN", "SOFI", "RKLB", "MAIRE.MI"]

results = []
for t in tickers:
    res = v3_logic(t)
    if res: results.append(res)

if results:
    df = pd.DataFrame(results)
    
    # Mostra la tabella come nella tua foto 21
    st.table(df)
    
    st.write("---")
    
    # VERDETTO FINALE PER I 2500€
    if any(x == "🚀 BUY (Sano)" for x in df['STATUS']):
        st.success("✅ Esistono opportunità con rischio calcolato per i 2500€.")
    else:
        st.warning("🛡️ NESSUN INGRESSO SICURO - Mantenere Liquidità.")

st.sidebar.info("V3 COMMANDER\nProtocollo Prudenza Totale attivo.")


