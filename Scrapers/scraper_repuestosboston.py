from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options


options = Options()
# options.add_argument("--headless")   # Ejecutar sin abrir ventana
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

inicio = time.time()
fecha_hora_actual = datetime.now()


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


def buscar_boston(repuesto, marca_text, modelo_text):
    texto_busqueda = f"{repuesto} {marca_text} {modelo_text}"
    query = texto_busqueda.strip().replace(' ', '+')
    search_url = f"https://www.repuestosboston.cl/catalogsearch/result/?q={query}&compatible=todos"
    print(f"Buscando en: {search_url}")

    try:
        driver.get(search_url)
        #time.sleep(2)  
        wait = WebDriverWait(driver, 10)

        # Esperar a que se carguen los productos
        productos = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.item.product.product-item")))

        resultados = []
        for producto in productos:
            try:
                # Nombre del producto
                try:
                    nombre = producto.find_element(By.CSS_SELECTOR, "h2.product.name.product-item-name").text.strip()
                except:
                    nombre = "No disponible"

                # Link
                try:
                    link = producto.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                except:
                    link = ""

                # Precio
                try:
                    precio = producto.find_element(By.CSS_SELECTOR, "span.price").text.strip()
                except:
                    precio = "No disponible"

                # Estado stock
                try:
                    stock = producto.find_element(By.CSS_SELECTOR, "div.amasty-label-container").text.strip()
                except:
                    stock = "Disponible"

                # Imagen
                try:
                    img = producto.find_element(By.CSS_SELECTOR, "img.product-image-photo")
                    img_url = img.get_attribute("src")
                except:
                    img_url = ""

                resultados.append({
                    "Nombre Producto": nombre,
                    "Precio": precio,
                    "Stock": stock,
                    "Link": link,
                    "Imagen": img_url,
                    "Marca Buscada": marca_text,
                    "Modelo Buscado": modelo_text,
                    "Texto Búsqueda": texto_busqueda
                })

            except Exception as e:
                print(f"⚠️ Error extrayendo producto: {e}")
                continue

        return resultados

    except Exception as e:
        print(f"❌ Error inesperado en búsqueda '{texto_busqueda}': {e}")
        return []

# ==============================
# Main
# ==============================
repuestos = cargar_repuestos()
modelos_marcas = cargar_modelos_marcas()

datos_completos = []
for repuesto in repuestos:
    for modelo_marca in modelos_marcas:
        marca_text = modelo_marca.get('marca', '')
        modelo_text = modelo_marca.get('modelo', '')
        try:
            datos_completos.extend(buscar_boston(repuesto, marca_text, modelo_text))
        except Exception as e:
            print(f"Error en búsqueda '{repuesto} {marca_text} {modelo_text}': {e}")
            continue



df_final = pd.DataFrame(datos_completos).drop_duplicates(subset=["Nombre Producto", "Link"])

os.makedirs('Data encontrada', exist_ok=True)
output_path = 'Data encontrada/resultados_repuestosboston.xlsx'
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel(output_path, index=False)
print(f"✅ Datos guardados en '{output_path}'")

fin = time.time()
duracion = fin - inicio
duracion_legible = str(timedelta(seconds=int(duracion)))
with open('Data encontrada/tiempo_ejecucion_repuestosboston.txt', 'w') as f:
    f.write(f"Tiempo total de ejecucion: {duracion_legible}\n")
    f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")

driver.quit()
