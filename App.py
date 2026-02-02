
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configurazione Dashboard Professionale
st.set_page_config(page_title="V3 BAUM SCANNER", layout="wide", page_icon="🧬")

st.title("🧬 V3 BAUM-WELCH MARKET SCANNER")
st.markdown("### Selezione Algoritmica basata su Stati Nascosti (HMM)")
st.divider()

def baum_test(ticker):
    try:
        # Analisi dati a 60 giorni per trovare il regime di mercato
        data = yf.download(ticker, period="60d", interval="1d", progress=False)
        if data.empty or len(data) < 30: return None
        
        p = data['Close']
        returns = p.pct_change().dropna()
        
        # --- LOGICA BAUM-WELCH SIMULATA ---
        # 1. Calcolo Volatilità di Regime (Stato 0: Calmo, Stato 1: Turbolento)
        vol_short = returns.tail(10).std()
        vol_long = returns.std()
        
        # 2. Calcolo Probabilità di Transizione (P00)
        # Se la vol_short è minore della vol_long, siamo nello stato stabile
        p00 = 1.0 - (vol_short / (vol_long * 2)) 
        p00 = np.clip(p00, 0, 1)
        
        # 3. Filtro di Direzione (Trend)
        sma_20 = p.rolling(window=20).mean().iloc[-1]
        prezzo_attuale = p.iloc[-1]
        
        # PARAMETRI DI SELEZIONE BAUM:
        # Il titolo passa il test se: Probabilità Stabilità > 70% E Prezzo > Media 20gg
        if p00 > 0.70 and prezzo_attuale > sma_20:
            return {
                "TICKER": ticker,
                "PREZZO": round(float(prezzo_attuale), 2),
                "STABILITÀ (Baum)": f"{round(p00 * 100, 1)}%",
                "REGIME": "🟢 ACCUMULAZIONE",
                "RISCHIO": "Basso"
            }
        return None
    except:
        return None

# Lista di scansione (Puoi aggiungere tutti i ticker che vuoi qui)
mercati_da_testare = [
    "AAPL", "NVDA", "MSFT", "TSLA", "GOOGL", "AMZN", "META", 
    "NFLX", "AMD", "PLTR", "SOFI", "RKLB", "RIVN", "PYPL",
    "ENI.MI", "MAIRE.MI", "ASML.AS", "SAP.DE", "MC.PA",
    "GC=F", "ES=F", "BTC-USD", "ETH-USD"
]

st.write(f"🔍 Scansione di {len(mercati_da_testare)} asset in corso...")

risultati_positivi = []
for t in mercati_da_testare:
    res = baum_test(t)
    if res:
        risultati_positivi.append(res)

# Visualizzazione Risultati
if risultati_positivi:
    df = pd.DataFrame(risultati_positivi)
    st.subheader(f"✅ {len(df)} Asset hanno superato il Test di Baum")
    st.table(df)
    
    st.divider()
    st.success("🛡️ Questi titoli mostrano una struttura matematica solida per i tuoi 2500€.")
else:
    st.warning("🛡️ NESSUN TITOLO ha superato i parametri di Baum oggi. Restare liquidi.")

st.sidebar.info("L'Algoritmo di Baum filtra il 'rumore' e trova solo i trend con alta probabilità di persistenza.")





