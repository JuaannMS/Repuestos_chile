import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 1. Cargar CSV
df = pd.read_csv("Data consolidada/df_nombres_duplicados.csv")

# 2. Función para extraer detalles desde la página
def extraer_detalles(url: str) -> dict:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    marca = soup.select_one(".product-brand") and soup.select_one(".product-brand").get_text(strip=True)
    modelo = soup.select_one(".product-model") and soup.select_one(".product-model").get_text(strip=True)
    num_parte = soup.select_one("#part-number") and soup.select_one("#part-number").get_text(strip=True)
    categoria = soup.select_one(".breadcrumb li:nth-last-child(2)") and \
                soup.select_one(".breadcrumb li:nth-last-child(2)").get_text(strip=True)

    return {
        "marca": marca,
        "modelo": modelo,
        "num_parte": num_parte,
        "categoría": categoria
    }

# 3. Generador de nombre
def generar_nombre(detalles: dict) -> str:
    piezas = [
        detalles.get("marca"),
        detalles.get("modelo"),
        detalles.get("categoría"),
        detalles.get("num_parte") and f"P.N.{detalles['num_parte']}"
    ]
    piezas = [re.sub(r"[\s––]+", " ", p).strip() for p in piezas if p]
    return " – ".join(piezas)

# 4. Loop principal con progreso
nuevos_nombres = []
total = len(df)

for idx, row in df.iterrows():
    # Mensaje de progreso cada 100 filas
    if idx != 0 and idx % 100 == 0:
        print(f"→ Procesadas {idx} de {total} URLs")

    url = row["Link"]  # Ajusta si tu columna de URLs se llama distinto
    try:
        detalles = extraer_detalles(url)
        nuevos_nombres.append(generar_nombre(detalles))
    except Exception as e:
        print(f"[Fila {idx}] Error al procesar {url}: {e}")
        nuevos_nombres.append(row["nombre_actual"])  # Ajusta si tu columna de nombre original se llama distinto

# Mensaje final
print(f"✅ Completado: procesadas {total} URLs.")

# 5. Guardar resultado
df["nombre_enriquecido"] = nuevos_nombres
df.to_excel("Data consolidada/df_nombres_duplicados_modificados.xlsx", index=False)
print("¡Listo! Archivo guardado con nombres enriquecidos.")
