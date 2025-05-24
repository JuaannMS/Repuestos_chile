from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import re

fecha_hora_actual = datetime.now()

# Guardar inicio de ejecución
inicio = time.time()


def extraer_precios(texto):
    # Buscar precios con regex
    precios_encontrados = re.findall(r'\$?\s?[\d.,]+', str(texto))
    precios_limpios = [re.sub(r'[^\d]', '', p) for p in precios_encontrados]

    if len(precios_limpios) >= 2:
        return pd.Series([precios_limpios[0], precios_limpios[1]])
    elif len(precios_limpios) == 1:
        return pd.Series([precios_limpios[0], precios_limpios[0]])
    else:
        return pd.Series([None, None])



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
url = 'https://www.takora.cl/autos/repuestos/'
driver.get(url)
time.sleep(3)

# Cargar inputs
repuestos = cargar_repuestos()
modelos_marcas = cargar_modelos_marcas()

datos_completos = []
from selenium.common.exceptions import TimeoutException, NoSuchElementException

for repuesto in repuestos:
    for modelo_marca in modelos_marcas:
        marca = modelo_marca.get('marca', '')
        modelo = modelo_marca.get('modelo', '')
        generacion = str(modelo_marca.get('generacion', ''))
        anos = modelo_marca.get('anos', '')

        texto_busqueda = f"{repuesto} {marca} {modelo}"
        query = "+".join(texto_busqueda.split())
        url = f"https://www.takora.cl/autos/repuestos/advanced_search_result.php?keywords={query}"

        try:
            driver.get(url)
            wait = WebDriverWait(driver, 3)
            time.sleep(2)  # Dejar que cargue

            try:
                productos = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//td[contains(@class,'productListing-data')]"))
                )

                if not productos:
                    print(f"No se encontraron productos para: {texto_busqueda}")
                    continue

                for producto in productos:
                    links_info = producto.find_elements(By.XPATH, ".//a[contains(@href,'product_info.php')]")

                    if len(links_info) >= 2:
                        name_link = links_info[1]
                    elif links_info:
                        name_link = links_info[0]
                    else:
                        continue

                    nombre = name_link.text.strip()
                    link = name_link.get_attribute('href')

                    try:
                        img_el = producto.find_element(By.XPATH, ".//img")
                        img_src = img_el.get_attribute("src")
                        # Convertir a URL completa si es relativa
                        if img_src.startswith("http"):
                            img_url = img_src
                        else:
                            img_url = "https://www.takora.cl/autos/repuestos/" + img_src.lstrip("/")
                    except NoSuchElementException:
                        img_url = ''

                    try:
                        precio_txt = producto.find_element(By.CLASS_NAME, 'Price_listing').text.strip()
                    except NoSuchElementException:
                        precio_txt = ''

                    try:
                        oem = producto.find_element(By.CLASS_NAME, 'OEM_listing').text.replace('OEM:', '').strip()
                    except NoSuchElementException:
                        oem = ''

                    try:
                        fabricante = producto.find_element(By.CLASS_NAME, 'Manufacturer_listing').text.strip()
                    except NoSuchElementException:
                        fabricante = ''

                    datos_completos.append({
                        'Busqueda': texto_busqueda,
                        'Nombre Producto': nombre,
                        'Precio': precio_txt,
                        'OEM': oem,
                        'Marca Fabricante': fabricante,
                        'Marca Buscada': marca,
                        'Modelo Buscado': modelo,
                        'Link': link,
                        'Imagen' : img_url
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
output_path = 'Data encontrada/resultados_takora.xlsx'

# df_final = pd.read_excel('C:/Users/jmmsa/OneDrive/Escritorio/Scraper Repuestos/Data encontrada/resultados_takora.xlsx')
# df_final.rename(columns={'Precio': 'Precio Normal', 'Precio Normal': 'Precio'}, inplace=True)

# # Aplicar la función a df_final['Precio']
# df_final[['Precio Normal', 'Precio']] = df_final['Precio'].apply(extraer_precios)

df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel(output_path, index=False)
print(f"Datos guardados en '{output_path}'")

# Guardar tiempo de ejecución
fin = time.time()
duracion = fin - inicio
duracion_legible = str(timedelta(seconds=int(duracion)))
with open('Data encontrada/tiempo_ejecucion_takora.txt', 'w') as f:
    f.write(f"Tiempo total de ejecución: {duracion_legible}\n")
    f.write(f"Duración en segundos: {duracion:.2f} segundos\n")

# Cerrar navegador
driver.quit()
