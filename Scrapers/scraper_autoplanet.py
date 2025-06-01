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
url = 'https://www.autoplanet.cl/'
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
            wait = WebDriverWait(driver, 3)

            # Buscar input de búsqueda
            input_element = wait.until(EC.presence_of_element_located((By.ID, "smartSearchId")))
            input_element.clear()
            input_element.send_keys(texto_busqueda)
            input_element.send_keys(Keys.RETURN)

            time.sleep(2)  # Dejar cargar resultados

            try:
                # Esperar que aparezcan productos
                productos = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'deco-none')]")))

                if not productos:
                    print(f"No se encontraron productos para: {texto_busqueda}")
                    continue

                for producto in productos:
                    try:
                        # Link del producto
                        link_producto = producto.get_attribute('href')

                        # Nombre del producto
                        nombre_element = producto.find_element(By.XPATH, ".//p[contains(@class, 'title')]")
                        nombre_producto = nombre_element.text.strip()

                        # Precio del producto
                        try:
                            precio_element = producto.find_element(By.XPATH, ".//span[contains(@class, 'new-price')]")
                            precio_producto = precio_element.text.strip()
                        except NoSuchElementException:
                            precio_producto = "No disponible"

                        img_element = producto.find_element(By.XPATH, ".//img[contains(@class, 'img-plp')]")
                        img_url = img_element.get_attribute('src')

                        datos_completos.append({
                            'Nombre Producto': nombre_producto,
                            'Precio': precio_producto,
                            'Busqueda': texto_busqueda,
                            'Marca Buscada': marca,
                            'Modelo Buscado': modelo,
                            'Link': link_producto,
                            'Imagen': img_url
                        })

                    except Exception as e:
                        print(f"Error extrayendo producto individual: {e}")
                        continue

            except TimeoutException:
                print(f"No se encontraron productos para: {texto_busqueda}")
                continue

        except Exception as e:
            print(f"Error inesperado en búsqueda {texto_busqueda}: {e}")
            continue

# Guardar datos en Excel
df_final = pd.DataFrame(datos_completos).drop_duplicates()
os.makedirs('Data encontrada', exist_ok=True)
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel('Data encontrada/resultados_autoplanet.xlsx', index=False)
print("Datos guardados en 'Data encontrada/resultados_autoplanet_corregido.xlsx'")

# Guardar tiempo de ejecución
fin = time.time()
duracion = fin - inicio
duracion_legible = str(timedelta(seconds=int(duracion)))

with open('Data encontrada/tiempo_ejecucion_autoplanet.txt', 'w') as f:
    f.write(f"Tiempo total de ejecución: {duracion_legible}\n")
    f.write(f"Duración en segundos: {duracion:.2f} segundos\n")

# Cerrar navegador
driver.quit()
