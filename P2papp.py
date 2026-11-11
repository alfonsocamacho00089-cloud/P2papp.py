import statistics

def obtener_binance_promedio():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    resultados = {}
    
    for tipo in ["BUY", "SELL"]:
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "merchantCheck": True,
            "page": 1,
            "payTypes": [],  # Vacío incluye todos los métodos de pago, igual que los monitores
            "publisherType": "merchant",
            "rows": 10,      # Pedimos 10 para poder descartar los patrocinados y quedarnos con 5 reales
            "tradeType": tipo,
            "transAmount": "" # Sin filtro de monto para leer el libro general
        }
        try:
            response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                anuncios = response.json().get('data', [])
                precios_reales = []
                
                for item in anuncios:
                    adv = item.get('adv', {})
                    # Filtramos anuncios promocionados/patrocinados que distorsionan la punta
                    if adv.get('privilegeType') is None:
                        precios_reales.append(float(adv['price']))
                    
                    # Nos detenemos al juntar los primeros 5 precios reales
                    if len(precios_reales) == 5:
                        break
                
                if precios_reales:
                    clave = "compra_buy" if tipo == "BUY" else "venta_sell"
                    # Promedio simple de los 5 mejores anuncios reales
                    resultados[clave] = round(statistics.mean(precios_reales), 2)
                    
            time.sleep(random.uniform(1.0, 2.0))
        except Exception as e:
            print(f"Error en {tipo}: {e}")
            continue

    # Calculamos el promedio general (punto medio entre Buy y Sell) estilo Monitor Dólar
    if "compra_buy" in resultados and "venta_sell" in resultados:
        resultados["promedio_general"] = round(
            (resultados["compra_buy"] + resultados["venta_sell"]) / 2, 2
        )
        
    return resultados
