from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Fecha y hora de carga
fecha_hora_actual = datetime.now()

# Guardar inicio de ejecución
inicio = time.time()

# Funciones para cargar inputs
def cargar_repuestos():
    df = pd.read_csv('Input Repuestos/input_repuestos.csv')
    return df['repuestos'].dropna().tolist()

def cargar_modelos_marcas():
    path = 'Modelos y marcas'
    archivos = [f for f in os.listdir(path) if f.endswith('.csv')]
    #archivos = archivos[:2]  # solo los dos primeros
    records = []
    for archivo in archivos:
        df = pd.read_csv(os.path.join(path, archivo))
        records.extend(df.to_dict('records'))
    return records

# Configurar WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()),
    options=options
)

# Navegar a la página y cerrar alerta
driver.get('https://mundorepuestos.com/')
time.sleep(3)
wait = WebDriverWait(driver, 10)
boton_ok = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
boton_ok.click()
time.sleep(2)

# Cargar datos de entrada
repuestos = cargar_repuestos()
modelos_marcas = cargar_modelos_marcas()
datos_completos = []
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Bucle principal
for repuesto in repuestos:
    for mm in modelos_marcas:
        marca = mm.get('marca', '')
        modelo = mm.get('modelo', '')
        generacion = str(mm.get('generacion', ''))
        anos = mm.get('anos', '')

        texto_busqueda = f"{repuesto} {marca} {modelo}"
        try:
            wait_short = WebDriverWait(driver, 5)

            # Buscar y escribir en el input
            inp = wait_short.until(EC.visibility_of_element_located((By.ID, 'txtBuscar')))
            inp.clear()
            inp.send_keys(texto_busqueda)

            # Clic en buscar
            btn = wait_short.until(EC.element_to_be_clickable((By.ID, 'btnBuscar')))
            btn.click()
            time.sleep(2)

            try:
                productos_links = wait_short.until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'linkVerPrd'))
                )

                for link in productos_links:
                    href = link.get_attribute('href')

                    # SUBIR 2 NIVELES desde <a class="linkVerPrd"> → div.producto → td → tr
                    fila = link.find_element(By.XPATH, "./ancestor::tr")

                    # Buscar imagen dentro de la columna 'col-img-productoDesk' en esa fila
                    try:
                        img_el = fila.find_element(By.XPATH, ".//td[contains(@class, 'col-img-productoDesk')]//img")
                        img_url = img_el.get_attribute('src')
                    except NoSuchElementException:
                        img_url = ''

                    # Extraer datos del producto desde el contenedor
                    container = link.find_element(By.XPATH, ".//div[@id='datos-producto']")

                    try:
                        codigo = container.find_element(By.CSS_SELECTOR, "p.codigo_producto").text
                    except NoSuchElementException:
                        codigo = ''

                    try:
                        nombre = container.find_element(By.CSS_SELECTOR, "span.titulo-producto").text
                    except NoSuchElementException:
                        nombre = ''

                    spans = container.find_elements(By.XPATH, "./span")
                    descripcion = spans[1].text if len(spans) > 1 else ''

                    try:
                        anos_aplic = container.find_element(By.CSS_SELECTOR, "span.years").text
                    except NoSuchElementException:
                        anos_aplic = ''

                    try:
                        marca_prod = container.find_element(By.CSS_SELECTOR, "span.nameMarca").text
                    except NoSuchElementException:
                        marca_prod = ''

                    try:
                        origen = container.find_element(By.CSS_SELECTOR, "span.productoOrigen").text
                    except NoSuchElementException:
                        origen = ''

                    try:
                        precio_original = container.find_element(By.CSS_SELECTOR, "span.precio_original").text
                    except NoSuchElementException:
                        precio_original = ''

                    precio_oferta = link.get_attribute("data-priceoffer") or ''

                    datos_completos.append({
                        'Código':           codigo,
                        'Nombre Producto':  nombre,
                        'Descripción':      descripcion,
                        'Años Aplicación':  anos_aplic,
                        'Marca Producto':   marca_prod,
                        'Origen':           origen,
                        'Precio Oferta':    precio_oferta,
                        'Precio Original':  precio_original,
                        'Busqueda':         texto_busqueda,
                        'Marca Buscada':    marca,
                        'Modelo Buscado':   modelo,
                        'Link':             href,
                        'Imagen':           img_url
                    })

            except TimeoutException:
                print(f"No se encontraron productos para: {texto_busqueda}")
                continue

        except Exception as e:
            print(f"Error inesperado en búsqueda {texto_busqueda}: {e}")
            continue


# Guardar resultados
df_final = pd.DataFrame(datos_completos).drop_duplicates()
os.makedirs('Data encontrada', exist_ok=True)
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel('Data encontrada/resultados_mundorepuestos.xlsx', index=False)
print("Datos guardados en 'Data encontrada/resultados_mundorepuestos.xlsx'")

# Guardar tiempo de ejecución
fin = time.time()
dur = fin - inicio
with open('Data encontrada/tiempo_ejecucion_mundorepuestos.txt', 'w') as f:
    f.write(f"Tiempo total de ejecución: {str(timedelta(seconds=int(dur)))}\n")
    f.write(f"Duración en segundos: {dur:.2f}\n")

# Cerrar driver
driver.quit()
