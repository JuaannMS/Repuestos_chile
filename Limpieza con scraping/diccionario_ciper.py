import json
import pandas as pd
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from tqdm import tqdm


df = pd.read_excel('Data encontrada/resultados_ciper.xlsx')


df = df.drop_duplicates(subset=[ 'Link'])


df['Precio'] = (
    df['Precio']
    .astype(str)
    .str.replace(r'[\$\.\,]', '', regex=True)    # quita $, puntos y comas
    .astype(float)
)

df = df[
    df['Precio'].notna() &    # no nulo
    (df['Precio'] != 0)       # distinto de cero
].copy()

def extraer_specs(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except:
        return None, None

    soup = BeautifulSoup(r.content, "html.parser")
    marca = None
    modelo = None

    # Seleccionamos cada fila de especificación
    filas = soup.select("div.vtex-flex-layout-0-x-flexRow--productSpecification")
    for fila in filas:
        # nombre del campo (p.ej. "Marca Vehículo", "Modelo", etc.)
        nombre = fila.select_one("span.vtex-product-specifications-1-x-specificationName")
        valor  = fila.select_one("span.vtex-product-specifications-1-x-specificationValue")
        if not nombre or not valor:
            continue

        texto_campo = nombre.text.strip()
        texto_valor = valor.get("data-specification-value", valor.text).strip()

        if texto_campo == "Marca Vehículo":
            marca = texto_valor
        elif texto_campo == "Modelo":
            modelo = texto_valor

        # Si ya encontramos ambos, salimos
        if marca and modelo:
            break

    return marca, modelo


#ir agregando solo los link de producto que no tengan una marca o modelo asociado
resultados = [extraer_specs(url) for url in tqdm(df["Link"], desc="Extrayendo")]

df[["Marca", "Modelo"]] = pd.DataFrame(resultados, index=df.index)


df.to_excel('Data consolidada/marca_modelo_ciper.xlsx', index=False)

