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

# Ir al sitio
url = 'https://ulti.cl/'
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

            # Buscar input de búsqueda (DESKTOP)
            input_element = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                '//*[@id="searchInput"]'   # ESTE es el correcto
            )))
            input_element.clear()
            input_element.send_keys(texto_busqueda)
            input_element.send_keys(Keys.RETURN)

            time.sleep(3)

            try:
                productos = driver.find_elements(By.CSS_SELECTOR, ".products-list__content .products-list__item")
                if not productos:
                    print(f"No se encontraron productos para: {texto_busqueda}")
                    continue

                for producto in productos:
                    try:
                        # Link del producto
                        link = producto.find_element(By.CSS_SELECTOR, ".product-card__image a").get_attribute("href")

                        try:
                            img_url = producto.find_element(By.CSS_SELECTOR, ".product-card__image img.image__tag").get_attribute("src")
                        except NoSuchElementException:
                            img_url = ''
                        
                        # Badges de marca y origen
                        marca_badge = producto.find_element(By.CSS_SELECTOR, ".product-card__badges .tag-badge--sale").text.strip()
                        origen_badge = producto.find_element(By.CSS_SELECTOR, ".product-card__badges .tag-badge--new").text.strip()
                        
                        # SKU
                        sku_text = producto.find_element(By.CSS_SELECTOR, ".product-card__meta").text
                        sku = sku_text.replace("SKU:", "").strip()
                        
                        # Nombre
                        nombre = producto.find_element(By.CSS_SELECTOR, ".product-card__name a").text.strip()
                        
                        # Precio
                        precio = producto.find_element(By.CSS_SELECTOR, ".product-card__price--current").text.strip()
                        
                        # Características y compatibilidad
                        lis = producto.find_elements(By.CSS_SELECTOR, ".product-card__features li")
                        textos = [li.text.strip() for li in lis]
                        # ... tu código de extracción ...
                        caracteristicas = textos[:-1]
                        compatibilidad = textos[-1] if textos else ""

                        # separar en dos partes por el primer espacio
                        parts = compatibilidad.split(' ', 1)
                        marca_compat = parts[0]
                        modelo_compat = parts[1] if len(parts) > 1 else ''

                        datos_completos.append({
                            'Marca Buscada': marca_badge,
                            'Origen': origen_badge,
                            'SKU': sku,
                            'Nombre Producto': nombre,
                            'Precio': precio,
                            'Características': "; ".join(caracteristicas),
                            'Marca Buscada': marca_compat,
                            'Modelo Buscado': modelo_compat,
                            'Link': link,
                            'Imagen': img_url
                        })

                    except Exception as e:
                        print(f"Error extrayendo producto individual: {e}")
                        continue

            except TimeoutException:
                print(f"No se cargaron productos para: {texto_busqueda}")
                continue

        except Exception as e:
            print(f"Error inesperado en búsqueda '{texto_busqueda}': {e}")
            continue

# Guardar datos en Excel
df_final = pd.DataFrame(datos_completos).drop_duplicates()
os.makedirs('Data encontrada', exist_ok=True)
output_path = 'Data encontrada/resultados_ulti.xlsx'
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel(output_path, index=False)
print(f"Datos guardados en '{output_path}'")

# Guardar tiempo de ejecución
fin = time.time()
duracion = fin - inicio
duracion_legible = str(timedelta(seconds=int(duracion)))
with open('Data encontrada/tiempo_ejecucion_ulti.txt', 'w') as f:
    f.write(f"Tiempo total de ejecucion: {duracion_legible}\n")
    f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")

# Cerrar navegador
driver.quit()
