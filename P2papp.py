import requests
import json
import time
import random
import statistics
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def obtener_binance_escalonado():
    url = "https://binance.com"
    resultados = {"compras_buy": 0, "ventas_sell": 0, "promedio_general": 0}
    
    for tipo in ["BUY", "SELL"]:
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "merchantCheck": True,
            "page": 1,
            "payTypes": [],
            "publisherType": "merchant",
            "rows": 10,
            "tradeType": tipo,
            "transAmount": ""
        }
        try:
            response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                anuncios = response.json().get('data', [])
                precios_reales = []
                
                for item in anuncios:
                    adv = item.get('adv', {})
                    if adv.get('privilegeType') is None:
                        precios_reales.append(float(adv['price']))
                    if len(precios_reales) == 5:
                        break
                
                if precios_reales:
                    clave = "compras_buy" if tipo == "BUY" else "ventas_sell"
                    resultados[clave] = round(statistics.mean(precios_reales), 2)
            else:
                print(f"⚠️ Binance P2P respondió código {response.status_code} ({tipo})")
                    
            time.sleep(random.uniform(1.5, 2.5))
        except Exception as e:
            print(f"⚠️ Error en Binance P2P ({tipo}): {e}")
            continue

    if resultados["compras_buy"] > 0 and resultados["ventas_sell"] > 0:
        resultados["promedio_general"] = round((resultados["compras_buy"] + resultados["ventas_sell"]) / 2, 2)
        
    return resultados

def obtener_yadio():
    url = "https://yadio.io"
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        if response.status_code == 200:
            return response.json().get('USD', {}).get('rate')
    except Exception as e:
        print(f"⚠️ Error Yadio: {e}")
    return None

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
    print("🚀 Iniciando actualización de tasas...")
    datos_finales = {
        "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    p_binance_directo = obtener_binance_directo()
    if p_binance_directo:
        datos_finales["binance_directo"] = float(p_binance_directo)
        print("✅ Binance Directo (Referencia) cargado")

    binance_data = obtener_binance_escalonado()
    p_yadio = obtener_yadio()

    if binance_data["promedio_general"] > 0:
        datos_finales["binance_p2p"] = binance_data
        print("✅ Binance P2P promediado cargado")
        
    if p_yadio:
        datos_finales["yadio"] = {"title": "Yadio API", "price": float(p_yadio)}
        print("✅ Yadio cargado")

    if len(datos_finales) > 1:
        with open('p2p.json', 'w', encoding='utf-8') as f:
            json.dump(datos_finales, f, indent=4, ensure_ascii=False)
        print("💾 Archivo 'p2p.json' actualizado.")
    else:
        print("🚫 No se pudo obtener ninguna tasa (posible bloqueo de IP en GitHub).")

if __name__ == "__main__":
    actualizar_todo()
