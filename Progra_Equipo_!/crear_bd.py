import sqlite3
import pandas as pd

# 1. Cargar el archivo de Excel
excel_file = "University Day_ IBM Campus Jalisco (respuestas).xlsx"
df = pd.read_excel(excel_file)

# 2. Conectar/Crear la base de datos SQLite
conn = sqlite3.connect("estudiantes_ibm.db")
cursor = conn.cursor()

# 3. Crear las 3 tablas
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Carreras (
    id_carrera INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_carrera TEXT NOT NULL UNIQUE
);
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Estudiantes (
    id_estudiante INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_estudiante TEXT,
    nombre_completo TEXT NOT NULL,
    semestre TEXT,
    id_carrera INTEGER NOT NULL,
    FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera)
);
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Contacto (
    id_contacto INTEGER PRIMARY KEY AUTOINCREMENT,
    id_estudiante INTEGER NOT NULL,
    correo_institucional TEXT NOT NULL,
    telefono_whatsapp TEXT,
    FOREIGN KEY (id_estudiante) REFERENCES Estudiantes(id_estudiante)
);
"""
)

# 4. Insertar carreras únicas
carreras_unicas = df["A que carrera perteneces?"].dropna().unique()
for carrera in carreras_unicas:
    cursor.execute(
        "INSERT OR IGNORE INTO Carreras (nombre_carrera) VALUES (?)", (carrera,)
    )

conn.commit()

# Crear mapa de carreras
cursor.execute("SELECT id_carrera, nombre_carrera FROM Carreras")
mapa_carreras = {nombre: id_c for id_c, nombre in cursor.fetchall()}

# 5. Insertar Estudiantes y Contacto
for _, row in df.iterrows():
    nombre = row["Marca temporal 2"]
    codigo = (
        str(int(row["Código de Estudiante"]))
        if pd.notnull(row["Código de Estudiante"])
        else ""
    )
    carrera = row["A que carrera perteneces?"]
    semestre = row["De que semestre eres?"]
    correo = row["Correo Electrónico (Institucional)"]
    telefono = str(row["Cual es tu número de contacto? (Whatsapp)"])

    id_carrera = mapa_carreras.get(carrera)

    if id_carrera and pd.notnull(nombre):
        cursor.execute(
            """
            INSERT INTO Estudiantes (codigo_estudiante, nombre_completo, semestre, id_carrera)
            VALUES (?, ?, ?, ?)
        """,
            (codigo, nombre, semestre, id_carrera),
        )

        id_estudiante = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO Contacto (id_estudiante, correo_institucional, telefono_whatsapp)
            VALUES (?, ?, ?)
        """,
            (id_estudiante, correo, telefono),
        )

conn.commit()
conn.close()

print(
    "¡Base de datos 'estudiantes_ibm.db' creada e importada exitosamente con 3 tablas!"
)