import streamlit as st
import requests
import datetime
st.set_page_config(page_title="TuPropina P2P - Alto", page_icon="📡")
st.title("📡 Antena Binance P2P (Precio Alto)")

def obtener_p2p_alto():
    st.cache_data.clear()
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # SOLO CAMBIAMOS "SELL" por "BUY" para ver el precio más alto
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "tradeType": "BUY", 
        "bank": ["Banesco"],
        "rows": 1,
        "page": 1,
        "publisherType": None
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
hora_actual = (datetime.datetime.now() - datetime.timedelta(hours=4)).strftime("%I:%M:%S %p")
if "Error" in str(precio_alto) or "Sin" in str(precio_alto):
    st.error(precio_alto)
else:
    st.balloons()
    st.success(f"### 🔥 PRECIO ALTO (BUY): {precio_alto} Bs.")
    # Esto sigue siendo lo que lee tu otra app
    st.code(f"VALOR_REAL|{precio_alto}|")

st.info("Ahora estás viendo la tasa de 'Compra', que siempre es un poco más alta que la de 'Venta'.")
# Al final de tu código de Python en GitHub:
with open("tasa.txt", "w") as f:
    f.write(str(precio_alto))

st.success(f"Tasa guardada en GitHub: {precio_alto}")
st.write(f"🕒 **Última actualización:** {hora_actual}")
