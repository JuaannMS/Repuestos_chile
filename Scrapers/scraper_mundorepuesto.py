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
driver.get('https://mundorepuestos.com/')
time.sleep(3)

# Esperar que el botón aparezca
wait = WebDriverWait(driver, 10)
boton_ok = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
boton_ok.click()

time.sleep(2)

# Cargar inputs
repuestos = cargar_repuestos()
modelos_marcas = cargar_modelos_marcas()

datos_completos = []



# Recorrer combinaciones de repuesto + modelo + marca
for repuesto in repuestos:
    for modelo_marca in modelos_marcas:
        marca = modelo_marca.get('marca', '')
        modelo = modelo_marca.get('modelo', '')
        generacion = str(modelo_marca.get('generacion', ''))
        anos = modelo_marca.get('anos', '')

        texto_busqueda = f"{repuesto} {marca} {modelo}"

        try:
            wait = WebDriverWait(driver, 3)

            # Buscar input
            input_busqueda = wait.until(EC.visibility_of_element_located((By.ID, 'txtBuscar')))
            input_busqueda.clear()
            input_busqueda.send_keys(texto_busqueda)

            # Clic en botón buscar
            boton_buscar = wait.until(EC.element_to_be_clickable((By.ID, 'btnBuscar')))
            boton_buscar.click()

            time.sleep(2)

            try:
                # Capturar todos los productos encontrados
                productos_links = WebDriverWait(driver, 3).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'linkVerPrd'))
                )

                for link_producto in productos_links:
                    href = link_producto.get_attribute('href')
                    datos_elemento = link_producto.text.strip().split('\n')

                    if len(datos_elemento) > 6:  # Producto válido
                        datos_completos.append({
                            'Código': datos_elemento[0].strip(),
                            'Nombre Producto': datos_elemento[1].strip(),
                            'Descripción': datos_elemento[2].strip(),
                            'Años Aplicación': datos_elemento[3].strip(),
                            'Marca Producto': datos_elemento[4].split(':')[1].strip() if ':' in datos_elemento[4] else '',
                            'Origen': datos_elemento[5].split(':')[1].strip() if ':' in datos_elemento[5] else '',
                            'Precio Oferta': datos_elemento[6].strip(),
                            'Precio Original': datos_elemento[8].strip() if len(datos_elemento) > 8 else '',
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
df_final = pd.DataFrame(datos_completos).drop_duplicates()
os.makedirs('Data encontrada', exist_ok=True)
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel('Data encontrada/resultados_mundorepuestos.xlsx', index=False)
print("Datos guardados en 'Data encontrada/resultados_mundorepuestos.xlsx'")

# Guardar tiempo de ejecución
fin = time.time()
duracion = fin - inicio
duracion_legible = str(datetime.timedelta(seconds=int(duracion)))

with open('Data encontrada/tiempo_ejecucion_mundorepuestos.txt', 'w') as f:
    f.write(f"Tiempo total de ejecucion: {duracion_legible}\n")
    f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")

# Cerrar navegador
driver.quit()
