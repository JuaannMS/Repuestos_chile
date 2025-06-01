import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# Lista de rutas de scrapers
scrapers = [
    "Scrapers/scraper_autoplanet.py",
    "Scrapers/scraper_casaderepuestos.py",
    "Scrapers/scraper_chilerepuestos.py",
    "Scrapers/scraper_ciper.py",
    "Scrapers/scraper_emgi.py",
    "Scrapers/scraper_inalco.py",
    "Scrapers/scraper_mundorepuesto.py",
    "Scrapers/scraper_salfarepuestos.py",
    "Scrapers/scraper_takora.py"
]

def ejecutar_scraper(scraper):
    try:
        print(f"Ejecutando {scraper}...")
        result = subprocess.run(["python", scraper], capture_output=True, text=True)
        print(f"{scraper} finalizado con código {result.returncode}")
        if result.stdout:
            print(f"Salida de {scraper}:\n{result.stdout}")
        if result.stderr:
            print(f"Errores de {scraper}:\n{result.stderr}")
    except Exception as e:
        print(f"Error al ejecutar {scraper}: {e}")

# Ejecutar todos los scrapers en paralelo usando hilos
if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=9) as executor:
        futures = [executor.submit(ejecutar_scraper, scraper) for scraper in scrapers]
        for future in as_completed(futures):
            future.result()  # para lanzar cualquier excepción en los hilos
