import asyncio
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import random
import re
import time

# === Selenium ===
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ======= SELECTORES DE PRECIO =======
PRICE_SELECTORS = {
    "ulti.cl": "div.product__price.product__price--current",
    # "emgi.cl": "span.product-single__price",
    # "inalcotiendaonline.cl": "div.product__price.product__price--current",
    # "ciper.cl": "span.vtex-product-price-1-x-currencyContainer",
    # "chilerepuestos.com": "body > div.single-page-area > div > div:nth-child(2) > div.col-lg-5.col-md-5.col-sm-6 > div > div.product-content > div > span.new-price",
    # # Takora.cl y Autoplanet.cl tienen funciones dedicadas
}

# ======= USER-AGENTS =======
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
]

# ======= LECTURA DE EXCEL =======
def load_urls_from_excel(file_path, col_name="url"):
    df = pd.read_excel(file_path)
    return df[col_name].dropna().tolist()

# ======= FUNCION PARA AUTOPLANET (USA SELENIUM) =======
def get_price_autoplanet(url):
    print(f"🔄 [Selenium] Cargando {url}...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        price_el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.new-price"))
        )
        raw_price = price_el.text.strip()
        clean_price = float(raw_price.replace("$", "").replace(".", "").replace(",", "."))
        return {
            "url": url,
            "precio_normal": clean_price,
            "precio_oferta": None,
            "precio_final": clean_price,
            "error": None
        }
    except Exception as e:
        return {"url": url, "precio_normal": None, "precio_oferta": None, "precio_final": None, "error": f"Selenium: {e}"}
    finally:
        driver.quit()

# ======= FUNCION MEJORADA PARA TAKORA =======
async def fetch_price_takora(session, url):
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        async with session.get(url, headers=headers, timeout=20) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "lxml")

            td_price = soup.select_one("td.priceHeading")
            if not td_price:
                return {"url": url, "precio_normal": None, "precio_oferta": None, "precio_final": None, "error": "NO SE ENCONTRÓ priceHeading"}

            text = td_price.get_text(" ", strip=True)

            # Buscar todos los precios en el bloque
            precios = re.findall(r"\$?\s?(\d{1,3}(?:\.\d{3})+)", text)

            def clean(p):
                return float(p.replace(".", "")) if p else None

            price_normal = clean(precios[0]) if len(precios) >= 1 else None
            price_oferta = clean(precios[1]) if len(precios) >= 2 else None

            # Si solo hay un precio, es el normal
            if len(precios) == 1:
                price_oferta = None

            precio_final = price_oferta if price_oferta else price_normal

            return {
                "url": url,
                "precio_normal": price_normal,
                "precio_oferta": price_oferta,
                "precio_final": precio_final,
                "error": None
            }

    except Exception as e:
        return {"url": url, "precio_normal": None, "precio_oferta": None, "precio_final": None, "error": str(e)}

# ======= FUNCION PARA OTROS SITIOS =======
async def fetch_price(session, url, retries=3):
    domain = urlparse(url).netloc.replace("www.", "")

    # # Autoplanet → Selenium
    # if "autoplanet.cl" in domain:
    #     return get_price_autoplanet(url)

    # # Takora → función especial
    # if "takora.cl" in domain:
    #     return await fetch_price_takora(session, url)

    # Otros sitios → scraping normal
    selector = PRICE_SELECTORS.get(domain)
    if not selector:
        return {"url": url, "precio_normal": None, "precio_oferta": None, "precio_final": None, "error": "NO SELECTOR DEFINIDO"}

    for attempt in range(retries):
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            async with session.get(url, headers=headers, timeout=20) as resp:
                html = await resp.text()
                soup = BeautifulSoup(html, "lxml")
                el = soup.select_one(selector)
                if not el:
                    raise ValueError("NO SE ENCONTRÓ EL ELEMENTO")

                raw_price = el.get_text(strip=True)
                clean_price = float(raw_price.replace("$", "").replace(" ", "").replace(".", "").replace(",", "."))
                return {
                    "url": url,
                    "precio_normal": clean_price,
                    "precio_oferta": None,
                    "precio_final": clean_price,
                    "error": None
                }

        except Exception as e:
            if attempt == retries - 1:
                return {"url": url, "precio_normal": None, "precio_oferta": None, "precio_final": None, "error": str(e)}
            await asyncio.sleep(2)  # reintento

# ======= SCRAPING CONCURRENTE =======
async def scrape_all(urls):
    results = []
    connector = aiohttp.TCPConnector(limit_per_host=5)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_price(session, url) for url in urls]
        for coro in asyncio.as_completed(tasks):
            res = await coro
            print(f"✅ {res['url']} → Normal: {res['precio_normal']} | Oferta: {res['precio_oferta']} | Final: {res['precio_final']} | {res['error'] or 'OK'}")
            results.append(res)
    return results

# ======= MAIN =======
if __name__ == "__main__":
    excel_path = "data_carga2.xlsx"   
    column_name = "link"                   

    urls = load_urls_from_excel(excel_path, column_name)
    data = asyncio.run(scrape_all(urls))

    df_result = pd.DataFrame(data)
    df_result.to_excel("precios_resultado1.xlsx", index=False)
    print("\n✅ Resultados guardados en precios_resultado.xlsx")
