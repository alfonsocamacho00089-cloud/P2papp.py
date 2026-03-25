import streamlit as st
import requests

def obtener_p2p_real():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }
    payload = {
        "asset": "USDT", "fiat": "VES", "merchantCheck": True,
        "rows": 1, "tradeType": "BUY", "publisherType": "merchant"
    }
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        data = res.json()
        return data['data'][0]['adv']['price']
    except:
        return None

st.title("📡 Antena P2P Real-Time")

# Botón manual para evitar el rebote infinito
if st.button('🔄 Actualizar Tasa Ahora'):
    st.cache_data.clear() # Limpia la memoria para traer el dato nuevo

tasa = obtener_p2p_real()

if tasa:
    st.metric(label="Binance P2P Real", value=f"{tasa} Bs")
    st.code(f"VALOR_REAL|{tasa}|", language="text") # Más fácil de copiar/leer
    st.success("✅ Señal estable")
else:
    st.error("⚠️ Error de conexión. Intenta de nuevo en un momento.")

st.info("Nota: Se recomienda esperar al menos 1 minuto entre actualizaciones.")
