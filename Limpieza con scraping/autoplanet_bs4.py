import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime, timedelta

df_autoplanet1 = pd.read_excel('Data encontrada/resultados_autoplanet.xlsx')

#Extraer marca es facil, pero modelo es mas dificil ya que nos muestra multicompatibilidad

