import streamlit as st
import requests
import time

def obtener_p2p_real():
    # Usamos el API de Binance Directo (desde el servidor de Streamlit no se bloquea)
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "merchantCheck": True,
        "rows": 1,
        "tradeType": "BUY"
    }
    try:
        res = requests.post(url, json=payload, timeout=5)
        data = res.json()
        return data['data'][0]['adv']['price']
    except:
        return None

st.title("📡 Antena de Precios Real-Time")

tasa = obtener_p2p_real()

if tasa:
    st.metric(label="Binance P2P Real", value=f"{tasa} Bs")
    # Esto es para que tu HTML pueda leer el dato
    st.write(f"VALOR_REAL|{tasa}|") 
else:
    st.error("Error de conexión con Binance")

# Auto-refresco cada 2horas 
time.sleep(120)
st.rerun()

Solo quito el final y agrego eso que pudiste 
