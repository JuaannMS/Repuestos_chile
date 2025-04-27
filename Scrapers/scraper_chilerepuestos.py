# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# import pandas as pd
# import time

# # Configurar opciones del navegador
# options = webdriver.ChromeOptions()
# options.add_argument('--start-maximized')

# # Inicializar el WebDriver
# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# # URL de la página a analizar
# url = 'https://chilerepuestos.com'
# driver.get(url)

# time.sleep(5)

# url = 'https://chilerepuestos.com/1/search?Buscar=Bomba+de+agua+Hyundai+Santa+Fe'
# driver.get(url)

# # Cargar el CSV
# df_repuestos = pd.read_csv('repuestos_chile.csv')



# for index, row in df_repuestos.iterrows():
#     # Construir el texto de búsqueda
#     texto_busqueda = f"{row['Repuesto']} {row['Modelo']} {row['Marca']}"

#     # Ingresar el texto en el input de búsqueda
#     input_busqueda = driver.find_element(By.ID, 'Buscador')
#     input_busqueda.clear()
#     input_busqueda.send_keys(texto_busqueda)

#     # Clic en el botón de búsqueda
#     boton_buscar = driver.find_element(By.XPATH, "//button[@class='btn btn-default btn-lg']")
#     boton_buscar.click()

#     time.sleep(1)
#     datos_completos = []
#     try:
#         productos = driver.find_element(By.XPATH, '//*[@id="shop-grid"]/div').text
#         # Separar por bloques de productos
#         for producto in productos.split('COMPRAR'):
#             lineas = producto.strip().split('\n')
            
#             if len(lineas) >= 6:
#                 datos_completos.append({
#                     'Marca': lineas[0].strip(),
#                     'Nombre': lineas[1].strip(),
#                     'Descripción': lineas[2].strip(),
#                     'Precio': lineas[-3].strip(),
#                     'Código': lineas[-1].strip()
#                 })

#     except Exception as e:
#         print(f"Error al extraer el contenido del componente: {e}")


# # Crear un DataFrame final con todos los datos
# df_final = pd.DataFrame(datos_completos)

# # Guardar el DataFrame en un archivo CSV
# df_final.to_csv('productos_repuestos1.csv', index=False)
# print("Datos guardados en 'productos_repuestos.csv'")

# # Cerrar el navegador
# driver.quit()


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

# Guardar inicio de ejecución
inicio = time.time()

# Funciones para cargar inputs
def cargar_repuestos():
    df = pd.read_csv('Input Repuestos/input_repuestos.csv')
    df= df.head(2)
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

# Cargar inputs
repuestos = cargar_repuestos()
modelos_marcas = cargar_modelos_marcas()
print(modelos_marcas)

datos_completos = []

# Recorrer combinaciones de repuesto + modelo + marca
for repuesto in repuestos:
    for modelo_marca in modelos_marcas:
        marca = modelo_marca.get('marca', '')
        modelo = modelo_marca.get('modelo', '')
        generacion = str(modelo_marca.get('generacion', ''))
        anos = modelo_marca.get('anos', '')

        texto_busqueda = f"{repuesto} {modelo} {marca}"

        try:
            # Ir a la página principal de búsqueda
            driver.get('https://chilerepuestos.com/')
            time.sleep(2)

            # Ingresar texto en input de búsqueda
            input_busqueda = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'Buscador'))
            )
            input_busqueda.clear()
            input_busqueda.send_keys(texto_busqueda)

            # Clic en el botón de búsqueda
            boton_buscar = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-default btn-lg']"))
            )
            boton_buscar.click()

            # Esperar resultados
            time.sleep(2)

            try:
                productos_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="shop-grid"]/div'))
                )

                productos = productos_element.text

                for producto in productos.split('COMPRAR'):
                    lineas = producto.strip().split('\n')

                    if len(lineas) >= 6:
                        datos_completos.append({
                            'Marca Producto': lineas[0].strip(),
                            'Nombre Producto': lineas[1].strip(),
                            'Descripción': lineas[2].strip(),
                            'Precio': lineas[-3].strip(),
                            'Código': lineas[-1].strip(),
                            'Busqueda': texto_busqueda,
                            'Marca Buscada': marca,
                            'Modelo Buscado': modelo,
                            'Generacion': generacion,
                            'Anos': anos
                        })

            except NoSuchElementException:
                print(f"No se encontraron productos para: {texto_busqueda}")
                continue

        except Exception as e:
            print(f"Error en búsqueda {texto_busqueda}: {e}")
            continue

# Guardar datos en CSV
df_final = pd.DataFrame(datos_completos)
os.makedirs('Data encontrada', exist_ok=True)
df_final.to_csv('Data encontrada/productos_chilerepuestos.csv', index=False)
print("Datos guardados en 'Data encontrada/productos_chilerepuestos.csv'")

# Guardar tiempo de ejecución
fin = time.time()
duracion = fin - inicio
duracion_legible = str(datetime.timedelta(seconds=int(duracion)))

with open('Data encontrada/tiempo_ejecucion_chilerepuestos.txt', 'w') as f:
    f.write(f"Tiempo total de ejecución: {duracion_legible}\n")
    f.write(f"Duración en segundos: {duracion:.2f} segundos\n")

# Cerrar navegador
driver.quit()

