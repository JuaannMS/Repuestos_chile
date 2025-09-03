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
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
 
 
# Guardar inicio de ejecución
inicio = time.time()
fecha_hora_actual = datetime.now()
 
 
# Configurar navegador
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
 
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
 
# Ir al sitio
url = 'https://www.autoplanet.cl/categoria/Repuestos/01?q=&page=0&sort='
driver.get(url)
time.sleep(3)
 
 
elemento = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '195')]"))
    )
 
    # Obtener el valor del componente
total_repuestos = elemento.text
 
total_repuestos = int(total_repuestos)
 
# Lista donde guardarás los datos
datos_completos = []
 
for i in range(1, total_repuestos + 1):
 
    url = f'https://www.autoplanet.cl/categoria/Repuestos/01?q=&page={i}&sort='
    driver.get(url)
    try:
        wait = WebDriverWait(driver, 10)
        productos = wait.until(
           EC.presence_of_all_elements_located(
               (By.CSS_SELECTOR, "div.product-item.card-plp")
           )
       )

        for producto in productos:
            try:
                # Subir al <a> para el link
                link_producto = producto.find_element(By.XPATH, "./ancestor::a").get_attribute("href")
        
                # Marca
                try:
                    marca = producto.find_element(By.XPATH, ".//p[contains(@class, 'mt-05')]").text.strip()
                except NoSuchElementException:
                    marca = "Sin marca"
        
                # Nombre
                try:
                    nombre = producto.find_element(By.XPATH, ".//p[contains(@class, 'title')]").text.strip()
                except NoSuchElementException:
                    nombre = "Sin nombre"
        
                # Precio nuevo
                try:
                    precio_actual = producto.find_element(By.XPATH, ".//span[contains(@class, 'new-price')]").text.strip()
                except NoSuchElementException:
                    precio_actual = "No disponible"
        
                # Precio anterior
                try:
                    precio_anterior = producto.find_element(By.XPATH, ".//span[contains(@class, 'old-price')]").text.strip()
                except NoSuchElementException:
                    precio_anterior = "No disponible"
        

        
                # Imagen
                try:
                    img_url = producto.find_element(By.XPATH, ".//img[contains(@class, 'img-plp')]").get_attribute("src")
                except NoSuchElementException:
                    img_url = "Sin imagen"
        
                datos_completos.append({
                    "Marca": marca,
                    "Nombre Producto": nombre,
                    "Precio": precio_actual,
                    "Link": link_producto,
                    "Imagen": img_url
                })
        
            except Exception as e:
                print(f"⚠️ Error en producto: {e}")
                continue

    except TimeoutException:
        print(f"⏳ No se encontraron productos en página {i}")
        continue
    

driver.quit()

    
df_final = pd.DataFrame(datos_completos).drop_duplicates()
os.makedirs('Data encontrada', exist_ok=True)
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel('Data encontrada/resultados_autoplanet2.xlsx', index=False)