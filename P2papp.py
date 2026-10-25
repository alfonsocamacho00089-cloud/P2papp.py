import json
import random
import time
from datetime import datetime
import requests

# Headers reforzados para evitar bloqueos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def obtener_binance_escalonado():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    resultados = {"compras_buy": {}, "ventas_sell": {}}
    
    for tipo in ["BUY", "SELL"]:
        for monto in:
            payload = {
                "asset": "USDT", "fiat": "VES", "merchantCheck": True,
                "page": 1, "payTypes": ["Banesco", "Mercantil", "Provincial", "BancoDeVenezuela", "BNC", "Bancamiga", "PagoMovil", "TransferenciaBancaria", "Banplus", "Bancaribe"], "publisherType": "merchant",
                "rows": 5, "tradeType": tipo, "transAmount": str(monto)
            }
            try:
                response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
                if response.status_code == 200:
                    precio = response.json()['data'][0]['adv']['price']
                    clave = "compras_buy" if tipo == "BUY" else "ventas_sell"
                    resultados[clave][f"tasa_{monto}"] = float(precio)
                time.sleep(random.uniform(1.5, 3.0)) 
            except: 
                continue
    return resultados
    

def obtener_yadio():
    url = "https://api.yadio.io/json/VES"
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        if response.status_code == 200:
            return response.json().get('USD', {}).get('rate')
    except: 
        return None


def obtener_binance_directo():
    url = "https://binance.com"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            for item in response.json().get('data', []):
                if item.get('pair') == 'USDT_VES':
                    return float(item.get('price'))
    except: 
        return None


def actualizar_todo():
    datos_finales = {}

    # 1. Obtener tasa Binance Directo (Nuevo botón)
    p_binance_directo = obtener_binance_directo()
    if p_binance_directo:
        datos_finales["binance_directo"] = float(p_binance_directo)
        print("✅ Binance Directo cargado")

    # 2. Obtener datos del P2P Escalonado
    binance_data = obtener_binance_escalonado()
    if binance_data and (binance_data["compras_buy"] or binance_data["ventas_sell"]):
        datos_finales["binance_p2p"] = binance_data
        print("✅ Binance (10k y 100k) cargado")
    
    # 3. Obtener datos de Yadio
    p_yadio = obtener_yadio()
    if p_yadio:
        datos_finales["yadio"] = {"title": "Yadio API", "price": float(p_yadio)}
        print("✅ Yadio cargado")

    # Guardamos el archivo si conseguimos al menos una tasa
    if datos_finales:
        with open('p2p.json', 'w', encoding='utf-8') as f:
            json.dump(datos_finales, f, indent=4, ensure_ascii=False)
        print("💾 Archivo 'p2p.json' actualizado.")
    else:
        print("🚫 No se pudo obtener ninguna tasa.")


if __name__ == "__main__":
    actualizar_todo()
                
