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
url = 'https://cichile.cl'
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
            # Armar URL para CI Chile
            query = texto_busqueda.strip().replace(' ', '+')
            search_url = f"https://cichile.cl/?s={query}&post_type=product&dgwt_wcas=1"
            driver.get(search_url)

            time.sleep(5)
            wait = WebDriverWait(driver, 10)
            productos = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product")))

            if not productos:
                print(f"No se encontraron productos para: {texto_busqueda}")
                continue

            for producto in productos:
                try:
                    # Obtener código del producto
                    codigo = producto.get_attribute("data-pid")
                    
                    # Obtener nombre del producto
                    nombre = producto.find_element(By.CSS_SELECTOR, "div.pdp-link a.link").text.strip()
                    
                    # Obtener marca
                    marca = producto.find_element(By.CSS_SELECTOR, "div.tile-brand span").text.strip()
                    
                    # Obtener precio
                    try:
                        precio = producto.find_element(By.CSS_SELECTOR, "span.sales .value").text.strip()
                    except NoSuchElementException:
                        precio = "No disponible"
                    
                    # Obtener link del producto
                    link_element = producto.find_element(By.CSS_SELECTOR, "div.pdp-link a.link")
                    href = link_element.get_attribute("href")
                    if href.startswith('/'):
                        link = f"https://tienda.repuestosexpress.cl{href}"
                    else:
                        link = href
                    
                    # Obtener imagen
                    try:
                        img = producto.find_element(By.CSS_SELECTOR, "img.tile-image")
                        img_url = img.get_attribute("src")
                    except:
                        img_url = ""

                    datos_completos.append({
                        'Nombre Producto': nombre,
                        'Código': codigo,
                        'Marca': marca,
                        'Precio': precio,
                        'Marca Buscada': marca_text,
                        'Modelo Buscado': modelo_text,
                        'Texto Búsqueda': texto_busqueda,
                        'Link': link,
                        'Imagen': img_url
                    })

                except Exception as e:
                    print(f"Error extrayendo producto: {e}")
                    continue

        except Exception as e:
            print(f"Error inesperado en búsqueda '{texto_busqueda}': {e}")
            continue




df_final = pd.DataFrame(datos_completos).drop_duplicates(subset=["Nombre Producto", "Link"])
# Guardar datos en Excel
os.makedirs('Data encontrada', exist_ok=True)
output_path = 'Data encontrada/resultados_cichile.xlsx'
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel(output_path, index=False)
print(f"Datos guardados en '{output_path}'")

# Guardar tiempo de ejecución
fin = time.time()
duracion = fin - inicio
duracion_legible = str(timedelta(seconds=int(duracion)))
with open('Data encontrada/tiempo_ejecucion_cichile.txt', 'w') as f:
    f.write(f"Tiempo total de ejecucion: {duracion_legible}\n")
    f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")

# Cerrar navegador
driver.quit()