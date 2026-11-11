import requests
import json
import time
from datetime import datetime
import random
import statistics

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def obtener_binance_escalonado():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    resultados = {
        "promedio_monitor": {},
        "compras_buy": {}, 
        "ventas_sell": {}
    }
    
    # 1. PROMEDIO ESTILO MONITOR / USDT.COM.VE (Sin filtro de monto y sin anuncios pagados)
    for tipo in ["BUY", "SELL"]:
        payload_general = {
            "asset": "USDT", "fiat": "VES", "merchantCheck": True,
            "page": 1, "payTypes": [], "publisherType": "merchant",
            "rows": 10, "tradeType": tipo, "transAmount": ""
        }
        try:
            response = requests.post(url, json=payload_general, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                anuncios = response.json().get('data', [])
                precios_reales = []
                for item in anuncios:
                    adv = item.get('adv', {})
                    # Ignoramos anuncios promocionados que alteran el primer lugar
                    if adv.get('privilegeType') is None:
                        precios_reales.append(float(adv['price']))
                    if len(precios_reales) == 5:
                        break
                
                if precios_reales:
                    clave = "compra_buy" if tipo == "BUY" else "venta_sell"
                    resultados["promedio_monitor"][clave] = round(statistics.mean(precios_reales), 2)
            time.sleep(random.uniform(1.5, 2.5))
        except:
            continue

    # Calculamos el promedio central entre Buy y Sell
    mon = resultados["promedio_monitor"]
    if "compra_buy" in mon and "venta_sell" in mon:
        mon["promedio_general"] = round((mon["compra_buy"] + mon["venta_sell"]) / 2, 2)

    # 2. TUS TASAS ESCALONADAS ORIGINALES (Promediando los 3 primeros anuncios reales)
    bancos = ["Banesco", "Mercantil", "Provincial", "BancoDeVenezuela", "BNC", "Bancamiga", "PagoMovil", "TransferenciaBancaria", "Banplus", "Bancaribe"]
    
    for tipo in ["BUY", "SELL"]:
        for monto in (10000, 100000):
            payload = {
                "asset": "USDT", "fiat": "VES", "merchantCheck": True,
                "page": 1, "payTypes": bancos, "publisherType": "merchant",
                "rows": 6, "tradeType": tipo, "transAmount": str(monto)
            }
            try:
                response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
                if response.status_code == 200:
                    anuncios = response.json().get('data', [])
                    precios_tramo = [
                        float(item['adv']['price']) for item in anuncios 
                        if item.get('adv', {}).get('privilegeType') is None
                    ][:3]
                    
                    if precios_tramo:
                        clave = "compras_buy" if tipo == "BUY" else "ventas_sell"
                        resultados[clave][f"tasa_{monto}"] = round(statistics.mean(precios_tramo), 2)
                time.sleep(random.uniform(1.5, 2.5)) 
            except:
                continue
                
    return resultados
