import streamlit as st
import requests
import json

# 1. Configuración de la página (Solo una vez)
st.set_page_config(page_title="Antena TuPropina P2P + Bancos", page_icon="📡")

st.title("📡 Antena TuPropina (P2P + Bancos)")

# --- SECCIÓN BINANCE P2P ---
def obtener_p2p_alto():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT", "fiat": "VES", "tradeType": "SELL", 
        "bank": ["Banesco"], "rows": 1, "page": 1, "publisherType": "merchant"
    }
    try:
        headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()['data'][0]['adv']['price']
        return "Error"
    except:
        return "Sin señal"

precio_alto = obtener_p2p_alto()

# Guardamos el USDT en tasa.txt (lo que ya usas hoy)
if "Error" not in str(precio_alto) and "Sin" not in str(precio_alto):
    with open("tasa.txt", "w") as f:
        f.write(str(precio_alto))
    st.success(f"### 🔥 USDT ALTO: {precio_alto} Bs.")
else:
    st.error(f"Falla en USDT: {precio_alto}")

st.divider()

# --- SECCIÓN BANCOS ---
st.subheader("🏦 Tasas de Bancos en Venezuela")

def buscar_bancos():
    # Esta es la API que agrupa los bancos
    url = "https://pydolarvenezuela-api.vercel.app/api/v1/dollar?page=bancamiga"
    try:
        response = requests.get(url, timeout=10)
        # Extraemos los monitores que son los bancos
        return response.json()['monitors']
    except:
        return None

# Botón para activar la búsqueda de bancos
if st.button('🔄 Actualizar Lista de Bancos'):
    with st.spinner('Conectando con los bancos...'):
        data_bancos = buscar_bancos()
        if data_bancos:
            # MAGIA: Guardamos la data en bancos.json para tu HTML
            with open("bancos.json", "w") as f:
                json.dump(data_bancos, f)
            
            st.success("¡Datos de bancos guardados exitosamente!")
            # Mostramos la tabla para que tú la veas en Streamlit
            st.dataframe(data_bancos)
        else:
            st.error("No se pudo obtener la información de los bancos en este momento.")

st.info("Nota: Al darle al botón, se genera el archivo 'bancos.json' que usará tu App principal.")
