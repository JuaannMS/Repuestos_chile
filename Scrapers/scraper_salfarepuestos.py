from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, timedelta

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


url = 'https://www.salfarepuestos.cl/'
driver.get(url)
time.sleep(3)

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
            wait = WebDriverWait(driver, 10)

            # Buscar input de búsqueda
            input_element = wait.until(EC.visibility_of_element_located((By.XPATH,
                "//input[@placeholder='Ingresa lo que deseas encontrar']")))
            input_element.click()
            input_element.send_keys(Keys.CONTROL, 'a')
            input_element.send_keys(Keys.DELETE)
            input_element.send_keys(texto_busqueda)
            input_element.send_keys(Keys.RETURN)

            time.sleep(1.5)

            productos = driver.find_elements(By.CSS_SELECTOR, "div.vtex-search-result-3-x-galleryItem")
            if not productos:
                print(f"No se encontraron productos para: {texto_busqueda}")
                continue

            for producto in productos:
                
                # Nombre del producto
                nombre = producto.find_element(By.CSS_SELECTOR, ".vtex-product-summary-2-x-brandName").text.strip()

                # SKU
                sku = producto.find_element(By.CSS_SELECTOR, ".vtex-product-identifier-0-x-product-identifier__value").text.strip()

                # Precio listado (tachado) — puede no existir
                try:
                    precio_lista = producto.find_element(By.CSS_SELECTOR, ".vtex-product-price-1-x-listPriceValue").text.strip()
                except NoSuchElementException:
                    precio_lista = ""

                # Precio actual
                try:
                    precio_actual = producto.find_element(By.CSS_SELECTOR, ".vtex-product-price-1-x-sellingPriceValue").text.strip()
                except NoSuchElementException:
                    precio_actual = ""

                # Link
                link = producto.find_element(By.CSS_SELECTOR, "a.vtex-product-summary-2-x-clearLink").get_attribute("href")

                # Imagen
                try:
                    img_url = producto.find_element(By.CSS_SELECTOR, "img.vtex-product-summary-2-x-image").get_attribute("src")
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


# Guardar datos en Excel
df_final = pd.DataFrame(datos_completos).drop_duplicates()
os.makedirs('Data encontrada', exist_ok=True)
output_path = 'Data encontrada/resultados_salfarepuestos.xlsx'
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel(output_path, index=False)
print(f"Datos guardados en '{output_path}'")

# Guardar tiempo de ejecución
fin = time.time()
duracion = fin - inicio
duracion_legible = str(timedelta(seconds=int(duracion)))
with open('Data encontrada/tiempo_ejecucion_salfarepuestos.txt', 'w') as f:
    f.write(f"Tiempo total de ejecucion: {duracion_legible}\n")
    f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")

# Cerrar navegador
driver.quit()
