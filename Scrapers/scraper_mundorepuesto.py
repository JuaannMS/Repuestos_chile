from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time


from selenium.webdriver.common.keys import Keys
import pandas as pd
from datetime import datetime, timedelta
from selenium.common.exceptions import NoSuchElementException, TimeoutException


fecha_hora_actual = datetime.now()
inicio = time.time()

profile_path = r"C:\Users\jmmsa\AppData\Roaming\Mozilla\Firefox\Profiles\jfcepb6x.default-release"


options = Options()

# Usar perfil real
options.profile = profile_path  

# Preferencias para evadir detección
options.set_preference("dom.webdriver.enabled", False)              # Ocultar flag webdriver
options.set_preference("useAutomationExtension", False)             # Desactivar extensión automation
options.set_preference("general.useragent.override",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0")
options.set_preference("dom.webnotifications.enabled", False)       # Bloquear notificaciones
options.set_preference("media.navigator.enabled", False)            # Deshabilitar WebRTC
options.set_preference("network.http.referer.XOriginPolicy", 0)     # Enviar referer completo
options.set_preference("privacy.trackingprotection.enabled", False) # Sin tracking protection

# Otras medidas útiles
options.set_preference("network.http.sendRefererHeader", 2)         # Siempre enviar referer
options.set_preference("intl.accept_languages", "es-CL,es,en-US,en") # Idioma realista
options.set_preference("geo.enabled", False)                        # Desactivar geolocalización
options.set_preference("browser.safebrowsing.enabled", False)       # Sin Google SafeBrowsing
options.set_preference("browser.cache.disk.enable", True)           # Mantener caché como humano
options.set_preference("browser.cache.memory.enable", True)

# Inicializar Firefox
driver = webdriver.Firefox(
    service=FirefoxService(GeckoDriverManager().install()),
    options=options
)

# Ocultar webdriver en JS
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# Inyectar propiedades "humanas"
driver.execute_script("""
Object.defineProperty(navigator, 'languages', {get: () => ['es-CL','es','en-US','en']});
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
""")

# Navegar a la página inicial
driver.get("https://mundorepuestos.com/")
time.sleep(20)

carpeta = "Modelos y marcas"
marcas = []
for archivo in os.listdir(carpeta):
    if archivo.endswith(".csv"):
        marca = os.path.splitext(archivo)[0]  # quitar extensión
        marcas.append(marca.lower())





def cargar_todos_los_productos(driver):
    
    wait = WebDriverWait(driver, 10)

    while True:
        try:
            texto = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#cantProductosMostrados span"))
            ).text.strip()

            partes = [int(s) for s in texto.replace("Mostrando", "").replace("productos", "").split() if s.isdigit()]
            if len(partes) == 2:
                mostrados, total = partes
                print(f"📊 {mostrados} / {total} productos visibles")

                if mostrados >= total:
                    print("✅ Todos los productos cargados")
                    break

            boton = wait.until(EC.element_to_be_clickable((By.ID, "btn_vermas")))
            driver.execute_script("arguments[0].click();", boton)
            time.sleep(2)

        except Exception as e:
            print(f"⚠️ No se pudo cargar más productos: {e}")
            break


datos_completos = []

wait = WebDriverWait(driver, 15)
wait_short = WebDriverWait(driver, 5)

