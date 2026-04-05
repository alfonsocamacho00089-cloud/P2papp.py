import requests
import json

# Headers reforzados para evitar bloqueos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}



def obtener_bybit():
    url = "https://api2.bybit.com/fiat/otc/item/list"
    payload = {
        "tokenId": "USDT", "currencyId": "VES", 
        "payment": ["Banesco"], "side": "0", 
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



def actualizar_todo():
    datos_finales = {}
    
    # Ejecutamos las consultas
    
    p_bybit = obtener_bybit()
    

    # Solo agregamos si hay respuesta exitosa
    

    if p_bybit:
        datos_finales["bybit"] = {"title": "Bybit P2P", "price": float(p_bybit)}
        print(f"✅ Bybit cargado: {p_bybit}")

    

    # Guardamos el archivo si conseguimos al menos una tasa
    if datos_finales:
        with open('tasas.json', 'w', encoding='utf-8') as f:
            json.dump(datos_finales, f, indent=4, ensure_ascii=False)
        print("💾 Archivo 'tasas.json' actualizado.")
    else:
        print("🚫 No se pudo obtener ninguna tasa.")

if __name__ == "__main__":
    actualizar_todo()
