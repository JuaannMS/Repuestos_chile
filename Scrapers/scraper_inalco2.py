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
import json
import re
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select


options = Options()
# options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
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

# Configurar navegador
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

search_url = f"https://www.inalcotiendaonline.cl/productos"
driver.get(search_url)



wait = WebDriverWait(driver, 10)  


# Seleccionar marca CHEVROLET
select_element = wait.until(EC.presence_of_element_located((By.ID, "selectBrandGarageProducts")))
select = Select(select_element)
select.select_by_visible_text("CHEVROLET")

# Cambiar cantidad de productos por página a 50
limit_select = wait.until(EC.presence_of_element_located((By.ID, "view-option-limit")))
select_limit = Select(limit_select)
select_limit.select_by_value("50")
time.sleep(2)  # dar tiempo a que recargue con 50 productos

# Obtener total de productos
legend_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.products-view__pagination-legend")))
legend_text = legend_element.text
match = re.search(r"de\s+(\d+)\s+Productos", legend_text)
total_productos = int(match.group(1)) if match else 0

# Calcular páginas (ahora con 50 por página)
productos_por_pagina = 50
total_paginas = total_productos // productos_por_pagina + (1 if total_productos % productos_por_pagina else 0)


datos_completos = []

for pagina in range(1, total_paginas + 1):
    
    
    productos = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.products-list__item")))
    for producto in productos:
        
        nombre = producto.find_element(By.CSS_SELECTOR, ".product-card__name").text.strip()

        link = producto.find_element(By.CSS_SELECTOR, "a.image__body").get_attribute("href")
        link = f"https://www.inalcotiendaonline.cl{link}" if link.startswith("/") else link

        try:
            img_url = producto.find_element(By.CSS_SELECTOR, "img.image__tag").get_attribute("src")
        except:
            img_url = ""

        try:
            precio_texto = producto.find_element(By.CSS_SELECTOR, "div.product-card__prices p").text
            precio = re.search(r"\$\d{1,3}(?:\.\d{3})*", precio_texto)
            precio_actual = precio.group() if precio else ""
            precio_normal = ""  # No se muestra explícitamente otro precio
        except:
            precio_actual = ""
            precio_normal = ""

        try:
            data_json = producto.find_element(By.CSS_SELECTOR, "button[name='btnAddCart']").get_attribute("data-json")
            json_data = json.loads(data_json)
            sku = json_data.get("ProductPartNumber", "")
        except:
            sku = ""

        datos_completos.append({
            'Nombre Producto': nombre,
            'SKU': sku,
            'Precio': precio_actual,
            'Precio Normal': precio_normal,
            'Link': link,
            'Imagen': img_url,
        })
    
    

    if pagina < total_paginas:
        try:
            next_li = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"li.page-item[data-page='{pagina+1}'] a.page-link"))
            )

            driver.execute_script("arguments[0].click();", next_li)

            wait.until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "div.products-view__pagination-legend"),
                    f"Mostrando"
                )
            )

        except Exception as e:
            print(" No se pudo hacer clic en Next:", e)
            break



# Guardar datos en Excel
df_final = pd.DataFrame(datos_completos).drop_duplicates(subset=["Link"])
os.makedirs('Data encontrada', exist_ok=True)
output_path = 'Data encontrada/resultados_inalco1.xlsx'
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel(output_path, index=False)
print(f"Datos guardados en '{output_path}'")

# Guardar tiempo de ejecución
fin = time.time()
duracion = fin - inicio
duracion_legible = str(timedelta(seconds=int(duracion)))
with open('Data encontrada/tiempo_ejecucion_inalco.txt', 'w') as f:
    f.write(f"Tiempo total de ejecucion: {duracion_legible}\n")
    f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")

# Cerrar navegador
driver.quit()
