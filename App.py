import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

# --- CONFIGURAZIONE GENERALE SUITE ---
st.set_page_config(page_title="V3 BAUM SUITE", layout="wide", page_icon="⚖️")

# --- DATABASE E PORTAFOGLIO ---
# Qui monitoriamo il mercato generale
asset_class = {
    "BTC-USD": "🪙 CRYPTO", "ETH-USD": "🪙 CRYPTO", "SOL-USD": "🪙 CRYPTO",
    "GC=F": "🔱 FUTURE (ORO)", "ES=F": "🔱 FUTURE (S&P500)", "NQ=F": "🔱 FUTURE (NASDAQ)",
    "AAPL": "🇺🇸 AZIONE US", "NVDA": "🇺🇸 AZIONE US", "MSFT": "🇺🇸 AZIONE US", 
    "TSLA": "🇺🇸 AZIONE US", "PLTR": "🇺🇸 AZIONE US", "RIVN": "🇺🇸 AZIONE US", "COIN": "🇺🇸 AZIONE US",
    "ENI.MI": "🇮🇹 AZIONE IT", "MAIRE.MI": "🇮🇹 AZIONE IT", "UCG.MI": "🇮🇹 AZIONE IT"
}

# Qui ci sono le tue Apple prese a 222
# Formato: "TICKER": [Prezzo d'acquisto, "Nome Posizione"]
my_portfolio = {
    "AAPL": [222.00, "Apple Milano"], 
}

# --- FUNZIONE LOGICA BAUM-WELCH ---
def baum_analysis(ticker, timeframe="1d", span="60d"):
    try:
        data = yf.download(ticker, period=span, interval=timeframe, progress=False)
        if data.empty: return None
        # Gestione MultiIndex di yfinance
        p = data['Close'][ticker] if isinstance(data.columns, pd.MultiIndex) else data['Close']
        returns = p.pct_change().dropna()
        # Calcolo Stabilità (HMM Proxy)
        p00 = np.clip(1.0 - (returns.tail(10).std() / (returns.std() * 2)), 0, 1)
        # Indicatori di Trend
        sma_20 = p.rolling(window=20).mean().iloc[-1]
        prezzo_attuale = float(p.iloc[-1])
        return {
            "TICKER": ticker, 
            "PREZZO": round(prezzo_attuale, 2), 
            "STABILITÀ": p00, 
            "SOPRA_MEDIA": prezzo_attuale > sma_20, 
            "SMA20": round(sma_20, 2)
        }
    except: return None

# --- SIDEBAR DI NAVIGAZIONE ---
st.sidebar.title("🎮 Centro Comando")
st.sidebar.divider()
modalita = st.sidebar.radio("Scegli Strumento:", ["🎯 HUNTER (Analisi)", "🛡️ GUARDIAN (Portafoglio)"])

# --- MODALITÀ 1: HUNTER ---
if modalita == "🎯 HUNTER (Analisi)":
    st.title("🎯 V3 HUNTER: Scansione Regimi")
    st.sidebar.subheader("Opzioni Scansione")
    intervallo = "1d"
    if st.sidebar.button("⚡ Quick Test (1 Ora)"):
        intervallo = "1h"
        st.sidebar.warning("Analisi 1h attiva: Sensibilità Massima.")

    gold_list, silver_list = [], []
    with st.spinner('Scansione mercati in corso...'):
        for t in asset_class.keys():
            res = baum_analysis(t, timeframe=intervallo)
            if res:
                res["CATEGORIA"] = asset_class.get(t, "📈")
                if res["STABILITÀ"] > 0.75 and res["SOPRA_MEDIA"]:
                    gold_list.append(res)
                elif res["STABILITÀ"] > 0.50:
                    silver_list.append(res)

    # Radar Top 3
    if silver_list:
        st.subheader(f"📡 Radar Finalisti ({intervallo})")
        sorted_silver = sorted(silver_list, key=lambda x: x['STABILITÀ'], reverse=True)[:3]
        cols = st.columns(3)
        for i, stock in enumerate(sorted_silver):
            with cols[i]:
                st.metric(label=f"{stock['CATEGORIA']} - {stock['TICKER']}", value=f"{stock['PREZZO']} $", delta=f"{round(stock['STABILITÀ']*100, 1)}% Stabilità")
                st.progress(stock['STABILITÀ'])

    st.divider()
    col_g, col_s = st.columns(2)
    with col_g:
        st.subheader("🚀 OPPORTUNITÀ GOLD")
        if gold_list:
            st.table(pd.DataFrame(gold_list)[["TICKER", "CATEGORIA", "PREZZO"]])
        else:
            st.info("🛡️ Nessun segnale Gold confermato.")
    with col_s:
        st.subheader("📂 WATCHLIST HMM")
        if silver_list:
            st.table(pd.DataFrame(silver_list)[["TICKER", "STABILITÀ", "SOPRA_MEDIA"]])

# --- MODALITÀ 2: GUARDIAN ---
elif modalita == "🛡️ GUARDIAN (Portafoglio)":
    st.title("🛡️ V3 GUARDIAN: Monitoraggio Posizioni")
    if not my_portfolio:
        st.info("Il tuo portafoglio è vuoto.")
    else:
        g_results = []
        for t, info in my_portfolio.items():
            res = baum_analysis(t, timeframe="1d")
            if res:
                entry_price = info[0]
                label = info[1]
                perf = ((res["PREZZO"] - entry_price) / entry_price) * 100
                g_results.append({
                    "POSIZIONE": label,
                    "TICKER": t,
                    "CARICO": f"{entry_price} $",
                    "ATTUALE": f"{res['PREZZO']} $",
                    "PROFITTO %": f"{round(perf, 2)}%",
                    "STABILITÀ": res["STABILITÀ"],
                    "SOGLIA USCITA (SMA20)": f"{res['SMA20']} $",
                    "STATO": "✅ TIENI" if res["SOPRA_MEDIA"] else "⚠️ VENDI"
                })
        
        df_g = pd.DataFrame(g_results)
        
        # Metriche in alto
        cols = st.columns(len(g_results))
        for i, row in df_g.iterrows():
            with cols[i]:
                st.metric(label=f"💰 {row['POSIZIONE']}", value=row['ATTUALE'], delta=row['PROFITTO %'])
                st.write(f"🛡️ Protezione a: **{row['SOGLIA USCITA (SMA20)']}**")
                st.progress(row['STABILITÀ'])
        
        st.divider()
        st.subheader("📋 Piano d'Azione")
        st.table(df_g[["POSIZIONE", "TICKER", "CARICO", "PROFITTO %", "SOGLIA USCITA (SMA20)", "STATO"]])

# --- FOOTER ---
st.divider()
now = datetime.datetime.now().strftime("%H:%M:%S")
st.caption(f"🕒 Sistema operativo | Ultimo aggiornamento: {now} | Socio, rimani sempre cauto.")




