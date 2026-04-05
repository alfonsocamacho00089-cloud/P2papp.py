import requests
import json

# Headers reforzados para evitar bloqueos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def obtener_binance():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    # Filtramos por monto de 5.000 Bs para evitar las tasas de "ballenas"
    payload = {
        "asset": "USDT", 
        "fiat": "VES", 
        "merchantCheck": True,
        "page": 1, 
        "payTypes": ["Banesco"], 
        "publisherType": None,
        "rows": 5,           # Traemos 5 para promediar
        "tradeType": "SELL",  # "BUY" muestra lo que el usuario paga (la venta del cajero)
        "transAmount": "5000" # <--- EL FILTRO MÁGICO
    }
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=20)
        if response.status_code == 200:
            data = response.json().get('data', [])
            if data:
                # Sacamos el promedio de los primeros 5 anuncios reales
                precios = [float(adv['adv']['price']) for adv in data]
                return round(sum(precios) / len(precios), 2)
    except Exception as e:
        print(f"Error en Binance: {e}")
        return None

def obtener_bybit():
    url = "https://api2.bybit.com/fiat/otc/item/list"
    payload = {
        "tokenId": "USDT", "currencyId": "VES", 
        "payment": ["Banesco"], "side": "1", 
        "size": "1", "page": "1"
    }
    try:
        # Bybit necesita los headers exactos para no dar 403
        response = requests.post(url, json=payload, headers=HEADERS, timeout=20)
        if response.status_code == 200:
            res_json = response.json()
            items = res_json.get('result', {}).get('items', [])
            return items[0]['price'] if items else None
    except: return None

def obtener_yadio():
    url = "https://api.yadio.io/json/VES"
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        if response.status_code == 200:
            return response.json().get('USD', {}).get('rate')
    except: return None

def actualizar_todo():
    datos_finales = {}
    
    # Ejecutamos las consultas
    p_binance = obtener_binance()
    p_bybit = obtener_bybit()
    p_yadio = obtener_yadio()

    # Solo agregamos si hay respuesta exitosa
    if p_binance:
        datos_finales["binance"] = {"title": "Binance P2P", "price": float(p_binance)}
        print(f"✅ Binance cargado: {p_binance}")

    if p_bybit:
        datos_finales["bybit"] = {"title": "Bybit P2P", "price": float(p_bybit)}
        print(f"✅ Bybit cargado: {p_bybit}")

    if p_yadio:
        datos_finales["yadio"] = {"title": "Yadio API", "price": float(p_yadio)}
        print(f"✅ Yadio cargado: {p_yadio}")

    # Guardamos el archivo si conseguimos al menos una tasa
    if datos_finales:
        with open('p2p.json', 'w', encoding='utf-8') as f:
            json.dump(datos_finales, f, indent=4, ensure_ascii=False)
        print("💾 Archivo 'p2p.json' actualizado.")
    else:
        print("🚫 No se pudo obtener ninguna tasa.")

if __name__ == "__main__":
    actualizar_todo()
