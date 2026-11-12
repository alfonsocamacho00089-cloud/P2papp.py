import requests
import json
import time
from datetime import datetime
import random

# Headers reforzados para evitar bloqueos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.bybit.com",
    "Referer": "https://www.bybit.com/"
}


def obtener_binance_escalonado():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    resultados = {"compras_buy": {}, "ventas_sell": {}}
    
    for tipo in ["BUY", "SELL"]:
        payload = {
            "asset": "USDT", "fiat": "VES", "merchantCheck": True,
            "page": 1, "payTypes": ["Banesco", "Mercantil", "Provincial", "BancoDeVenezuela", "BNC", "Bancamiga", "PagoMovil", "TransferenciaBancaria", "Banplus", "Bancaribe"], "publisherType": "merchant",
            "rows": 20, "tradeType": tipo, "transAmount": ""
        }
        try:
            response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                anuncios = response.json()['data']
                precios = [float(item['adv']['price']) for item in anuncios]
                
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
    url = "https://api.yadio.io/json/VES"
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        if response.status_code == 200:
            return response.json().get('USD', {}).get('rate')
    except: return None

def obtener_binance_directo():
    # Endpoint público de Binance para consultar el precio de referencia de conversión USDT/VES
    url = "https://www.binance.com/bapi/asset/v1/public/asset-service/product/get-product-by-symbol?symbol=USDT_VES"
    # URL alternativa de respaldo (Ticker general de precios de Binance)
    url_alt = "https://api.binance.com/api/v3/ticker/price?symbol=USDTVES"
    
    try:
        # Intentamos con la API de activos
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
        # Si falla, probamos el ticker global de Binance v3
        response = requests.get(url_alt, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            precio = response.json().get('price')
            if precio:
                return float(precio)
    except:
        pass
        
    return None
def obtener_bybit_p2p():
    url = "https://bybit.com"
    resultados = {"compras_buy": {}, "ventas_sell": {}}
    lados = {"BUY": "1", "SELL": "0"}
    
    for tipo, side_code in lados.items():
        payload = {
            "userId": "",
            "tokenId": "USDT",
            "currencyId": "VES",
            "payment": [],
            "side": side_code,
            "size": "20",
            "page": "1",
            "amount": "",
            "authMaker": False,
            "canTrade": False
        }
        try:
            response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
            if response.status_code == 200 and response.text.strip():
                items = response.json().get('result', {}).get('items', [])
                precios = [float(item['price']) for item in items if item.get('price')]
                
                if precios:
                    primeros_5 = precios[:5]
                    ultimos_5 = precios[-5:]
                    combinados = primeros_5 + ultimos_5
                    
                    clave = "compras_buy" if tipo == "BUY" else "ventas_sell"
                    resultados[clave]["primeros_5"] = round(sum(primeros_5) / len(primeros_5), 2)
                    resultados[clave]["ultimos_5"] = round(sum(ultimos_5) / len(ultimos_5), 2)
                    resultados[clave]["promedio"] = round(sum(combinados) / len(combinados), 2)
            else:
                print(f"⚠️ Bybit respondió HTTP {response.status_code} ({tipo})")
            time.sleep(random.uniform(1.5, 2.5))
        except Exception as e:
            print(f"⚠️ Error consultando Bybit ({tipo}): {e}")
            continue
            
    return resultados


    
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
        print("✅ Binance P2P (10k y 100k) cargado")
        
    if p_yadio:
        datos_finales["yadio"] = {"title": "Yadio API", "price": float(p_yadio)}
    
    bybit_data = obtener_bybit_p2p()
    if bybit_data["compras_buy"] or bybit_data["ventas_sell"]:
        datos_finales["bybit_p2p"] = bybit_data
        print("✅ Bybit P2P cargado")
    
    if datos_finales:
        with open('p2p.json', 'w', encoding='utf-8') as f:
            json.dump(datos_finales, f, indent=4, ensure_ascii=False)
        print("💾 Archivo 'p2p.json' actualizado.")
    else:
        print("🚫 No se pudo obtener ninguna tasa.")

if __name__ == "__main__":
    actualizar_todo()
