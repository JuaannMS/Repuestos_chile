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
url = 'https://chilerepuestos.com'
driver.get(url)

time.sleep(5)

url = 'https://chilerepuestos.com/1/search?Buscar=Bomba+de+agua+Hyundai+Santa+Fe'
driver.get(url)

# Cargar el CSV
df_repuestos = pd.read_csv('repuestos_chile.csv')



for index, row in df_repuestos.iterrows():
    # Construir el texto de búsqueda
    texto_busqueda = f"{row['Repuesto']} {row['Modelo']} {row['Marca']}"

    # Ingresar el texto en el input de búsqueda
    input_busqueda = driver.find_element(By.ID, 'Buscador')
    input_busqueda.clear()
    input_busqueda.send_keys(texto_busqueda)

    # Clic en el botón de búsqueda
    boton_buscar = driver.find_element(By.XPATH, "//button[@class='btn btn-default btn-lg']")
    boton_buscar.click()

    time.sleep(1)
    datos_completos = []
    try:
        productos = driver.find_element(By.XPATH, '//*[@id="shop-grid"]/div').text
        # Separar por bloques de productos
        for producto in productos.split('COMPRAR'):
            lineas = producto.strip().split('\n')
            
            if len(lineas) >= 6:
                datos_completos.append({
                    'Marca': lineas[0].strip(),
                    'Nombre': lineas[1].strip(),
                    'Descripción': lineas[2].strip(),
                    'Precio': lineas[-3].strip(),
                    'Código': lineas[-1].strip()
                })

    except Exception as e:
        print(f"Error al extraer el contenido del componente: {e}")


# Crear un DataFrame final con todos los datos
df_final = pd.DataFrame(datos_completos)

# Guardar el DataFrame en un archivo CSV
df_final.to_csv('productos_repuestos1.csv', index=False)
print("Datos guardados en 'productos_repuestos.csv'")

# Cerrar el navegador
driver.quit()

