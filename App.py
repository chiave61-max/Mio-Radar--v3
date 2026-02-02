import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configurazione Dashboard
st.set_page_config(page_title="V3 SCANNER", layout="wide", page_icon="📊")

st.title("📊 V3 COMMANDER - Radar Opportunità")
st.write("Analisi tecnica basata sul Protocollo Prudenza")
st.divider()

def v3_logic_engine(ticker):
    try:
        # Recupero dati 15 giorni per stabilità RSI
        data = yf.download(ticker, period="15d", interval="1h", progress=False)
        if data.empty:
            return None
        
        # Gestione MultiIndex se presente
        if isinstance(data.columns, pd.MultiIndex):
            prezzo_serie = data['Close'][ticker]
        else:
            prezzo_serie = data['Close']
            
        prezzo = prezzo_serie.iloc[-1]
        
        # Calcolo RSI Protocollo V3
        delta = prezzo_serie.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=7).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        # Volatilità annualizzata
        volat = prezzo_serie.pct_change().std() * np.sqrt(252)
        
        # Status Protocollo
        if rsi > 65:
            status = "🚀 BUY (Sano)"
        elif rsi < 35:
            status = "🔥 IPERVENDUTO"
        else:
            status = "⚖️ HOLD (Debole)"
            
        return {
            "TICKER": ticker, 
            "PREZZO": round(float(prezzo), 2), 
            "RSI": round(float(rsi), 1), 
            "VOLAT": round(float(volat), 2), 
            "STATUS": status
        }
    except Exception:
        return None

# Lista Ticker monitorata (corretta per evitare errori)
tickers_radar = [
    "SPY", "AAPL", "NVDA", "MSFT", "ENI.MI", 
    "ASML.AS", "GC=F", "PLTR", "RIVN", 
    "SOFI", "RKLB", "MAIRE.MI"
]

results = []
for t in tickers_radar:
    res = v3_logic_engine(t)
    if res:
        results.append(res)

if results:
    df = pd.DataFrame(results)
    # Mostra la tabella tecnica identica a quella che volevi
    st.table(df)
    st.divider()
    
    # VERDETTO FINALE
    if any(df['STATUS'] == "🚀 BUY (Sano)"):
        st.success("✅ Esistono opportunità con rischio calcolato per nuove posizioni.")
    else:
        st.warning("🛡️ NESSUN INGRESSO SICURO - Mantenere Liquidità.")
else:
    # Messaggio di errore se proprio non scarica nulla
    st.error("Nessun dato recuperato. Verifica la connessione o i simboli.")

st.sidebar.info("V3 SCANNER - Solo monitoraggio tecnico attivo.")





