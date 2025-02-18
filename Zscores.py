import mysql.connector

# Configura los parámetros de conexión
db_config = {
    "host": "109.106.251.18",        # Cambia si el servidor no está en localhost
    "user": "saltaped_enrique",         # Usuario de MySQL
    "password": "enfi7625",# Cambia por tu contraseña
    "database": "saltaped_sivin2" # Nombre de la base de datos
}

try:
    # Conectar al servidor MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Definir los valores de entrada para la función
    sexo = 2
    bus = 'p'
    valor = 10.5
    fecha_nace = '2021-01-01'
    fecha_control = '2024-02-17'

    # Ejecutar la función ZSCORE
    query = "SELECT ZSCORE(%s, %s, %s, %s, %s)"
    cursor.execute(query, (sexo, bus, valor, fecha_nace, fecha_control))
    # print(query)
    # Obtener y mostrar el resultado
    resultado = cursor.fetchone()
    if resultado:
        print(f"Z-score calculado: {resultado[0]}")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Cerrar conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
