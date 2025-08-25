import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime, timedelta

#MARCAS NO CONOCIDAS
fecha_hora_actual = datetime.now()

# ==============================
# Funciones para cargar inputs
# ==============================
def cargar_repuestos():
    df = pd.read_csv('Input Repuestos/input_repuestos.csv')
    return df['repuestos'].dropna().tolist()

def cargar_marcas():
    path = 'Modelos y marcas'
    marcas = []
    for archivo in os.listdir(path):
        if archivo.endswith('.csv'):
            marca = os.path.splitext(archivo)[0]
            marcas.append(marca)
    return marcas

# ==============================
# Función de scraping
# ==============================
def buscar_repuesto(repuesto):
    texto_busqueda = f"{repuesto}"
    query = texto_busqueda.strip().replace(" ", "+")
    url = f"https://tienda.repuestosexpress.cl/busqueda?q={query}&search-button=&lang=es_CL"
    print(f"Buscando en: {url}")

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=15)

    if response.status_code != 200:
        print(f"❌ Error {response.status_code} en la búsqueda {texto_busqueda}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    productos = soup.select("div.product")
    resultados = []

    if not productos:
        print(f"No se encontraron productos para: {texto_busqueda}")
        return resultados

    for producto in productos:
        try:
            # Código
            codigo = producto.get("data-pid")

            # Nombre
            try:
                nombre = producto.select_one("div.pdp-link a.link").get_text(strip=True)
            except:
                nombre = "No disponible"

            # Marca
            try:
                marca_prod = producto.select_one("div.tile-brand span").get_text(strip=True)
            except:
                marca_prod = "No disponible"

            # Precio
            try:
                precio = producto.select_one("span.sales .value").get_text(strip=True)
            except:
                precio = "No disponible"

            # Link
            try:
                link_element = producto.select_one("div.pdp-link a.link")
                href = link_element["href"]
                if href.startswith("/"):
                    link = f"https://tienda.repuestosexpress.cl{href}"
                else:
                    link = href
            except:
                link = ""

            # Imagen
            try:
                img_url = producto.select_one("img.tile-image")["src"]
            except:
                img_url = ""

            resultados.append({
                'Nombre Producto': nombre,
                'Código': codigo,
                'Marca': marca_prod,
                'Precio': precio,
                'Texto Búsqueda': texto_busqueda,
                'Link': link,
                'Imagen': img_url
            })

        except Exception as e:
            print(f"⚠️ Error extrayendo producto: {e}")
            continue

    return resultados

# ==============================
# Main
# ==============================
repuestos = cargar_repuestos()
marcas = cargar_marcas()

datos_completos = []
for repuesto in repuestos:
    #for marca in marcas:
    try:
        datos_completos.extend(buscar_repuesto(repuesto))
    except Exception as e:
        print(f"⚠️ Error inesperado en búsqueda '{repuesto}': {e}")
        continue

# Convertir a DataFrame y limpiar duplicados
df_final = pd.DataFrame(datos_completos).drop_duplicates(subset=["Nombre Producto", "Link"])

# Guardar datos en Excel
os.makedirs('Data encontrada', exist_ok=True)
output_path = 'Data encontrada/resultados_repuestosexpress.xlsx'
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel(output_path, index=False)
print(f"✅ Datos guardados en '{output_path}'")

# Guardar tiempo de ejecución
fin = time.time()
duracion = fin - inicio
duracion_legible = str(timedelta(seconds=int(duracion)))
with open('Data encontrada/tiempo_ejecucion_repuestosexpress.txt', 'w') as f:
    f.write(f"Tiempo total de ejecucion: {duracion_legible}\n")
    f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")
