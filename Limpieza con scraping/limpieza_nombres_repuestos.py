import json
import re
import pandas as pd
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from requests.exceptions import ReadTimeout, RequestException

with open("extractors.json", encoding="utf-8") as f:
    config = json.load(f)


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


INPUT_CSV   = "Data consolidada/df_nombres_duplicados.xlsx"
OUTPUT_FILE = "Data consolidada/df_nombres_duplicados_modificados_ciper.xlsx"
URL_COLUMN  = "Link"

df = pd.read_excel(INPUT_CSV)
df = df[df["Pagina"].isin(["CHILEREPUESTOS" ])] #, "MUNDOREPUESTOS" "CHILEREPUESTOS", 
nombres = []
total = len(df)

for idx, row in df.iterrows():
    url     = row[URL_COLUMN]
    dominio = urlparse(url).netloc.lower()
    rule    = config.get(dominio, {})

    # Por defecto usamos el valor original si ocurre cualquier excepción
    nombre_base = row.get("Nombre Producto", "").strip()
    name = nombre_base

    # ——— 3.1. Caso especial para mundorepuestos.com ——————————————
    if "mundorepuestos.com" in dominio:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            compat_a = soup.select_one("div.contCompatibilidad .detalle_modelo a")
            fragmento = ""
            if compat_a:
                texto = compat_a.get_text(strip=True)
                # Extraer cilindrada + rango de años, p.ej. "1.6L (2004 - 2010)"
                m = re.search(r"(\d+\.\d+L\s*\(\s*\d{4}\s*-\s*\d{4}\s*\))", texto)
                if m:
                    fragmento = m.group(1)

            if fragmento:
                name = f"{nombre_base} {fragmento}"
            # si no hay fragmento, queda el nombre_base

        except (ReadTimeout, RequestException) as e:
            print(f"⚠️  [Timeout/Error] fila {idx+1}: no se pudo procesar mundorepuestos.com → {url}")
            # name ya está asignado a nombre_base, se continúa

    # ——— 3.2. Caso especial para chilerepuestos.com ——————————————
    elif "chilerepuestos.com" in dominio:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            # Buscamos el <li> que contiene “Modelo:” dentro de .product-details-list
            modelo_texto = ""
            for li in soup.select("div.product-details-list ul li"):
                if li.get_text(strip=True).startswith("Modelo:"):
                    span = li.select_one("span")
                    if span:
                        modelo_texto = span.get_text(strip=True)
                    break

            # Tomamos las dos primeras palabras de 'modelo_texto' (p.ej. "SANTANA 1800")
            modelo_dos = ""
            if modelo_texto:
                palabras = modelo_texto.split()
                modelo_dos = " ".join(palabras[:2])  # Las dos primeras

            if modelo_dos:
                name = f"{nombre_base} {modelo_dos}"
            # si no hay modelo_dos, queda nombre_base

        except (ReadTimeout, RequestException) as e:
            print(f"⚠️  [Timeout/Error] fila {idx+1}: no se pudo procesar chilerepuestos.com → {url}")
            # name ya está asignado a nombre_base, se continúa

    else:
        # Si es tipo slug:
        if rule.get("type") == "slug":
            name = generar_slug_name(url)

        else:
            # Intentamos la petición genérica con CSS o custom
            try:
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

                # Formatear piezas en un solo nombre (marca – modelo – categoría – P.N.xxx)
                piezas = [
                    detalles.get("marca"),
                    detalles.get("modelo"),
                    detalles.get("categoría"),
                    detalles.get("num_parte") and f"P.N.{detalles['num_parte']}"
                ]
                piezas = [re.sub(r"[\s––]+", " ", p).strip() for p in piezas if p]
                if piezas:
                    name = " – ".join(piezas)

            except (ReadTimeout, RequestException) as e:
                print(f"⚠️  [Timeout/Error] fila {idx+1}: no se pudo procesar {dominio} → {url}")
                # name ya está asignado a nombre_base, se continúa

    nombres.append(name or nombre_base)

    if (idx + 1) % 50 == 0:
        print(f"→ Procesadas {idx+1} de {total} URLs")


#del df['Nombre Producto']
df['Nombres nuevos'] = nombres

df.to_excel(OUTPUT_FILE, index=False)
print(f"✅ Completado: procesadas {len(nombres)} de {total} filas. Salida en {OUTPUT_FILE}")