for marca in marcas:
    url = f"https://mundorepuestos.com/marca/{marca}"
    driver.get(url)

    time.sleep(15)

    try:
        # Buscar todos los modelos dentro del contenedor
        modelos = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#contenedorModelos .linkModelo a.link_modeloslargos"))
        )
        print(f"✅ {len(modelos)} modelos encontrados para {marca}")

        for i in range(len(modelos)):
            # ⚠️ Recargar modelos después de cada back()
            modelos = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#contenedorModelos .linkModelo a.link_modeloslargos"))
            )
            modelo = modelos[i]

            nombre_modelo = modelo.text.strip()
            print(f"   - Visitando modelo: {nombre_modelo}")

            # Scroll al elemento
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", modelo)
            time.sleep(1)

            # Intentar clic normal, si falla, fallback a JS
            try:
                modelo.click()
            except:
                driver.execute_script("arguments[0].click();", modelo)

            # Esperar a que cargue la página del modelo
            time.sleep(15)

            try:
                productos_links = wait_short.until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'linkVerPrd'))
                )

                for link in productos_links:
                    href = link.get_attribute('href')

                    # SUBIR al <tr> padre
                    fila = link.find_element(By.XPATH, "./ancestor::tr")

                    # Imagen
                    try:
                        img_el = fila.find_element(By.XPATH, ".//td[contains(@class, 'col-img-productoDesk')]//img")
                        img_url = img_el.get_attribute('src')
                    except NoSuchElementException:
                        img_url = ''

                    # Contenedor de datos
                    try:
                        container = fila.find_element(By.XPATH, ".//div[@id='datos-producto']")
                    except NoSuchElementException:
                        container = None

                    # Variables
                    codigo = nombre_prod = descripcion = anos_aplic = marca_prod = origen = precio_original = ''

                    if container:
                        try: codigo = container.find_element(By.CSS_SELECTOR, "p.codigo_producto").text
                        except NoSuchElementException: pass
                        try: nombre_prod = container.find_element(By.CSS_SELECTOR, "span.titulo-producto").text
                        except NoSuchElementException: pass
                        spans = container.find_elements(By.XPATH, "./span")
                        if len(spans) > 1:
                            descripcion = spans[1].text
                        try: anos_aplic = container.find_element(By.CSS_SELECTOR, "span.years").text
                        except NoSuchElementException: pass
                        try: marca_prod = container.find_element(By.CSS_SELECTOR, "span.nameMarca").text
                        except NoSuchElementException: pass
                        try: origen = container.find_element(By.CSS_SELECTOR, "span.productoOrigen").text
                        except NoSuchElementException: pass
                        try: precio_original = container.find_element(By.CSS_SELECTOR, "span.precio_original").text
                        except NoSuchElementException: pass

                    precio_oferta = link.get_attribute("data-priceoffer") or ''

                    datos_completos.append({
                        'Marca':            marca,
                        'Modelo':           nombre_modelo,
                        'Código':           codigo,
                        'Nombre Producto':  nombre_prod,
                        'Descripción':      descripcion,
                        'Años Aplicación':  anos_aplic,
                        'Marca Producto':   marca_prod,
                        'Origen':           origen,
                        'Precio Oferta':    precio_oferta,
                        'Precio Original':  precio_original,
                        'Link':             href,
                        'Imagen':           img_url
                    })

            except TimeoutException:
                print(f"⚠️ No se encontraron productos para: {nombre_modelo}")

            # 🔙 Volver a la página de modelos
            driver.back()
            time.sleep(3)

    except Exception as e:
        print(f"❌ Error al procesar {marca}: {e}")




df_final = pd.DataFrame(datos_completos).drop_duplicates(subset=["Link"])

print("✅ Navegación finalizada.")
driver.quit()


df_final = pd.DataFrame(datos_completos).drop_duplicates()
os.makedirs('Data encontrada', exist_ok=True)
df_final['fecha_carga'] = fecha_hora_actual
df_final.to_excel('Data encontrada/resultados_mundorepuestos.xlsx', index=False)
print("Datos guardados en 'Data encontrada/resultados_mundorepuestos.xlsx'")

fin = time.time()
duracion = fin - inicio
duracion_legible = str(timedelta(seconds=int(duracion)))
with open('Data encontrada/tiempo_ejecucion_mundorepuestos.txt', 'w') as f:
    f.write(f"Tiempo total de ejecucion: {duracion_legible}\n")
    f.write(f"Duracion en segundos: {duracion:.2f} segundos\n")


