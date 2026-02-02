import streamlit as st
import yfinance as yf

st.title("🛡️ V3 SHIELD - MONITOR")
st.write("Monitoraggio Apple (Carico: 222€ | Stop: 211€)")

data = yf.download("AAPL.MI", period="5d", interval="1h")
if not data.empty:
    prezzo = data['Close'].iloc[-1]
    st.metric("Apple Milano", f"{prezzo:.2f} €", f"{prezzo-222:.2f} €")
    st.line_chart(data['Close'])

