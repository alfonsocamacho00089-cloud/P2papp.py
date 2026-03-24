import streamlit as st
import requests

st.title("📡 Prueba de Señal BCV")

def probar_bcv():
    url = "https://api.alcambio.app/public"
    try:
        # Petición súper simple
        response = requests.get(url, timeout=10)
        datos = response.json()
        
        # Buscamos solo el BCV en la lista
        for item in datos['data']:
            if item['name'] == 'BCV':
                return item['price']
        return "No encontré el nombre BCV"
    except Exception as e:
        return f"Error de conexión: {e}"

tasa_bcv = probar_bcv()

if "Error" in str(tasa_bcv):
    st.error(tasa_bcv)
else:
    st.success(f"### Tasa Oficial BCV: {tasa_bcv} Bs")
    st.balloons()

st.info("Si esto sale en verde, la antena está viva.")
