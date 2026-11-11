import requests
import json
import time
import random
import statistics
from datetime import datetime

# Headers reforzados para evitar bloqueos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

BANCOS_VE = [
    "Banesco", "Mercantil", "Provincial", "BancoDeVenezuela", 
    "BNC", "Bancamiga", "PagoMovil", "TransferenciaBancaria", 
    "Banplus", "Bancaribe"
]

def consultar_p2p(tipo, monto="", bancos=None, filas=10):
    """Función auxiliar para consultar el libro de órdenes P2P de Binance."""
    url = "https://binance.com"
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "merchantCheck": True,
        "page": 1,
        "payTypes": bancos if bancos is not None else [],
        "publisherType": "merchant",
        "rows": filas,
        "tradeType": tipo,
        "transAmount": str(monto) if monto else ""
    }
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json().get('data', [])
    except Exception as e:
        print(f"⚠️ Error consultando Binance P2P ({tipo} - monto: {monto}): {e}")
    return []

def obtener_binance_unificado():
    """Obtiene tanto el promedio estilo monitor como las tasas escalonadas reales."""
    datos_p2p = {
        "referencia_monitor": {},
        "ejecucion_real": {
            "compras_buy": {},
            "ventas_sell": {}
        }
    }

    # 1. PROMEDIO ESTILO MONITOR (Sin filtro de monto, filtrando anuncios promocionados)
    for tipo in ["BUY", "SELL"]:
        anuncios = consultar_p2p(tipo=tipo, monto="", bancos=[], filas=10)
        precios_reales = []
        
        for item in anuncios:
            adv = item.get('adv', {})
            if adv.get('privilegeType') is None:  # Ignora anuncios patrocinados
                precios_reales.append(float(adv['price']))
            if len(precios_reales) == 5:
                break
        
        if precios_reales:
            clave = "compra_buy" if tipo == "BUY" else "venta_sell"
            datos_p2p["referencia_monitor"][clave] = round(statistics.mean(precios_reales), 2)
        
        time.sleep(random.uniform(1.2, 2.2))

    # Calculamos el punto medio entre Buy y Sell
    ref = datos_p2p["referencia_monitor"]
    if "compra_buy" in ref and "venta_sell" in ref:
        ref["promedio_general"] = round((ref["compra_buy"] + ref["venta_sell"]) / 2, 2)

    # 2. TASAS REALES POR TRAMO (10.000 y 100.000 con tus bancos específicos)
    for tipo in ["BUY", "SELL"]:
        for monto in:
            anuncios = consultar_p2p(tipo=tipo, monto=monto, bancos=BANCOS_VE, filas=5)
            
            # Tomamos el primer anuncio real (no patrocinado) de ese tramo
            precio_tramo = None
            for item in anuncios:
                adv = item.get('adv', {})
                if adv.get('privilegeType') is None:
                    precio_tramo = float(adv['price'])
                    break
            
            # Respaldo por si todos los primeros fueran patrocinados
            if precio_tramo is None and anuncios:
                precio_tramo = float(anuncios[0]['adv']['price'])

            if precio_tramo:
                clave = "compras_buy" if tipo == "BUY" else "ventas_sell"
                datos_p2p["ejecucion_real"][clave][f"tasa_{monto}"] = precio_tramo
            
            time.sleep(random.uniform(1.2, 2.2))

    return datos_p2p

def obtener_yadio():
    url = "https://yadio.io"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return {
                "usd_general": data.get('USD', {}).get('rate'),
                "p2p_usdt": data.get('USD', {}).get('other', {}).get('p2p_usdt', {}).get('rate')
            }
    except Exception as e:
        print(f"⚠️ Error consultando Yadio: {e}")
    return None

def obtener_binance_directo():
    url = "https://binance.com"
    url_alt = "https://binance.com"
    
    for endpoint in [url, url_alt]:
        try:
            response = requests.get(endpoint, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data.get('success'):
                    precio = data['data'].get('sPrice') or data['data'].get('price')
                    if precio:
                        return float(precio)
                elif 'price' in data:
                    return float(data['price'])
        except:
            continue
    return None

def actualizar_todo():
    datos_finales = {
        "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    p_binance_directo = obtener_binance_directo()
    if p_binance_directo:
        datos_finales["binance_directo"] = p_binance_directo
        print("✅ Binance Directo cargado")

    binance_data = obtener_binance_unificado()
    if binance_data["referencia_monitor"] or binance_data["ejecucion_real"]["compras_buy"]:
        datos_finales["binance_p2p"] = binance_data
        print("✅ Binance P2P (Monitor + Escalonado) cargado")
        
    p_yadio = obtener_yadio()
    if p_yadio:
        datos_finales["yadio"] = p_yadio
        print("✅ Yadio cargado")

    if len(datos_finales) > 1:
        with open('p2p.json', 'w', encoding='utf-8') as f:
            json.dump(datos_finales, f, indent=4, ensure_ascii=False)
        print("💾 Archivo 'p2p.json' actualizado con éxito.")
    else:
        print("🚫 No se pudo obtener ninguna tasa.")

if __name__ == "__main__":
    actualizar_todo()
