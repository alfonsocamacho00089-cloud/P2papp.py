import requests
import datetime
import json

#st.set_page_config(page_title="TuPropina P2P - Alto", page_icon="📡")
#st.title("📡 Antena Binance P2P (Precio Alto)")

def obtener_p2p_alto():
    #st.cache_data.clear()
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # SOLO CAMBIAMOS "BUY" por "SELL" para ver el precio más alto
    payload = {
    "asset": "USDT",
    "fiat": "VES",
    "tradeType": "SELL",  # "SELL" para ver cuánto pagan por tus USDT
    "payTypes": ["Banesco"], # "Rosneft" es el código interno para PAGO MÓVIL
    "transAmount": "500",    # Un monto más común (500 Bs) para captar tasas reales
    "rows": 10,
    "page": 1,
    "publisherType": "merchant"
    }

    try:
        headers = {
            # USAMOS EL LARGO (EL MEJOR)
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Referer": "https://p2p.binance.com/" # Este toque extra le dice que vienes de su propia web
        }
        
        # ... resto de tu código igual
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get('data'):
                # Creamos una lista con los 10 precios que trajo Binance
                lista_precios = [float(anuncio['adv']['price']) for anuncio in res_json['data']]
                # De esos 10, elegimos el más alto (el máximo)
                return max(lista_precios)
            return "Sin anuncios"
precio_alto = obtener_p2p_alto()
hora_actual = (datetime.datetime.now() - datetime.timedelta(hours=4)).strftime("%I:%M:%S %p")
if "Error" in str(precio_alto) or "Sin" in str(precio_alto):
 data_p2p = [{"bank": "Binance P2P", "precio": precio_alto}]

if str(precio_alto) != str(json.load(open("p2p.json"))[0]["precio"]):
    
   # Asegúrate de que estas líneas tengan la misma sangría (espacios a la izquierda)
        resultado = [{"bank": "Binance P2P", "precio": precio_alto}]
        with open("p2p.json", "w") as f:
            json.dump(resultado, f, indent=4)
        print(f"¡Actualizado con éxito! precio: {precio_alto}")

        # enviar_notificacion_precio(precio_alto)
