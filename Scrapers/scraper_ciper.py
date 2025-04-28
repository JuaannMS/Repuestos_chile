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
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Guardar inicio de ejecución
inicio = time.time()

# Funciones para cargar inputs
def cargar_repuestos():
    df = pd.read_csv('Input Repuestos/input_repuestos.csv')
    return df['repuestos'].dropna().tolist()

def cargar_modelos_marcas():
    path = 'Modelos y marcas'
    archivos_encontrados = [archivo for archivo in os.listdir(path) if archivo.endswith('.csv')]
    archivos_a_leer = archivos_encontrados[:2]  # Solo los dos primeros archivos

    modelos_marcas = []
    for archivo in archivos_a_leer:
        archivo_path = os.path.join(path, archivo)
        df = pd.read_csv(archivo_path)
        modelos_marcas.extend(df.to_dict('records'))
    
    return modelos_marcas

# Configurar opciones del navegador
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')

# Inicializar el WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# Ir al sitio
driver.get('https://www.ciper.cl/')
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
            wait = WebDriverWait(driver, 5)

            # Buscar input de búsqueda
            input_element = wait.until(EC.visibility_of_element_located((
                By.XPATH, "//input[@type='text' and @placeholder='Buscar']"
            )))

            # Limpiar input anterior
            input_element.send_keys(Keys.CONTROL + "a")
            input_element.send_keys(Keys.DELETE)

            # Escribir nueva búsqueda
            input_element.send_keys(texto_busqueda)
            input_element.send_keys(Keys.RETURN)
            time.sleep(3)

            try:
                # Esperar la galería de productos
                gallery = wait.until(EC.visibility_of_element_located((
                    By.XPATH, "//div[contains(@class, 'vtex-search-result-3-x-gallery')]"
                )))

                # Capturar todos los productos <a>
                productos_links = gallery.find_elements(By.XPATH, ".//a[contains(@class, 'vtex-product-summary-2-x-clearLink')]")

                for producto in productos_links:
                    href = producto.get_attribute('href')
                    texto_producto = producto.text.strip().split('\n')

                    if len(texto_producto) >= 2:
                        nombre = texto_producto[0].strip()
                        precio = ""

                        for linea in texto_producto:
                            if "$" in linea or "¢" in linea:
                                precio = linea.strip()
                                break

                        datos_completos.append({
                            'Nombre Producto': nombre,
                            'Precio': precio,
                            'Busqueda': texto_busqueda,
                            'Marca Buscada': marca,
                            'Modelo Buscado': modelo,
                            'Generacion': generacion,
                            'Anos': anos,
                            'Link': href  # <-- Capturamos el link aquí
                        })

            except TimeoutException:
                print(f"No se encontraron productos para: {texto_busqueda}")
                continue

        except Exception as e:
            print(f"Error inesperado en búsqueda {texto_busqueda}: {e}")
            continue

# Guardar datos en CSV
df_resultados = pd.DataFrame(datos_completos).drop_duplicates()
os.makedirs('Data encontrada', exist_ok=True)
df_resultados.to_excel('Data encontrada/resultados_ciper.xlsx', index=False)
print("Datos guardados en 'Data encontrada/resultados_ciper.csv'")

# Guardar tiempo de ejecución
fin = time.time()
duracion = fin - inicio
duracion_legible = str(datetime.timedelta(seconds=int(duracion)))

with open('Data encontrada/tiempo_ejecucion_ciper.txt', 'w') as f:
    f.write(f"Tiempo total de ejecucion: {duracion_legible}\n")
    f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")

# Cerrar navegador
driver.quit()
