import pandas as pd
import os

# Directorio donde guardas los archivos Excel
directorio = "./planillas"

# Archivo Excel consolidado
archivo_consolidado = "./planillas/consolidado.xlsx"

# Lista para almacenar los DataFrames
dataframes = []

# Leer cada archivo en el directorio
for archivo in os.listdir(directorio):
    if archivo.endswith(".xlsx") or archivo.endswith(".xls"):  # Asegura que sea un archivo Excel
        ruta_completa = os.path.join(directorio, archivo)
        df = pd.read_excel(ruta_completa)  # Leer el archivo
        dataframes.append(df)

# Concatenar todos los DataFrames en uno solo
df_consolidado = pd.concat(dataframes, ignore_index=True)

# Guardar en un nuevo archivo Excel
df_consolidado.to_excel(archivo_consolidado, index=False)

print("Consolidación completada.")
