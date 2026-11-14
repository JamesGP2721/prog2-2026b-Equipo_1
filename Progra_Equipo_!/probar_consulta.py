import sqlite3
import pandas as pd

# Conectar a la base de datos creada
conn = sqlite3.connect("estudiantes_ibm.db")

# Ejecutar la consulta SQL uniendo las 3 tablas
query = """
SELECT 
    e.nombre_completo AS Estudiante,
    c.nombre_carrera AS Carrera,
    co.correo_institucional AS Correo,
    co.telefono_whatsapp AS Telefono
FROM Estudiantes e
JOIN Carreras c ON e.id_carrera = c.id_carrera
JOIN Contacto co ON e.id_estudiante = co.id_estudiante;
"""

# Cargar el resultado en un DataFrame e imprimir los primeros 15 registros
df_resultado = pd.read_sql_query(query, conn)
print(df_resultado.head(15))

conn.close()
