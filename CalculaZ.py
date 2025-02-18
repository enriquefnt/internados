import pandas as pd
import mysql.connector

# Parámetros de conexión a MySQL
db_config = {
    "host": "109.106.251.18",       
    "user": "saltaped_enrique",     
    "password": "enfi7625",
    "database": "saltaped_sivin2" 
}

# Leer el archivo de Excel
archivo_excel = "./planillas/consolidado.xlsx"  
df = pd.read_excel(archivo_excel, dtype=str)  # Leer todo como string para validaciones

# Conectar a MySQL
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Crear nuevas columnas para los Z-scores
df["Z_PesoEdad"] = "error"
df["Z_TallaEdad"] = "error"
df["Z_IMCEdad"] = "error"

# Función para convertir fechas al formato correcto
def convertir_fecha(fecha):
    try:
        return pd.to_datetime(fecha, dayfirst=False).strftime("%Y-%m-%d")
    except Exception:
        return None  # Si hay un error, devuelve None

# Función para convertir números y corregir comas
def convertir_numero(valor):
    try:
        num = float(str(valor).replace(",", "."))  # Reemplaza coma por punto y convierte a float
        return num / 1000 if num > 1000 else num  # Convierte gramos a kg si es necesario
    except ValueError:
        return None  # Si no se puede convertir, devuelve None


# Iterar sobre cada fila del DataFrame
for index, row in df.iterrows():
    sexo = {"M": 1, "F": 2}.get(str(row["SEXO"]).strip().upper(), 0)
    fecha_nace = convertir_fecha(row["FN"])
    fecha_control = convertir_fecha(row["FECHA INGRESO"])
    peso = convertir_numero(row["PESO INGRESO (kg)"])
    talla = convertir_numero(row["TALLA INGRESO (cm)"])
    print(peso,talla,fecha_control,fecha_nace,sexo)
    try:
        # Calcular Z-Score de Peso/Edad
        if peso is not None and fecha_nace and fecha_control:
            cursor.execute("SELECT ZSCORE(%s, %s, %s, %s, %s)", (sexo, 'p', peso, fecha_nace, fecha_control))
            df.at[index, "Z_PesoEdad"] = cursor.fetchone()[0] or "error"

        # Calcular Z-Score de Talla/Edad
        if talla is not None and fecha_nace and fecha_control:
            cursor.execute("SELECT ZSCORE(%s, %s, %s, %s, %s)", (sexo, 't', talla, fecha_nace, fecha_control))
            df.at[index, "Z_TallaEdad"] = cursor.fetchone()[0] or "error"

        # Calcular Z-Score de IMC/Edad
        if peso is not None and talla is not None and fecha_nace and fecha_control:
            imc = peso / ((talla / 100) ** 2)
            cursor.execute("SELECT ZSCORE(%s, %s, %s, %s, %s)", (sexo, 'i', imc, fecha_nace, fecha_control))
            df.at[index, "Z_IMCEdad"] = cursor.fetchone()[0] or "error"

    except mysql.connector.Error as err:
        print(f"Error en la fila {index}: {err}")

# Cerrar conexión con MySQL
cursor.close()
conn.close()

# Guardar el DataFrame actualizado en un nuevo archivo Excel
df.to_excel("datos_con_zscores.xlsx", index=False)

print("Cálculo de Z-scores completado. Archivo guardado como 'datos_con_zscores.xlsx'.")
