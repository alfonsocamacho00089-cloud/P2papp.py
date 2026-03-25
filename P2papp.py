import streamlit as st
import requests
import time

def obtener_datos_alcambio():
    url = "https://api.alcambio.app/public"
    try:
        # Aquí no necesitamos disfraces, AlCambio nos deja pasar directo
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            datos = response.json()
            precios = {}
            # Recorremos la lista para pescar los precios que te interesan
            for item in datos['data']:
                if item['name'] == 'Binance P2P':
                    precios['binance'] = item['price']
                if item['name'] == 'BCV':
                    precios['bcv'] = item['price']
            return precios
        return None
    except:
        return None

# Configuración de la página
st.set_page_config(page_title="TuPropina - Monitor", page_icon="📈")
st.title("📊 Monitor de Tasas Real")

data = obtener_datos_alcambio()

if data:
    # Creamos dos columnas para que se vea profesional
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="Binance P2P (Hoy)", value=f"{data.get('binance')} Bs")
    
    with col2:
        st.metric(label="Dólar BCV (Mañana)", value=f"{data.get('bcv')} Bs")

    # Esta es la línea secreta que lee tu otra aplicación
    st.write(f"VALOR_REAL|{data.get('binance')}|")
    
    st.info(f"Última sincronización: {time.strftime('%H:%M:%S')}")
else:
    st.warning("🔄 Buscando señal en AlCambio...")

# Se actualiza solito cada 60 segundos
time.sleep(60)
st.rerun()
