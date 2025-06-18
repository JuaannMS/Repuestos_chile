import pandas as pd
import openai
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from time import sleep

# Cargar API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

def extraer_info_web(link):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(link, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        titulo = soup.find('title').get_text(strip=True) if soup.find('title') else ''
        meta = soup.find('meta', attrs={'name': 'description'})
        descripcion = meta['content'].strip() if meta else ''
        return f"Título: {titulo}\nDescripción: {descripcion}"
    except Exception as e:
        return f"No se pudo acceder al link: {str(e)}"

def validar_producto(nombre_producto, marca_buscada, modelo_buscado, link):
    nombre = str(nombre_producto).lower()
    marca_buscada = str(marca_buscada).lower()
    modelo_buscado = str(modelo_buscado).lower()

    marca_detectada = "Otro"
    modelo_detectado = "Otro"

    if marca_buscada in nombre and modelo_buscado in nombre:
        return "✅ Producto válido (por coincidencia directa en el nombre)", marca_buscada.title(), modelo_buscado.title()

    contenido_web = extraer_info_web(link)
    prompt = f"""
Analiza el siguiente producto. Indica la marca real y el modelo real para el cual es compatible.

Nombre original del producto: "{nombre_producto}"
Contenido web:
{contenido_web}

Devuelve exclusivamente este formato:
Marca real: [marca detectada]
Modelo real: [modelo o modelos separados por coma]
(Si no se puede determinar, escribe "Otro" en ambos campos).
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()

        for line in content.split('\n'):
            if "marca real" in line.lower():
                marca_detectada = line.split(":", 1)[1].strip()
            elif "modelo real" in line.lower():
                modelo_detectado = line.split(":", 1)[1].strip()

        resultado = "✅ Producto válido" if marca_detectada.lower() == marca_buscada and modelo_buscado in modelo_detectado.lower() else "❌ No compatible"
        return resultado, marca_detectada, modelo_detectado
    except Exception as e:
        return f"⚠️ Error al validar: {str(e)}", marca_detectada, modelo_detectado

# Leer archivo base
df = pd.read_excel("Data consolidada/df_nombres_duplicados.xlsx")
df_sample = df[['Nombre Producto', 'Marca Buscada', 'Modelo Buscado', 'Link']].dropna().head(10).copy()

# Procesamiento
resultados = []
marcas_detectadas = []
modelos_detectados = []

for _, row in df_sample.iterrows():
    resultado, marca_detectada, modelo_detectado = validar_producto(
        row['Nombre Producto'],
        row['Marca Buscada'],
        row['Modelo Buscado'],
        row['Link']
    )
    resultados.append(resultado)
    marcas_detectadas.append(marca_detectada)
    modelos_detectados.append(modelo_detectado)
    sleep(1.5)

# Agregar columnas al DataFrame original
df_sample['Resultado Agente'] = resultados
df_sample['Marca Detectada'] = marcas_detectadas
df_sample['Modelo Detectado'] = modelos_detectados

# Exportar archivo principal
df_sample.to_csv("validacion_gpt4mini_con_web.csv", index=False)

# Exportar archivo limpio solo con lo detectado
df_detectada = df_sample[['Link', 'Marca Detectada', 'Modelo Detectado']]
df_detectada.to_csv("producto_referencia_detectada.csv", index=False)

# Exportar archivo con los no válidos
df_no_validos = df_detectada[
    (df_detectada['Marca Detectada'].str.lower() == 'otro') |
    (df_detectada['Modelo Detectado'].str.lower() == 'otro')
]
df_no_validos.to_csv("productos_no_validos.csv", index=False)

print("✅ Archivos generados correctamente:")
print("- validacion_gpt4mini_con_web.csv")
print("- producto_referencia_detectada.csv")
print("- productos_no_validos.csv")
