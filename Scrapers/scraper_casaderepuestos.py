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
from selenium.common.exceptions import TimeoutException
from datetime import datetime

# Guardar inicio de ejecución
inicio = time.time()
fecha_hora_actual = datetime.now()

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
url = 'https://casaderepuestos.cl/'
driver.get(url)
time.sleep(3)

# Cargar inputs
repuestos = cargar_repuestos()
modelos_marcas = cargar_modelos_marcas()

datos_completos = []

for repuesto in repuestos:
    for modelo_marca in modelos_marcas:
        marca = modelo_marca.get('marca', '')
        modelo = modelo_marca.get('modelo', '')
        generacion = str(modelo_marca.get('generacion', ''))
        anos = modelo_marca.get('anos', '')

        texto_busqueda = f"{repuesto} {marca} {modelo}"

        try:
            wait = WebDriverWait(driver, 10)

            # Buscar input de búsqueda
            input_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "filter-search")))
            input_element.clear()
            input_element.send_keys(texto_busqueda)
            time.sleep(7)
            input_element.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.5)  # Pequeño tiempo para estabilidad
            input_element.send_keys(Keys.ENTER)

            time.sleep(3)

            try:
                productos = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "item")))

                if not productos:
                    print(f"No se encontraron productos para: {texto_busqueda}")
                    continue

                for producto in productos:
                    link = producto.find_element(By.CSS_SELECTOR, "a.pf-product").get_attribute('href')
                    nombre = producto.find_element(By.CSS_SELECTOR, "a.pf-product div").text.strip()
                    precio = producto.find_element(By.CSS_SELECTOR, "div.product-price span").text.strip()
                    oem = producto.find_element(By.CLASS_NAME, "cod-oem").text.strip()
                    fabricante = producto.find_element(By.CLASS_NAME, "brand").get_attribute('aria-label').strip()

                    datos_completos.append({
                        'Busqueda': texto_busqueda,
                        'Nombre Producto': nombre,
                        'Precio': precio,
                        'OEM': oem,
                        'Marca Fabricante': fabricante,
                        'Marca Buscada': marca,
                        'Modelo Buscado': modelo,
                        'Generacion': generacion,
                        'Anos': anos,
                        'Link': link
                    })

            except TimeoutException:
                print(f"No se encontraron productos para: {texto_busqueda}")
                continue

        except Exception as e:
            print(f"Error inesperado en búsqueda '{texto_busqueda}': {e}")
            continue

# Guardar datos en Excel
df_final = pd.DataFrame(datos_completos).drop_duplicates()
os.makedirs('Data encontrada', exist_ok=True)
output_path = 'Data encontrada/resultados_casaderepuestos.xlsx'
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel(output_path, index=False)
print(f"Datos guardados en '{output_path}'")

# Guardar tiempo de ejecución
fin = time.time()
duracion = fin - inicio
duracion_legible = str(datetime.timedelta(seconds=int(duracion)))
with open('Data encontrada/tiempo_ejecucion_casaderepuestos.txt', 'w') as f:
    f.write(f"Tiempo total de ejecución: {duracion_legible}\n")
    f.write(f"Duración en segundos: {duracion:.2f} segundos\n")

# Cerrar navegador
driver.quit()
