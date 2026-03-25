import streamlit as st
import requests
import time

def obtener_p2p_real():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # 1. Definimos el "disfraz" (User-Agent)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "merchantCheck": True,
        "rows": 1,
        "tradeType": "BUY"
    }

    try:
        # 2. Pasamos los headers dentro del post
        res = requests.post(url, json=payload, headers=headers, timeout=10)
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
time.sleep(2hours)
st.rerun()

