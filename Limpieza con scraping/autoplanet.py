import re
import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==============================
# 1) Cargar DataFrame
# ==============================
df_autoplanet1 = pd.read_excel('../Data encontrada/resultados_autoplanet.xlsx')

# ==============================
# 2) Cargar listado de marcas
# ==============================
carpeta = "../Modelos y marcas"
marcas_buscar = []
for archivo in os.listdir(carpeta):
    if archivo.endswith(".csv"):
        marca = os.path.splitext(archivo)[0]
        marcas_buscar.append(marca.lower())

marcas_string = "|".join(marcas_buscar)

pattern_nombre = rf"({marcas_string})\s+([A-Za-z]{{3,}}[A-Za-z\-]*)"
pattern_link   = rf"/({marcas_string})[_\-]+([A-Za-z]{{3,}}[A-Za-z\-]*)"

marcas = []
modelos = []

# ==============================
# 3) Detectar por regex
# ==============================

#df_autoplanet1 = df_autoplanet1.head(100)

for idx, row in df_autoplanet1.iterrows():
    nombre_producto = str(row.get("Nombre Producto", "")).lower()
    link = str(row.get("Link", "")).lower()

    marca_detectada = "Desconocido"
    modelo_detectado = "Desconocido"

    match_nombre = re.search(pattern_nombre, nombre_producto, re.IGNORECASE)
    if match_nombre:
        marca_detectada = match_nombre.group(1).capitalize()
        modelo_detectado = match_nombre.group(2)
    else:
        match_link = re.search(pattern_link, link, re.IGNORECASE)
        if match_link:
            marca_detectada = match_link.group(1).capitalize()
            modelo_detectado = match_link.group(2)

    marcas.append(marca_detectada)
    modelos.append(modelo_detectado)

df_autoplanet1["Marca buscada"] = marcas
df_autoplanet1["Modelo buscado"] = modelos

# ==============================
# 4) Selenium para los que quedaron como Desconocido
# ==============================
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 3)

for idx, row in df_autoplanet1.iterrows():
    if row["Marca buscada"] == "Desconocido" or row["Modelo buscado"] == "Desconocido":
        link = row["Link"]
        try:
            driver.get(link)

            # 1) Extraer marcas disponibles
            detalles = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.detalle"))
            )
            valores = [re.sub(r"\s*\(\d+\)", "", d.text).strip().upper() for d in detalles if d.text.strip()]

            # 2) Normalizar marcas
            marcas_upper = [m.upper() for m in marcas_buscar]

            # 3) Buscar primera marca conocida
            primera_marca = next((v for v in valores if v in marcas_upper), None)

            if not primera_marca:
                df_autoplanet1.at[idx, "Marca buscada"] = "Error"
                df_autoplanet1.at[idx, "Modelo buscado"] = "Error"
                continue

            # 4) Click en la marca
            elemento = wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//div[@class='detalle' and contains(., '{primera_marca}')]"))
            )
            driver.execute_script("arguments[0].click();", elemento)

            # 5) Extraer primer modelo
            primer_modelo = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.itemDiv mat-card div.detalle"))
            )
            texto_modelo = primer_modelo.text
            modelo_limpio = re.sub(r"\s*\(\d+\)", "", texto_modelo).strip().upper()

            # Guardar en DataFrame
            df_autoplanet1.at[idx, "Marca buscada"] = primera_marca.capitalize()
            df_autoplanet1.at[idx, "Modelo buscado"] = modelo_limpio.capitalize()

        except Exception as e:
            df_autoplanet1.at[idx, "Marca buscada"] = "Error"
            df_autoplanet1.at[idx, "Modelo buscado"] = "Error"
            print(f"❌ Error en {link}: {e}")

driver.quit()



df_autoplanet1.to_excel("../Data encontrada/resultados_autoplanet_finaesl.xlsx", index=False)
print("✅ Resultados guardados en resultados_autoplanet_final.xlsx")

