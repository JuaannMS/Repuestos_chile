from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


# Configurar opciones del navegador
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')

# Inicializar el WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# URL de la página a analizar
url= 'https://www.ciper.cl/focos%20led%20mitsubishi%20l200?_q=Focos%20LED%20Mitsubishi%20L200&map=ft'
driver.get(url)

df_repuestos = pd.read_csv('repuestos_chile.csv')

time.sleep(3)

datos_completos = []


for index, row in df_repuestos.iterrows():
    texto_busqueda = f"{row['Repuesto']} {row['Modelo']} {row['Marca']}"
    
    wait = WebDriverWait(driver, 10)
    input_element = wait.until(EC.visibility_of_element_located((
        By.XPATH, "//input[@type='text' and @placeholder='Buscar']"
    )))

    input_element.send_keys(Keys.CONTROL + "a")
    input_element.send_keys(Keys.DELETE)

    # Escribir nueva búsqueda
    input_element.send_keys(texto_busqueda)
    input_element.send_keys(Keys.RETURN)
    time.sleep(3)

    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.visibility_of_element_located((
        By.XPATH, "//div[contains(@class, 'vtex-search-result-3-x-gallery')]"
    )))
    # Obtener el texto del elemento
    texto = element.text
    # print(texto)

    productos = texto.strip().split("AÑADIR AL CARRITO")
    for producto in productos:
        lineas = producto.strip().split('\n')
        if len(lineas) >= 2:
            nombre = lineas[0].strip()
            precio = ""
            for linea in lineas:
                if "$" in linea or "¢" in linea:
                    precio = linea.strip()
                    break

            datos_completos.append({
                'Nombre': nombre,
                'Precio': precio,
                'Busqueda': texto_busqueda
            })


df_resultados = pd.DataFrame(datos_completos)
df_resultados = df_resultados.drop_duplicates()
df_resultados.to_csv('resultados_ciper.csv', index=False)