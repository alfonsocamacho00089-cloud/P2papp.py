import streamlit as st
import requests

st.set_page_config(page_title="TuPropina P2P - Alto", page_icon="📡")
st.title("📡 Antena Binance P2P (Precio Alto)")

def obtener_p2p_alto():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # SOLO CAMBIAMOS "BUY" por "SELL" para ver el precio más alto
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "tradeType": "SELL", 
        "bank": ["Banesco"],
        "rows": 1,
        "page": 1,
        "publisherType": "merchant"
    }

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            res_json = response.json()
            precio = res_json['data'][0]['adv']['price']
            return precio
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Sin señal: {e}"

precio_alto = obtener_p2p_alto()

if "Error" in str(precio_alto) or "Sin" in str(precio_alto):
    st.error(precio_alto)
else:
    st.balloons()
    st.success(f"### 🔥 PRECIO ALTO (SELL): {precio_alto} Bs.")
    # Esto sigue siendo lo que lee tu otra app
    st.code(f"VALOR_REAL|{precio_alto}|")

st.info("Ahora estás viendo la tasa de 'Venta', que siempre es un poco más alta que la de 'Compra'.")
# Al final de tu código de Streamlit:
# --- COPIA DESDE AQUÍ ---
if st.query_params.get("api") == "techo":
    st.code(f"VALOR_REAL|{precio_alto}|")
    st.stop() 
# --- HASTA AQUÍ ---
    # Esto ayuda a que el HTML lo encuentre más fácil
