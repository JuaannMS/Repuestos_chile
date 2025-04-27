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
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import datetime

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

# Configurar opciones del navegador
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')

# Inicializar el WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# URL de la página a analizar
url = 'https://www.autoplanet.cl/'
driver.get(url)

# Cargar repuestos y modelos/marcas
repuestos = cargar_repuestos()
modelos_marcas = cargar_modelos_marcas()

datos_completos = []

# Recorrer todas las combinaciones de repuesto + modelo + marca
for repuesto in repuestos:
    for modelo_marca in modelos_marcas:
        marca = modelo_marca.get('marca', '')
        modelo = modelo_marca.get('modelo', '')
        generacion = str(modelo_marca.get('generacion', ''))
        anos = modelo_marca.get('anos', '')

        # Preparar el texto de búsqueda
        texto_busqueda = f"{repuesto} {marca} {modelo}"
        
        input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "smartSearchId"))
        )
        input_element.clear()
        time.sleep(1)
        input_element.send_keys(texto_busqueda)
        input_element.send_keys(Keys.RETURN)
        time.sleep(1)

        # Inicia el while
        while True:
            try:
                element = driver.find_element(By.XPATH, '//*[@id="productSearchAutomootive"]/div/div/app-plp-grid/div[3]')
                texto = element.text

                productos = texto.strip().split("\n\n")

                for producto in productos:
                    lineas = producto.strip().split('\n')
                    if len(lineas) >= 2:
                        marca_producto = lineas[0].strip()
                        nombre = lineas[1].strip()
                        precio = lineas[-1].strip()

                        datos_completos.append({
                            'Marca Producto': marca_producto,
                            'Nombre Producto': nombre,
                            'Precio': precio,
                            'Busqueda': texto_busqueda
                        })

                
                break

            except Exception as e:
                print(f"Error inesperado dentro del while: {e}")
                break


# Guardar fin
fin = time.time()
duracion = fin - inicio
duracion_legible = str(datetime.timedelta(seconds=int(duracion)))

with open('Data encontrada/tiempo_ejecucion.txt', 'w') as f:
    f.write(f"Tiempo total de ejecucinn: {duracion_legible}\n")
    f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")

# Guardar los datos recolectados
df_resultados = pd.DataFrame(datos_completos)
df_resultados.to_csv('Data encontrada/resultados_autoplanet.csv', index=False)

# Cerrar navegador
driver.quit()
