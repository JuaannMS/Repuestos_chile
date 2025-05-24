import json
import re
import pandas as pd
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# ——— 1. Carga de configuración —————————————————————————
with open("extractors.json", encoding="utf-8") as f:
    config = json.load(f)

# ——— 2. Funciones auxiliares ——————————————————————————

def generar_slug_name(url: str) -> str:
    """Extrae y formatea el slug de la URL como nombre legible."""
    path = urlparse(url).path.strip("/").split("/")[0].rstrip("-")
    core = re.sub(r"-\d+$", "", path)
    return core.replace("-", " ").title()

def extraer_por_css(soup: BeautifulSoup, selectors: dict) -> dict:
    """Lee múltiples campos usando selectores CSS."""
    detalles = {}
    for key, sel in selectors.items():
        tag = soup.select_one(sel)
        detalles[key] = tag.get_text(strip=True) if tag else None
    return detalles

# ——— 3. Lógica principal ——————————————————————————————

# Ajusta el nombre de archivo y la columna de URL según tu CSV
INPUT_CSV    = "Data consolidada/df_nombres_duplicados.csv"
OUTPUT_FILE  = "Data consolidada/df_nombres_duplicados_modificados.xlsx"
URL_COLUMN   = "Link"

df    = pd.read_csv(INPUT_CSV)
df = df.head(10)
nombres = []
total   = len(df)

for idx, row in df.iterrows():
    url     = row[URL_COLUMN]
    dominio = urlparse(url).netloc
    rule    = config.get(dominio, {})

    # 3.1. Extraer nombre según el tipo de rule
    if rule.get("type") == "slug":
        name = generar_slug_name(url)

    else:
        # peticion y parseo
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        if rule.get("type") == "css":
            detalles = extraer_por_css(soup, rule["selectors"])
        elif rule.get("type") == "custom":
            mod  = __import__(rule["module"], fromlist=[rule["function"]])
            func = getattr(mod, rule["function"])
            detalles = func(soup)
        else:
            detalles = {}

        # formatear piezas en un solo nombre
        piezas = [
            detalles.get("marca"),
            detalles.get("modelo"),
            detalles.get("categoría"),
            detalles.get("num_parte") and f"P.N.{detalles['num_parte']}"
        ]
        piezas = [re.sub(r"[\s––]+", " ", p).strip() for p in piezas if p]
        name = " – ".join(piezas)

    nombres.append(name or row.get("Nombre Producto", ""))

    # progreso cada 100
    if (idx + 1) % 100 == 0:
        print(f"→ Procesadas {idx+1} de {total} URLs")

# ——— 4. Guardar resultados ————————————————————————————

df["nombre_enriquecido"] = nombres
df.to_excel(OUTPUT_FILE, index=False)

print(f"✅ Completado: procesadas {total} URLs. Salida en {OUTPUT_FILE}")
