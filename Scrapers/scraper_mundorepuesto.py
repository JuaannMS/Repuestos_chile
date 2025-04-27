from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Configurar opciones del navegador
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')

# Inicializar el WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# URL de la página a analizar
url = 'https://mundorepuestos.com/busqueda/focos--led--l200'
driver.get(url)

time.sleep(5)  # Esperar que cargue la página

# Cargar el CSV
df_repuestos = pd.read_csv('repuestos_chile.csv')

# Buscar cada repuesto en la página
for index, row in df_repuestos.iterrows():
    # Construir el texto de búsqueda
    texto_busqueda = f"{row['Repuesto']} {row['Modelo']} {row['Marca']}"

    # Ingresar el texto en el input de búsqueda
    input_busqueda = driver.find_element(By.ID, 'txtBuscar')
    input_busqueda.clear()
    input_busqueda.send_keys(texto_busqueda)

    # Clic en el botón de búsqueda
    boton_buscar = driver.find_element(By.ID, 'btnBuscar')
    boton_buscar.click()

    time.sleep(2)

    # Extraer la información del componente
    try:
        contenido_productos = driver.find_element(By.XPATH, '//*[@id="contenido_productos"]').text
        productos = contenido_productos.split('Ver fotos')
        datos_totales = [] 
        for producto in productos:
            lineas = producto.strip().split('\n')
            if len(lineas) > 6:  # Verificar que sea un producto válido
                datos_totales.append({
                    'Código': lineas[0].strip(),
                    'Nombre': lineas[1].strip(),
                    'Descripción': lineas[2].strip(),
                    'Años': lineas[3].strip(),
                    'Marca': lineas[4].split(':')[1].strip(),
                    'Origen': lineas[5].split(':')[1].strip(),
                    'Precio Oferta': lineas[6].strip(),
                    'Precio Original': lineas[8].strip(),
                    'Descuento': lineas[10].strip()
                })
    except Exception as e:
        print(f"Error al extraer el contenido del componente para {texto_busqueda}")

# Crear un DataFrame final con todos los datos
df_final = pd.DataFrame(datos_totales)

# Guardar el DataFrame en un archivo CSV
df_final.to_csv('productos_repuestos.csv', index=False)
print("Datos guardados en 'productos_repuestos.csv'")

# Cerrar el navegador
driver.quit()