import requests
import json
import time
from datetime import datetime
import pytz

# Headers reforzados para evitar bloqueos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def obtener_binance_escalonado():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # --- LÓGICA DE TIEMPO (pytz) ---
    vzla_tz = pytz.timezone('America/Caracas')
    ahora = datetime.now(vzla_tz)
    h, m = ahora.hour, ahora.minute

    rangos_activos = []
    if h >= 6: rangos_activos.append(3000)
    if (h == 6 and m >= 15) or h > 6: rangos_activos.append(5000)
    if (h == 6 and m >= 30) or h > 6: rangos_activos.append(10000)
    if (h == 6 and m >= 45) or h > 6: rangos_activos.append(50000)
    if h >= 7: rangos_activos.append(100000)

    if not rangos_activos: return None

    # --- LÓGICA DE MONTOS (Ciclo) ---
    resultados = {"compras_buy": {}, "ventas_sell": {}}
    for tipo in ["BUY", "SELL"]:
        for monto in rangos_activos:
            payload = {
                "asset": "USDT", "fiat": "VES", "merchantCheck": False,
                "page": 1, "payTypes": ["Banesco"], "publisherType": None,
                "rows": 1, "tradeType": tipo, "transAmount": str(monto)
            }
            try:
                response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
                if response.status_code == 200:
                    precio = response.json()['data'][0]['adv']['price']
                    clave = "compras_buy" if tipo == "BUY" else "ventas_sell"
                    resultados[clave][f"tasa_{monto}"] = float(precio)
                time.sleep(1.2) 
            except: continue
    return resultados
    

def obtener_yadio():
    url = "https://api.yadio.io/json/VES"
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        if response.status_code == 200:
            return response.json().get('USD', {}).get('rate')
    except: return None

def actualizar_todo():
    datos_finales = {}
    
    # Llamamos a la nueva función integrada
    binance_data = obtener_binance_escalonado()
    p_bybit = obtener_bybit()
    p_yadio = obtener_yadio()

    if binance_data:
        datos_finales["binance_p2p"] = binance_data
        print(f"✅ Binance detallado cargado")

    if p_bybit:
        datos_finales["bybit"] = {"title": "Bybit P2P", "price": float(p_bybit)}
    
    if p_yadio:
        datos_finales["yadio"] = {"title": "Yadio API", "price": float(p_yadio)}

    if datos_finales:
        with open('p2p.json', 'w', encoding='utf-8') as f:
            json.dump(datos_finales, f, indent=4, ensure_ascii=False)

    # Guardamos el archivo si conseguimos al menos una tasa
    if datos_finales:
        with open('p2p.json', 'w', encoding='utf-8') as f:
            json.dump(datos_finales, f, indent=4, ensure_ascii=False)
        print("💾 Archivo 'p2p.json' actualizado.")
    else:
        print("🚫 No se pudo obtener ninguna tasa.")

if __name__ == "__main__":
    actualizar_todo()
