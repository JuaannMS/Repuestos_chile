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
url = 'https://www.autoplanet.cl/'
driver.get(url)

df_repuestos = pd.read_csv('repuestos_chile.csv')
datos_completos = []
for index, row in df_repuestos.iterrows():
    texto_busqueda = f"{row['Repuesto']} {row['Modelo']} {row['Marca']}"

    input_element = driver.find_element(By.ID, "smartSearchId")
    input_element.clear()
    input_element.send_keys(texto_busqueda)
    input_element.send_keys(Keys.RETURN)

    time.sleep(1)
    

    while True:
        try:
            # Esperar que cargue el contenedor de productos
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="productSearchAutomootive"]/div/div/app-plp-grid/div[3]'))
            )

            # EXTRAER TEXTO DE LA PÁGINA ACTUAL
            element = driver.find_element(By.XPATH, '//*[@id="productSearchAutomootive"]/div/div/app-plp-grid/div[3]')
            texto = element.text
            # print(texto)

            productos = texto.strip().split("\n\n")

            for producto in productos:
                lineas = producto.strip().split('\n')
                if len(lineas) >= 2:
                    marca = lineas[0].strip()
                    nombre = lineas[1].strip()
                    precio = lineas[-1].strip()
                    print(marca)
                    datos_completos.append({
                        'Marca': marca,
                        'Nombre': nombre,
                        'Precio': precio,
                        'Busqueda': texto_busqueda
                    })
                # break
                    # print(datos_completos)
            # Intentar hacer clic en el botón siguiente
            next_button = driver.find_element(By.XPATH, "//div[contains(@class, 'pagination-next')]/a")
            next_button.click()

            # Esperar a que cambie la página
            WebDriverWait(driver, 10).until(EC.staleness_of(element))
            time.sleep(3)
        
            # print(datos_completos)

        except NoSuchElementException:
            break
        except ElementClickInterceptedException:
            print("El botón siguiente no se puede clickear.")
            break
        except Exception as e:
            print(f"Error inesperado: {e}")
            break
    # break

# Guardar los datos de esta búsqueda en un archivo o seguir acumulando
df_resultados = pd.DataFrame(datos_completos)
# df_resultados = df_resultados.drop_duplicates()
df_resultados.to_csv('resultados_autoplante.csv', index=False)
