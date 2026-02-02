import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurazione della centrale operativa
st.set_page_config(page_title="V3 TOTAL SHIELD", layout="wide", page_icon="🛡️")
st.title("🛡️ V3 COMMANDER - Dashboard Integrata")

# --- SEZIONE BIG: I TUOI INVESTIMENTI ---
st.header("🚀 Monitor Portafoglio Core")
col1, col2, col3 = st.columns(3)

# APPLE - Il tuo investimento principale
try:
    aapl = yf.download("AAPL", period="5d", interval="1h", progress=False)
    if not aapl.empty:
        prezzo_aapl = float(aapl['Close'].iloc[-1])
        carico = 222.0
        stop_loss = 211.0
        diff = prezzo_aapl - carico
        
        col1.metric("APPLE (AAPL)", f"{prezzo_aapl:.2f} $", f"{diff:.2f} $")
        
        if prezzo_aapl <= stop_loss:
            st.sidebar.error(f"⚠️ ALERT APPLE: Sotto Stop Loss ({stop_loss}$)")
        else:
            st.sidebar.success("✅ Apple in zona sicura")
except:
    col1.error("Dati Apple non disponibili")

# ENI MILANO
try:
    eni = yf.download("ENI.MI", period="5d", progress=False)
    if not eni.empty:
        prezzo_eni = eni['Close'].iloc[-1]
        col2.metric("ENI (MI)", f"{prezzo_eni:.2f} €")
except:
    col2.error("Dati ENI non disponibili")

# ORO (Bene rifugio)
try:
    gold = yf.download("GC=F", period="5d", progress=False)
    if not gold.empty:
        prezzo_gold = gold['Close'].iloc[-1]
        col3.metric("ORO (Gold)", f"{prezzo_gold:.1f} $")
except:
    col3.error("Dati Oro non disponibili")

st.divider()

# --- SEZIONE SMALL: SCANNER OPPORTUNITÀ ---
st.header("📊 V3 Small Radar - Analisi Mercato")
lista_ticker = ["SPY", "NVDA", "MSFT", "PLTR", "SOFI", "RKLB", "MAIRE.MI", "RIVN"]

radar_data = []
for t in lista_ticker:
    try:
        # Recupero dati per calcolo RSI (14 periodi)
        h = yf.download(t, period="20d", progress=False)
        if not h.empty:
            chiusura = h['Close'].iloc[-1]
            delta = h['Close'].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.rolling(window=14).mean()
            ema_down = down.rolling(window=14).mean()
            rs = ema_up / ema_down
            rsi = 100 - (100 / (1 + rs.iloc[-1]))
            
            # Logica Status V3
            if rsi > 65: status = "🚀 BUY (Sano)"
            elif rsi < 35: status = "🔥 IPERVENDUTO"
            else: status = "⚖️ HOLD (Debole)"
            
            radar_data.append({
                "TICKER": t,
                "PREZZO": f"{chiusura:.2f}",
                "RSI": round(rsi, 1),
                "STATUS": status
            })
    except:
        continue

# Creazione della tabella finale
if radar_data:
    df = pd.DataFrame(radar_data)
    st.table(df)

st.sidebar.info("🛡️ Protocollo Prudenza Totale\nSistema aggiornato con Stop Loss a 211$.")

