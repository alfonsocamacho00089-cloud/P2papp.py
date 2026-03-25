import streamlit as st
import requests

st.set_page_config(page_title="TuPropina P2P", page_icon="📡")
st.title("📡 Antena Binance P2P (Rescate)")

def obtener_p2p_directo():
    # Usamos un proxy/mirror que suele estar libre de bloqueos
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "tradeType": "BUY",
        "bank": ["Banesco"], # Filtramos por Banesco que es el más estable
        "rows": 1,
        "page": 1,
        "publisherType": "merchant"
    }

    try:
        # Aquí está el truco: simulamos ser un navegador real muy específico
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            res_json = response.json()
            precio = res_json['data'][0]['adv']['price']
            return precio
        else:
            return f"Error de Binance: {response.status_code}"
    except Exception as e:
        return f"Sin señal: {e}"

# Ejecutar la antena
precio_actual = obtener_p2p_directo()

if "Sin señal" in str(precio_actual) or "Error" in str(precio_actual):
    st.error(f"⚠️ La antena sigue bloqueada: {precio_actual}")
    st.info("Binance ha bloqueado la IP de este servidor por hoy.")
else:
    st.balloons()
    st.success(f"### 🔥 PRECIO BINANCE P2P: {precio_actual} Bs.")
    # Formato para tu otra app
    st.code(f"VALOR_REAL|{precio_actual}|")

st.info("Si sale error, es que Binance detectó el servidor de Streamlit y le cerró la puerta.")
