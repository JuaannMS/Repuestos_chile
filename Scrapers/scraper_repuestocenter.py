import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime, timedelta

inicio = time.time()
fecha_hora_actual = datetime.now()


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


#SOLO BUSCAMOS POR MARCA Y NO POR MODELO, YA QUE LA PAGINA NO RETORNA DATA CON MUCHA ESPECIFICACION
def buscar_repuesto(repuesto, marca):
    query = f"{repuesto} {marca}".strip().replace(" ", "+")
    url = f"https://repuestocenter.cl/?s={query}&post_type=product"
    print(f"Buscando en: {url}")

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=15)

    # Parsear HTML
    soup = BeautifulSoup(response.text, "html.parser")
    productos = soup.select("div.product-grid-item.product")
    resultados = []

    for producto in productos:
        try:
            codigo = producto.get("data-id")
            nombre = producto.select_one("h3.wd-entities-title a").get_text(strip=True)
            link = producto.select_one("h3.wd-entities-title a")["href"]

            try:
                marca_prod = producto.select_one("span.attribute-label.product-label").get_text(strip=True)
            except:
                marca_prod = "No disponible"

            try:
                modelo = producto.select("div.modelo-attribute")[1].get_text(strip=True).replace("MODELO: ", "")
            except:
                modelo = "No disponible"

            try:
                precio = producto.select_one("span.woocommerce-Price-amount.amount").get_text(strip=True)
            except:
                precio = "No disponible"

            try:
                img_url = producto.select_one("img.attachment-woocommerce_thumbnail")["src"]
            except:
                img_url = ""

            resultados.append({
                'Nombre Producto': nombre,
                'Código': codigo,
                'Marca': marca_prod,
                'Modelo': modelo,
                'Precio': precio,
                'Marca Buscada': marca,
                'Texto Búsqueda': f"{repuesto} {marca}",
                'Link': link,
                'Imagen': img_url
            })

        except Exception as e:
            print(f"Error extrayendo producto: {e}")
            continue

    return resultados


repuestos = cargar_repuestos()
marcas = cargar_marcas()

datos_completos = []
for repuesto in repuestos:
    for marca in marcas:
        try:
            datos_completos.extend(buscar_repuesto(repuesto, marca))
        except Exception as e:
            print(f"Error en búsqueda '{repuesto} {marca}': {e}")
            continue

df_final = pd.DataFrame(datos_completos).drop_duplicates(subset=["Nombre Producto", "Link"])

os.makedirs('Data encontrada', exist_ok=True)
output_path = 'Data encontrada/resultados_repuestocenter.xlsx'
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel(output_path, index=False)
print(f"Datos guardados en '{output_path}'")

fin = time.time()
duracion = fin - inicio
duracion_legible = str(timedelta(seconds=int(duracion)))
with open('Data encontrada/tiempo_ejecucion_repuestocenter.txt', 'w') as f:
    f.write(f"Tiempo total de ejecucion: {duracion_legible}\n")
    f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")
