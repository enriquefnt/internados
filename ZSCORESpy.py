import pandas as pd
from datetime import datetime

# Función para calcular la edad en días y meses
def calcular_edad(fecha_nace, fecha_control):
    edad_dias = (fecha_control - fecha_nace).days
    edad_mes = edad_dias // 30  # Aproximado
    return edad_dias, edad_mes

# Función para leer la tabla de referencia
# Función para leer la tabla de referencia
def obtener_parametros(tabla, edad_col, edad, sexo, bus):
    df = pd.read_csv(f"{tabla}.csv", sep=";", dtype=str)

    df.columns = df.columns.str.replace('"', '').str.strip()  # Limpia comillas y espacios

    # Filtrar por edad
    row = df[df[edad_col] == str(edad)]  # Asegura que la edad sea una cadena

    if row.empty:
        return None, None, None  # Si no hay datos para esa edad

    if sexo == 2:
        L, M, S = row["la"].values[0], row["ma"].values[0], row["sa"].values[0]
    else:
        L, M, S = row["lo"].values[0], row["mo"].values[0], row["so"].values[0]

    # Convertir a números de punto flotante
    try:
        L, M, S = float(L), float(M), float(S)
    except ValueError:
        return None, None, None  # Si la conversión falla, retorna None

    return L, M, S


# Función principal para calcular el Z-score
def calcular_zscore(sexo, bus, valor, fecha_nace, fecha_control):
    edad_dias, edad_mes = calcular_edad(fecha_nace, fecha_control)

    # Determinar la tabla de referencia
    if edad_dias < 1875:  # Menores de 5 años
        if bus == 'p':
            tabla = "tablaPEx"
        elif bus == 't':
            tabla = "tablaTEx"
        elif bus == 'i':
            tabla = "tablaIMCx"
        edad_col = "age"
    else:  # Mayores de 5 años
        if bus == 'p':
            tabla = "tablaPE6x"
        elif bus == 't':
            tabla = "tablaTE6x"
        elif bus == 'i':
            tabla = "tablaIMCE6x"
        edad_col = "age_s"

    # Obtener valores L, M, S
    L, M, S = obtener_parametros(tabla, edad_col, edad_dias if edad_col == "age" else edad_mes, sexo, bus)

    if L is None or M is None or S is None:
        return None  # No se encontró una referencia válida

    # Cálculo del Z-score
    zscore = ((valor / M) ** L - 1) / (L * S)
    return zscore

# Ejemplo de uso
fecha_nacimiento = datetime.strptime("2018-01-01", "%Y-%m-%d")
fecha_control = datetime.strptime("2023-06-01", "%Y-%m-%d")
zscore = calcular_zscore(sexo=1, bus='i', valor=14.5, fecha_nace=fecha_nacimiento, fecha_control=fecha_control)

print(f"Z-score calculado: {zscore}")
