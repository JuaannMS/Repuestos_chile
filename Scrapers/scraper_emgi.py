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
import json
import re
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

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
            # Armar URL
            query = texto_busqueda.strip().replace(' ', '+')
            search_url = f"https://emgi.cl/search?type=product&q={query}"
            driver.get(search_url)

            wait = WebDriverWait(driver, 3)
            productos = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.col-12.col-sm-6.col-md-4.col-lg-3")))

            if not productos:
                print(f"No se encontraron productos para: {texto_busqueda}")
                continue

            for producto in productos:
                try:
                    nombre = producto.find_element(By.CSS_SELECTOR, ".product-card__name").text.strip()
                    link = producto.find_element(By.CSS_SELECTOR, ".product-card__name").get_attribute("href")

                    
                    contenedor_precio = producto.find_element(By.CSS_SELECTOR, "div.product-card__price")    
                    
                    # Buscar todos los precios en formato $xx.xxx
                    precios_encontrados = re.findall(r"\$\d{1,3}(?:\.\d{3})*", contenedor_precio.text)
                    precio_actual = precios_encontrados[0] if len(precios_encontrados) > 0 else ""
                    precio_normal = precios_encontrados[1] if len(precios_encontrados) > 1 else ""


                    try:
                        img = producto.find_element(By.CSS_SELECTOR, ".product-card__image img")
                        srcset = img.get_attribute("srcset")
                        img_url = srcset.split(",")[-1].split()[0] if srcset else img.get_attribute("src")
                    except:
                        img_url = ""

                    try:
                        script = producto.find_element(By.CSS_SELECTOR, "script[type='application/json']").get_attribute("innerHTML")
                        json_data = json.loads(script)
                        sku = json_data["variants"][0].get("sku", "")
                    except:
                        sku = ""

                    datos_completos.append({
                        'Nombre Producto': nombre,
                        'SKU': sku,
                        'Precio': precio_actual,
                        'Precio Normal': precio_normal,
                        'Marca Buscada': marca_text,
                        'Modelo Buscado': modelo_text,
                        'Texto Búsqueda': texto_busqueda,
                        'Link': link,
                        'Imagen': img_url,
                    })

                except Exception as e:
                    print(f"Error extrayendo producto: {e}")
                    continue

        except Exception as e:
            print(f"Error inesperado en búsqueda '{texto_busqueda}': {e}")
            continue



# Guardar datos en Excel
df_final = pd.DataFrame(datos_completos).drop_duplicates(subset=["Nombre Producto", "SKU"])
df_final = pd.DataFrame(df_final).drop_duplicates(subset=["Nombre Producto", "Link"])
os.makedirs('Data encontrada', exist_ok=True)
output_path = 'Data encontrada/resultados_emgi.xlsx'
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel(output_path, index=False)
print(f"Datos guardados en '{output_path}'")

# Guardar tiempo de ejecución
fin = time.time()
duracion = fin - inicio
duracion_legible = str(timedelta(seconds=int(duracion)))
with open('Data encontrada/tiempo_ejecucion_emgi.txt', 'w') as f:
    f.write(f"Tiempo total de ejecucion: {duracion_legible}\n")
    f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")

# Cerrar navegador
driver.quit()