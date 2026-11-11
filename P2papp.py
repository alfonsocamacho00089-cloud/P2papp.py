import requests
import json
import time
from datetime import datetime
import random

# Headers reforzados para evitar bloqueos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def obtener_binance_escalonado():
    url = "https://binance.com"
    resultados = {"compras_buy": {}, "ventas_sell": {}}
    
    for tipo in ["BUY", "SELL"]:
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "merchantCheck": False,
            "page": 1,
            "payTypes": [],
            "publisherType": None,
            "rows": 15,
            "tradeType": tipo,
            "transAmount": ""
        }
        try:
            response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                anuncios = response.json().get('data', [])
                
                # Filtramos solo los anuncios patrocinados y tomamos los precios reales
                precios = [
                    float(item['adv']['price']) for item in anuncios 
                    if item.get('adv', {}).get('privilegeType') is None
                ]
                
                if precios:
                    primeros_5 = precios[:5]
                    ultimos_5 = precios[-5:]
                    combinados = primeros_5 + ultimos_5
                    
                    clave = "compras_buy" if tipo == "BUY" else "ventas_sell"
                    resultados[clave]["primeros_5"] = round(sum(primeros_5) / len(primeros_5), 2)
                    resultados[clave]["ultimos_5"] = round(sum(ultimos_5) / len(ultimos_5), 2)
                    resultados[clave]["promedio"] = round(sum(combinados) / len(combinados), 2)
                    
            time.sleep(random.uniform(1.5, 3.0)) 
        except: continue
    return resultados

def obtener_yadio():
    url = "https://yadio.io"
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        if response.status_code == 200:
            return response.json().get('USD', {}).get('rate')
    except: return None

def obtener_binance_directo():
    url = "https://binance.com"
    url_alt = "https://binance.com"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'data' in data:
                precio = data['data'].get('sPrice') or data['data'].get('price')
                if precio:
                    return float(precio)
    except:
        pass

    try:
        response = requests.get(url_alt, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            precio = response.json().get('price')
            if precio:
                return float(precio)
    except:
        pass
        
    return None

def actualizar_todo():
    datos_finales = {}
    
    p_binance_directo = obtener_binance_directo()
    if p_binance_directo:
        datos_finales["binance_directo"] = float(p_binance_directo)
        print("✅ Binance Directo (Referencia) cargado")

    binance_data = obtener_binance_escalonado()
    p_yadio = obtener_yadio()

    if binance_data:
        datos_finales["binance_p2p"] = binance_data
        print("✅ Binance P2P cargado")
        
    if p_yadio:
        datos_finales["yadio"] = {"title": "Yadio API", "price": float(p_yadio)}

    if datos_finales:
        with open('p2p.json', 'w', encoding='utf-8') as f:
            json.dump(datos_finales, f, indent=4, ensure_ascii=False)
        print("💾 Archivo 'p2p.json' actualizado.")
    else:
        print("🚫 No se pudo obtener ninguna tasa.")

if __name__ == "__main__":
    actualizar_todo()
