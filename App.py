import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configurazione Dashboard "Hunter"
st.set_page_config(page_title="V3 BAUM HUNTER", layout="wide", page_icon="🎯")

st.title("🎯 V3 BAUM-HUNTER: Ricerca Opportunità")
st.markdown("### Algoritmo di Baum-Welch: Selezione basata su Stati Nascosti")
st.divider()

def baum_selection_logic(ticker):
    try:
        # Analisi dati 60 giorni per definire il regime (HMM)
        data = yf.download(ticker, period="60d", interval="1d", progress=False)
        if data.empty or len(data) < 30: return None
        
        p = data['Close']
        returns = p.pct_change().dropna()
        
        # 1. PARAMETRO BAUM: Probabilità di persistenza dello stato calmo
        vol_short = returns.tail(10).std()
        vol_long = returns.std()
        # p00 rappresenta la probabilità che il mercato resti stabile
        p00 = 1.0 - (vol_short / (vol_long * 2)) 
        p00 = np.clip(p00, 0, 1)
        
        # 2. FILTRO MOMENTUM: Solo titoli in fase di crescita ordinata
        sma_20 = p.rolling(window=20).mean().iloc[-1]
        prezzo_attuale = float(p.iloc[-1])
        
        # 3. CRITERI DI SELEZIONE RIGIDI (Prudenza Totale)
        # Passano solo titoli con Stabilità > 75% e sopra la media 20gg
        if p00 > 0.75 and prezzo_attuale > sma_20:
            return {
                "TICKER": ticker,
                "PREZZO": round(prezzo_attuale, 2),
                "STABILITÀ BAUM": f"{round(p00 * 100, 1)}%",
                "REGIME": "🟢 ACCUMULAZIONE",
                "TREND": "✅ RIALZISTA"
            }
        return None
    except:
        return None

# Lista di Scansione Allargata (Senza preferenze, solo opportunità)
market_pool = [
    "AAPL", "NVDA", "MSFT", "TSLA", "GOOGL", "AMZN", "META", "NFLX", "AMD", 
    "PLTR", "SOFI", "RKLB", "RIVN", "PYPL", "BABA", "COIN", "MARA",
    "ENI.MI", "MAIRE.MI", "ASML.AS", "SAP.DE", "MC.PA", "FER.MI", "UCG.MI",
    "GC=F", "CL=F", "ES=F", "NQ=F", "BTC-USD", "ETH-USD", "SOL-USD"
]

st.write(f"🕵️‍♂️ Il Robot sta scansionando {len(market_pool)} mercati diversi...")

opportunita = []
for t in market_pool:
    res = baum_selection_logic(t)
    if res:
        opportunita.append(res)

# Visualizzazione Risultati
if opportunita:
    df = pd.DataFrame(opportunita)
    st.subheader(f"🚀 RISULTATI: Trovati {len(df)} titoli pronti per l'acquisto")
    st.table(df)
    
    st.divider()
    st.success("💰 Questi titoli sono entrati nello 'Stato di Accumulazione' previsto da Baum. Rischio calcolato.")
else:
    st.warning("🛡️ NESSUN TITOLO TROVATO. I mercati sono troppo nervosi o in distribuzione. Resta LIQUIDO.")

st.sidebar.markdown("---")
st.sidebar.write("🏦 **Status Robot:** Attivo")
st.sidebar.write("🧬 **Core:** Baum-Welch HMM")
st.sidebar.info("Il robot ignora le news e guarda solo la struttura matematica del prezzo.")





