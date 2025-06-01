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
import time
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

# Configurar opciones del navegador
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')

# Inicializar el WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# URL base
driver.get('https://chilerepuestos.com/')
time.sleep(3)

boton_cerrar = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CLASS_NAME, "swal2-close"))
)
boton_cerrar.click()

time.sleep(1)


# Cargar inputs
repuestos = cargar_repuestos()
modelos_marcas = cargar_modelos_marcas()
# print(modelos_marcas)

datos_completos = []

for repuesto in repuestos:
    for modelo_marca in modelos_marcas:
        marca = modelo_marca.get('marca', '')
        modelo = modelo_marca.get('modelo', '')
        generacion = str(modelo_marca.get('generacion', ''))
        anos = modelo_marca.get('anos', '')

        texto_busq = f"{repuesto} {marca} {modelo}"

        # Construir query URL-friendly
        query = "+".join(texto_busq.split())
        # Si quieres recorrer varias páginas, puedes variar el número en lugar de 1
        page = 1
        search_url = f"https://chilerepuestos.com/{page}/search?Buscar={query}"


        try:

            driver.get(search_url)

            try:
                productos_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//div[contains(@class, 'shop-single-item')]")
                    )
                )
            except TimeoutException:
                print(f"No se encontraron productos para: {texto_busq}")
                continue  

            for producto in productos_element:
                # 🔥 Buscar directamente sin try-except individuales
                link_element = producto.find_element(By.XPATH, ".//div[@class='product-img']/a")
                href = link_element.get_attribute('href')

                marca_producto = producto.find_element(By.XPATH, ".//div[@class='product-card__badges']/div[contains(@class, 'tag-badge--sale')]").text.strip()
                nombre_producto = producto.find_element(By.XPATH, ".//div[@class='product-content']/h2/a").text.strip()
                descripcion_producto = producto.find_element(By.XPATH, ".//div[@class='product-content']/div").text.strip()
                precio_producto = producto.find_element(By.XPATH, ".//div[@class='pro-price']/span[contains(@class, 'new-price')]").text.strip()
                codigo_producto = producto.find_element(By.XPATH, ".//a[contains(@class, 'add-to-wishlist')]").text.strip()

                img_el   = producto.find_element(By.CLASS_NAME, "primary-img")
                src      = img_el.get_attribute("src")              # puede ser "/img/…"
                if src.startswith("/"):
                    img_url = "https://chilerepuestos.com" + src
                else:
                    img_url = src

                # Solo guardar si hay descripción válida
                if descripcion_producto and descripcion_producto.strip() not in ["", "Sin descripción"]:
                    datos_completos.append({
                        'Marca Producto': marca_producto,
                        'Descripción': descripcion_producto,
                        'Nombre Producto': nombre_producto,
                        'Precio': precio_producto,
                        'Busqueda': texto_busq,
                        'Marca Buscada': marca,
                        'Modelo Buscado': modelo,
                        'Link': href,
                        'Imagen': img_url,

                    })

        except Exception as e:
            # captura cualquier otro error y continúa
            print(f"Error en búsqueda {texto_busq}: {e}")
            continue

     

# Guardar datos en CSV  

#
df_final = pd.DataFrame(datos_completos).drop_duplicates()
os.makedirs('Data encontrada', exist_ok=True)
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel('Data encontrada/resultados_chilerepuestos.xlsx', index=False)
print("Datos guardados en 'Data encontrada/resultados_chilerepuestos.xlsx'")

# Guardar tiempo de ejecución
fin = time.time()
duracion = fin - inicio
duracion_legible = str(timedelta(seconds=int(duracion)))
with open('Data encontrada/tiempo_ejecucion_chilerepuestos.txt', 'w') as f:
    f.write(f"Tiempo total de ejecucion: {duracion_legible}\n")
    f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")

# Cerrar navegador
driver.quit()

