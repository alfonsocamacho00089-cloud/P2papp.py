import streamlit as st
import requests

st.set_page_config(page_title="TuPropina v3", page_icon="📡")
st.title("📡 Antena de Emergencia v3")

def obtener_todo():
    url = "https://api.alcambio.app/public"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        # Si 'data' existe, la usamos; si no, usamos el json completo
        return data.get('data', data)
    except Exception as e:
        return f"Error: {e}"

items = obtener_todo()

if isinstance(items, list):
    st.success("✅ ¡Señal recuperada! Datos encontrados:")
    for x in items:
        # Mostramos TODO lo que encontremos para ver dónde está el precio
        nombre = x.get('name', 'Sin nombre')
        precio = x.get('price', 'Sin precio')
        st.write(f"**{nombre}**: {precio} Bs.")
        
        # Guardamos el de Binance para tu otra app
        if "Binance" in nombre:
            st.write(f"VALOR_REAL|{precio}|")
else:
    st.error(f"⚠️ Seguimos sin ver los datos. Detalle: {items}")

st.info("Esta versión muestra todo lo que AlCambio tiene disponible ahorita.")
