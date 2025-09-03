from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import urllib.parse  # <-- IMPORT NECESARIO PARA CODIFICAR LA URL

fecha_hora_actual = datetime.now()

# Guardar inicio de ejecución
inicio = time.time()

# Funciones para cargar inputs
def cargar_repuestos():
    df = pd.read_csv('Input Repuestos/input_repuestos.csv')
    return df['repuestos'].dropna().tolist()

def cargar_modelos_marcas():
    path = 'Modelos y marcas'
    modelos_marcas = []
    for archivo in os.listdir(path):
        if archivo.endswith('.csv'):
            df = pd.read_csv(os.path.join(path, archivo))
            modelos_marcas.extend(df.to_dict('records'))
    return modelos_marcas

# Configurar navegador
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# Ya no vamos a la página principal, sino que armamos la URL directamente en el bucle
# driver.get('https://www.salfarepuestos.cl/')
# time.sleep(3)

# Cargar inputs
repuestos = cargar_repuestos()
modelos_marcas = cargar_modelos_marcas()

datos_completos = []
for repuesto in repuestos:
    for modelo_marca in modelos_marcas:
        marca_text = modelo_marca.get('marca', '')
        modelo_text = modelo_marca.get('modelo', '')
        texto_busqueda = f"{repuesto} {marca_text} {modelo_text}"
        print(f"Buscando: {texto_busqueda}")

        try:
            # 1) Codificamos el texto para la parte de la ruta
            ruta_codificada = urllib.parse.quote(texto_busqueda, safe='')
            # 2) Codificamos el texto para el parámetro _q (se usa quote_plus para espacios “+”)
            query_codificada = urllib.parse.quote_plus(texto_busqueda)

            # Construimos la URL completa (observa la sintaxis: /ruta_codificada?_q=query_codificada&map=ft)
            url_buscada = (
                f"https://www.salfarepuestos.cl/{ruta_codificada}"
                f"?_q={query_codificada}&map=ft"
            )

            # 3) Navegamos a esa URL directamente
            driver.get(url_buscada)

            # 4) Esperamos a que aparezcan los productos (ajusta el selector si fuera necesario)
            wait = WebDriverWait(driver, 10)
            # Aquí esperamos, por ejemplo, a que exista al menos un div con la clase de producto
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.vtex-search-result-3-x-galleryItem")
            ))

            # 5) Una vez cargados, extraemos todos los productos
            productos = driver.find_elements(By.CSS_SELECTOR, "div.vtex-search-result-3-x-galleryItem")
            if not productos:
                print(f"No se encontraron productos para: {texto_busqueda}")
                continue

            for producto in productos:
                # Nombre del producto
                nombre = producto.find_element(
                    By.CSS_SELECTOR,
                    ".vtex-product-summary-2-x-brandName"
                ).text.strip()

                # SKU
                sku = producto.find_element(
                    By.CSS_SELECTOR,
                    ".vtex-product-identifier-0-x-product-identifier__value"
                ).text.strip()

                # Precio listado (tachado) — puede no existir
                try:
                    precio_lista = producto.find_element(
                        By.CSS_SELECTOR,
                        ".vtex-product-price-1-x-listPriceValue"
                    ).text.strip()
                except NoSuchElementException:
                    precio_lista = ""

                # Precio actual
                try:
                    precio_actual = producto.find_element(
                        By.CSS_SELECTOR,
                        ".vtex-product-price-1-x-sellingPriceValue"
                    ).text.strip()
                except NoSuchElementException:
                    precio_actual = ""

                # Link
                link = producto.find_element(
                    By.CSS_SELECTOR,
                    "a.vtex-product-summary-2-x-clearLink"
                ).get_attribute("href")

                # Imagen
                try:
                    img_url = producto.find_element(
                        By.CSS_SELECTOR,
                        "img.vtex-product-summary-2-x-image"
                    ).get_attribute("src")
                except NoSuchElementException:
                    img_url = ""

                datos_completos.append({
                    'Nombre Producto': nombre,
                    'SKU': sku,
                    'Precio Normal': precio_lista,
                    'Precio': precio_actual,
                    'Marca Buscada': marca_text,
                    'Modelo Buscado': modelo_text,
                    'Texto Búsqueda': texto_busqueda,
                    'Link': link,
                    'Imagen': img_url,
                })

        except Exception as e:
            print(f"Error inesperado en búsqueda '{texto_busqueda}': {e}")
            continue

# # Guardar datos en Excel
# df_final = pd.DataFrame(datos_completos).drop_duplicates()
# os.makedirs('Data encontrada', exist_ok=True)
# output_path = 'Data encontrada/resultados_salfarepuestos.xlsx'
# df_final['fecha_carga'] = fecha_hora_actual
# df_final.to_excel(output_path, index=False)
# print(f"Datos guardados en '{output_path}'")

# # Guardar tiempo de ejecución
# fin = time.time()
# duracion = fin - inicio
# duracion_legible = str(timedelta(seconds=int(duracion)))
# with open('Data encontrada/tiempo_ejecucion_salfarepuestos.txt', 'w') as f:
#     f.write(f"Tiempo total de ejecucion: {duracion_legible}\n")
#     f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")

# # Cerrar navegador
# driver.quit()
