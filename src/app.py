import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

url = "https://companies-market-cap-copy.vercel.app/index.html"

# Download HTML
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Error al acceder a la página: {response.status_code}")
html_content = response.text

html_content