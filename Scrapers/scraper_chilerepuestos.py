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
from selenium.common.exceptions import NoSuchElementException
import time
from datetime import datetime

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

        texto_busqueda = f"{repuesto} {marca} {modelo}"

        try:
            # Ingresar texto en input de búsqueda
            input_busqueda = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, 'Buscador'))
            )
            input_busqueda.clear()
            input_busqueda.send_keys(texto_busqueda)

            # Clic en el botón de búsqueda
            boton_buscar = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-default btn-lg']"))
            )
            boton_buscar.click()

            # Esperar resultados
            time.sleep(2)

            try:
                productos_element = WebDriverWait(driver, 3).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'shop-single-item')]"))
                )

                for producto in productos_element:
                    # 🔥 Buscar directamente sin try-except individuales
                    link_element = producto.find_element(By.XPATH, ".//div[@class='product-img']/a")
                    href = link_element.get_attribute('href')

                    marca_producto = producto.find_element(By.XPATH, ".//div[@class='product-card__badges']/div[contains(@class, 'tag-badge--sale')]").text.strip()
                    nombre_producto = producto.find_element(By.XPATH, ".//div[@class='product-content']/h2/a").text.strip()
                    descripcion_producto = producto.find_element(By.XPATH, ".//div[@class='product-content']/div").text.strip()
                    precio_producto = producto.find_element(By.XPATH, ".//div[@class='pro-price']/span[contains(@class, 'new-price')]").text.strip()
                    codigo_producto = producto.find_element(By.XPATH, ".//a[contains(@class, 'add-to-wishlist')]").text.strip()

                    # Solo guardar si hay descripción válida
                    if descripcion_producto and descripcion_producto.strip() not in ["", "Sin descripción"]:
                        datos_completos.append({
                            'Marca Producto': marca_producto,
                            'Descripción': descripcion_producto,
                            'Nombre Producto': nombre_producto,
                            'Precio': precio_producto,
                            'Busqueda': texto_busqueda,
                            'Marca Buscada': marca,
                            'Modelo Buscado': modelo,
                            'Generacion': generacion,
                            'Anos': anos,
                            'Link': href
                        })

            except NoSuchElementException:
                print(f"No se encontraron productos para: {texto_busqueda}")
                continue

        except Exception as e:
            print(f"Error en búsqueda {texto_busqueda}: {e}")
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
duracion_legible = str(datetime.timedelta(seconds=int(duracion)))

with open('Data encontrada/tiempo_ejecucion_chilerepuestos.txt', 'w') as f:
    f.write(f"Tiempo total de ejecucion: {duracion_legible}\n")
    f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")

# Cerrar navegador
driver.quit()

