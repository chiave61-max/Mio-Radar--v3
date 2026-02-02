import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

# --- CONFIGURAZIONE GENERALE ---
st.set_page_config(page_title="V3 BAUM SUITE", layout="wide", page_icon="⚖️")

# --- MENU LATERALE ---
st.sidebar.title("🎮 Centro Comando")
modalita = st.sidebar.radio("Seleziona Strumento:", ["🎯 HUNTER (Caccia)", "🛡️ GUARDIAN (Portafoglio)"])

# --- DATABASE ASSET ---
asset_class = {
    "BTC-USD": "🪙 CRYPTO", "ETH-USD": "🪙 CRYPTO", "SOL-USD": "🪙 CRYPTO",
    "GC=F": "🔱 FUTURE (ORO)", "ES=F": "🔱 FUTURE (S&P500)", "NQ=F": "🔱 FUTURE (NASDAQ)",
    "AAPL": "🇺🇸 AZIONE US", "NVDA": "🇺🇸 AZIONE US", "MSFT": "🇺🇸 AZIONE US", 
    "TSLA": "🇺🇸 AZIONE US", "PLTR": "🇺🇸 AZIONE US", "RIVN": "🇺🇸 AZIONE US", "COIN": "🇺🇸 AZIONE US"
}

# --- PORTAFOGLIO REALE (Inserisci qui i tuoi dati) ---
# Formato: "TICKER": [Prezzo d'acquisto]
my_portfolio = {
    "AAPL": [180.50],  # Metti il tuo vero prezzo d'acquisto qui
}

# --- FUNZIONE LOGICA BAUM ---
def baum_analysis(ticker, timeframe="1d", span="60d"):
    try:
        data = yf.download(ticker, period=span, interval=timeframe, progress=False)
        if data.empty: return None
        p = data['Close'][ticker] if isinstance(data.columns, pd.MultiIndex) else data['Close']
        returns = p.pct_change().dropna()
        p00 = np.clip(1.0 - (returns.tail(10).std() / (returns.std() * 2)), 0, 1)
        sma_20 = p.rolling(window=20).mean().iloc[-1]
        prezzo = float(p.iloc[-1])
        return {"TICKER": ticker, "PREZZO": round(prezzo, 2), "STABILITÀ": p00, "SOPRA_MEDIA": prezzo > sma_20, "SMA20": round(sma_20, 2)}
    except: return None

# --- LOGICA MODALITÀ 1: HUNTER ---
if modalita == "🎯 HUNTER (Caccia)":
    st.title("🎯 V3 HUNTER: Scansione Segnali")
    intervallo = "1d"
    if st.sidebar.button("⚡ Quick Test (1 Ora)"):
        intervallo = "1h"
        st.sidebar.warning("Analisi 1h attiva.")

    gold_list, silver_list = [], []
    for t in asset_class.keys():
        res = baum_analysis(t, timeframe=intervallo)
        if res:
            res["CATEGORIA"] = asset_class.get(t, "📈")
            if res["STABILITÀ"] > 0.75 and res["SOPRA_MEDIA"]: gold_list.append(res)
            elif res["STABILITÀ"] > 0.50: silver_list.append(res)

    # Radar
    if silver_list:
        st.subheader("📡 Radar Finalisti")
        sorted_silver = sorted(silver_list, key=lambda x: x['STABILITÀ'], reverse=True)[:3]
        cols = st.columns(3)
        for i, stock in enumerate(sorted_silver):
            with cols[i]:
                st.metric(label=f"{stock['CATEGORIA']} - {stock['TICKER']}", value=f"{stock['PREZZO']} $", delta=f"{round(stock['STABILITÀ']*100, 1)}% Stab.")
                st.progress(stock['STABILITÀ'])

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🚀 OPPORTUNITÀ GOLD")
        if gold_list: st.table(pd.DataFrame(gold_list)[["TICKER", "CATEGORIA", "PREZZO"]])
        else: st.info("🛡️ Nessun segnale Gold.")
    with c2:
        st.subheader("📂 WATCHLIST")
        if silver_list: st.table(pd.DataFrame(silver_list)[["TICKER", "STABILITÀ", "SOPRA_MEDIA"]])

# --- LOGICA MODALITÀ 2: GUARDIAN ---
elif modalita == "🛡️ GUARDIAN (Portafoglio)":
    st.title("🛡️ V3 GUARDIAN: Protezione Apple & Co.")
    if not my_portfolio:
        st.warning("Inserisci i tuoi titoli nel codice per iniziare.")
    else:
        g_results = []
        for t, info in my_portfolio.items():
            res = baum_analysis(t)
            if res:
                entry = info[0]
                perf = ((res["PREZZO"] - entry) / entry) * 100
                g_results.append({
                    "TICKER": t, "ENTRATA": entry, "ATTUALE": res["PREZZO"],
                    "PROFITTO %": f"{round(perf, 2)}%", "STABILITÀ": res["STABILITÀ"],
                    "STOP PROTEZIONE (SMA20)": res["SMA20"],
                    "STATO": "✅ TIENI" if res["SOPRA_MEDIA"] else "⚠️ VENDI"
                })
        
        df_g = pd.DataFrame(g_results)
        cols = st.columns(len(g_results))
        for i, row in df_g.iterrows():
            with cols[i]:
                st.metric(label=f"💰 {row['TICKER']}", value=f"{row['ATTUALE']} $", delta=row['PROFITTO %'])
                st.write(f"Soglia di uscita: **{row['STOP PROTEZIONE (SMA20)']} $**")
                st.progress(row['STABILITÀ'])
        
        st.divider()
        st.subheader("📋 Gestione Rischio")
        st.table(df_g)

# Footer
st.divider()
st.caption(f"🕒 Ultimo check: {datetime.datetime.now().strftime('%H:%M:%S')}")




