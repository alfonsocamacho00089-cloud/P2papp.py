import requests
import datetime
import json

def obtener_p2p_alto():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # Lista de métodos que quieres consultar
    metodos = ["Rosneft", "Banesco", "Mercantil"]
    precios_encontrados = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Referer": "https://p2p.binance.com/"
    }

    for banco in metodos:
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "tradeType": "SELL", 
            "payTypes": [banco],
            "transAmount": "500", # Monto bajo para captar tasas reales de usuarios comunes
            "rows": 10,
            "page": 1,
            "publisherType": "merchant"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                res_json = response.json()
                # Verificamos que existan datos en la respuesta
                if res_json.get('data') and len(res_json['data']) > 0:
                    precio = float(res_json['data'][0]['adv']['price'])
                    precios_encontrados.append(precio)
        except Exception as e:
            print(f"Error consultando {banco}: {e}")

    # Si encontramos precios en al menos uno de los bancos, devolvemos el más alto
    if precios_encontrados:
        return max(precios_encontrados)
    else:
        return "Sin señal: No se encontraron anuncios"

# --- Lógica de actualización y guardado ---

precio_alto = obtener_p2p_alto()
hora_actual = (datetime.datetime.now() - datetime.timedelta(hours=4)).strftime("%I:%M:%S %p")

# Verificamos si hubo un error o falta de señal
if isinstance(precio_alto, str) and ("Error" in precio_alto or "Sin" in precio_alto):
    print(f"No se pudo actualizar: {precio_alto}")
else:
    # Intentamos cargar el precio anterior para comparar
    try:
        with open("p2p.json", "r") as f:
            datos_previos = json.load(f)
            precio_anterior = datos_previos[0]["precio"]
    except:
        precio_anterior = None

    # Si el precio cambió o es la primera vez, actualizamos el archivo
    if str(precio_alto) != str(precio_anterior):
        resultado = [{"bank": "Binance P2P", "precio": precio_alto}]
        with open("p2p.json", "w") as f:
            json.dump(resultado, f, indent=4)
        print(f"¡Actualizado con éxito! precio más alto: {precio_alto}")
