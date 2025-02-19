import pandas as pd
import mysql.connector
import config

print("pandas version "+pd.__version__)
# Parámetros de conexión a MySQL
db_config = {
    "host": "109.106.251.18",       
    "user": "saltaped_enrique",     
    "password": "enfi7625",
    "database": "saltaped_sivin2" 
}
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
# Leer el archivo de Excel
archivo_excel = "./planillas/consolidado.xlsx"  
df = pd.read_excel(archivo_excel, dtype=str)  # Leer todo como string para validaciones
df = df.drop_duplicates(subset=["DNI", "FECHA INGRESO"], keep="last")
# Ordenar la tabla por fecha de ingreso
df = df.sort_values(by=["DNI", "FECHA INGRESO"])
# Contar ocurrencias acumuladas de cada DNI
df["REINGRESO"] = df.groupby("DNI").cumcount() + 1  # Suma 1 para empezar desde 1
df["FECHA INGRESO"] = pd.to_datetime(df["FECHA INGRESO"], errors="coerce")
df["FECHA EGRESO"] = pd.to_datetime(df["FECHA EGRESO"], errors="coerce")

df["DIAS ESTADA"] = (df["FECHA EGRESO"] - df["FECHA INGRESO"]).dt.days

# Conectar a MySQL
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Crear nuevas columnas para los Z-scores
df["Z_PesoEdad_ing"] = "error"
df["Z_TallaEdad_ing"] = "error"
df["Z_IMCEdad_ing"] = "error"
df["Z_PesoEdad_egr"] = "error"
df["Z_TallaEdad_egr"] = "error"
df["Z_IMCEdad_egr"] = "error"




# Iterar sobre cada fila del DataFrame
for index, row in df.iterrows():
    sexo = {"M": 1, "F": 2}.get(str(row["SEXO"]).strip().upper(), 0)
    fecha_nace = convertir_fecha(row["FN"])
    fecha_control = convertir_fecha(row["FECHA INGRESO"])
    peso = convertir_numero(row["PESO INGRESO (kg)"])
    talla = convertir_numero(row["TALLA INGRESO (cm)"])
    fecha_control_e = convertir_fecha(row["FECHA EGRESO"])
    peso_e = convertir_numero(row["PESO EGRESO (kg)"])
    talla_e = convertir_numero(row["TALLA EGRESO (cm)"])
    
    # print(peso,talla,fecha_control,fecha_nace,sexo)
    try:
        # Calcular Z-Score de Peso/Edad ingreso
        if peso is not None and fecha_nace and fecha_control:
            cursor.execute("SELECT ZSCORE(%s, %s, %s, %s, %s)", (sexo, 'p', peso, fecha_nace, fecha_control))
            df.at[index, "Z_PesoEdad_ing"] = cursor.fetchone()[0] or "error"

        # Calcular Z-Score de Talla/Edad ingreso
        if talla is not None and fecha_nace and fecha_control:
            cursor.execute("SELECT ZSCORE(%s, %s, %s, %s, %s)", (sexo, 't', talla, fecha_nace, fecha_control))
            df.at[index, "Z_TallaEdad_ing"] = cursor.fetchone()[0] or "error"
 
        # Calcular Z-Score de IMC/Edad ingreso
        if peso is not None and talla is not None and fecha_nace and fecha_control:
            imc = peso / ((talla / 100) ** 2)
            cursor.execute("SELECT ZSCORE(%s, %s, %s, %s, %s)", (sexo, 'i', imc, fecha_nace, fecha_control))
            df.at[index, "Z_IMCEdad_ing"] = cursor.fetchone()[0] or "error"
        
        # Calcular Z-Score de Peso/Edad egreso
        if peso is not None and fecha_nace and fecha_control_e:
            cursor.execute("SELECT ZSCORE(%s, %s, %s, %s, %s)", (sexo, 'p', peso_e, fecha_nace, fecha_control_e))
            df.at[index, "Z_PesoEdad_egr"] = cursor.fetchone()[0] or "error"

        # Calcular Z-Score de Talla/Edad egreso
        if talla is not None and fecha_nace and fecha_control_e:
            cursor.execute("SELECT ZSCORE(%s, %s, %s, %s, %s)", (sexo, 't', talla_e, fecha_nace, fecha_control_e))
            df.at[index, "Z_TallaEdad_egr"] = cursor.fetchone()[0] or "error"
 
        # Calcular Z-Score de IMC/Edad egreso
        if peso is not None and talla is not None and fecha_nace and fecha_control_e:
            imc = peso_e / ((talla_e / 100) ** 2)
            cursor.execute("SELECT ZSCORE(%s, %s, %s, %s, %s)", (sexo, 'i', imc, fecha_nace, fecha_control_e))
            df.at[index, "Z_IMCEdad_egr"] = cursor.fetchone()[0] or "error"    

    except mysql.connector.Error as err:
        print(f"Error en la fila {index}: {err}")

# Cerrar conexión con MySQL
cursor.close()
conn.close()

# Guardar el DataFrame actualizado en un nuevo archivo Excel
df.to_excel("datos_con_zscores.xlsx", index=False)

print("Cálculo de Z-scores completado. Archivo guardado como 'datos_con_zscores.xlsx'.")
