import streamlit as st
import yfinance as yf

st.title("🛡️ V3 SHIELD - Apple Milano")

try:
    # Scarica dati Apple Milano
    data = yf.download("AAPL.MI", period="5d", interval="1h", progress=False)
    if not data.empty:
        prezzo = float(data['Close'].iloc[-1])
        # Calcolo rispetto al tuo carico di 222€
        st.metric("Apple attuale", f"{prezzo:.2f} €", f"{prezzo-222.0:.2f} €")
        st.line_chart(data['Close'])
        st.write("Target Carico: 222€ | Stop Loss: 211€")
except:
    st.error("Connessione ai mercati in corso...")
