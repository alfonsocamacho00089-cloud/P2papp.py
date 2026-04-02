import requests
import datetime
import json

def obtener_p2p_alto():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "tradeType": "SELL",
        "payTypes": ["Banesco"], 
        "transAmount": "500",
        "rows": 10,
        "page": 1,
        "publisherType": "merchant"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Referer": "https://p2p.binance.com/"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get('data') and len(res_json['data']) > 0:
                # Extraemos los precios de los 10 anuncios
                lista_precios = [float(anuncio['adv']['price']) for anuncio in res_json['data']]
                # Retornamos el más alto de esos 10
                return max(lista_precios)
            return "Sin anuncios"
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Sin señal: {e}"

# --- ESTAS LÍNEAS DEBEN IR PEGADAS AL MARGEN IZQUIERDO ---
precio_alto = obtener_p2p_alto()
hora_actual = (datetime.datetime.now() - datetime.timedelta(hours=4)).strftime("%I:%M:%S %p")

# Intentamos cargar el precio anterior para comparar
try:
    with open("p2p.json", "r") as f:
        datos_previos = json.load(f)
        precio_anterior = datos_previos[0]["precio"]
except:
    precio_anterior = None

# Si el precio es distinto, actualizamos
if str(precio_alto) != str(precio_anterior):
    resultado = [{"bank": "Binance P2P", "precio": precio_alto}]
    with open("p2p.json", "w") as f:
        json.dump(resultado, f, indent=4)
    print(f"¡Actualizado con éxito! precio máximo de 10: {precio_alto}")
else:
    print(f"El precio no ha cambiado: {precio_alto}")
