import requests
from bs4 import BeautifulSoup
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd

# URL de la página
url = "https://companies-market-cap-copy.vercel.app/index.html"

# Descargar y analizar HTML
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

# Extraer la tabla de ingresos
table = soup.find("table")  
rows = table.find_all("tr")[1:]  # Saltar la cabecera

# Procesar datos de la tabla
data = [[cols[0].text.strip(), cols[1].text.strip()] for row in rows if (cols := row.find_all("td"))]
df = pd.DataFrame(data, columns=["Date", "Revenue"]).sort_values("Date")

# Función para limpiar la columna "Revenue"
def convert_revenue(value):
    if "B" in value:
        return float(value.replace("B", "").replace("$", "").replace(",", ""))
    return float(value.replace("$", "").replace(",", ""))

df["Revenue"] = df["Revenue"].apply(convert_revenue)

# Guardar en SQLite con un bucle
conn = sqlite3.connect("tesla_revenues.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS revenue (date TEXT, revenue REAL)")

for index, row in df.iterrows():
    cursor.execute("INSERT INTO revenue (date, revenue) VALUES (?, ?)", (row["Date"], row["Revenue"]))

conn.commit()
conn.close()

# Visualizar los datos
plt.figure(figsize=(10, 6))
plt.plot(df["Date"], df["Revenue"], marker='o', label="Revenue")
plt.title("Tesla annual revenue")
plt.xlabel("Date")
plt.ylabel("Revenue in billions (USD)")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.savefig("revenue_plot.png")
plt.show()

## 🔹 Ejercicio extra: Extraer ganancias anuales
earnings_table = soup.find("table", {"class": "table"})
earnings_data = [
    {"Año": row.find_all("td")[0].text.strip(), "Ganancias": row.find_all("td")[1].text.strip()}
    for row in earnings_table.find_all("tr")[1:]
]
df_earnings = pd.DataFrame(earnings_data)

# Convertir "Ganancias" a números
def parse_earnings(value):
    value = value.replace("$", "").replace(",", "").strip()
    return (
        float(value.replace("Billion", "")) * 1e9 if "Billion" in value else
        float(value.replace("Million", "")) * 1e6 if "Million" in value else
        float(value.replace("B", "")) * 1e9 if "B" in value else
        float(value.replace("M", "")) * 1e6 if "M" in value else
        float(value)
    )

df_earnings["Año"] = df_earnings["Año"].str.extract(r"(\d+)").astype("Int64")
df_earnings["Ganancias"] = df_earnings["Ganancias"].apply(parse_earnings)

# Obtener el año más reciente
ultimo_ano_fila = df_earnings.sort_values("Año", ascending=False).iloc[0]
mensaje = f"Tesla ha generado ${ultimo_ano_fila['Ganancias']:,.2f} en el año {ultimo_ano_fila['Año']}."
print(mensaje)