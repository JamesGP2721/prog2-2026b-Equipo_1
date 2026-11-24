import os
import sqlite3
from datetime import datetime
from modelo import Alumno, Docente, Materia


class Bitacora:
    """Registra cronológicamente cada evento ocurrido dentro del sistema."""

    def __init__(self):
        """Inicializa una lista vacía de eventos cronológicos."""
        self._eventos: list[str] = []

    @property
    def eventos(self) -> tuple[str, ...]:
        """Devuelve una tupla con todos los eventos registrados en la bitácora."""
        return tuple(self._eventos)

    def registrar_evento(self, mensaje: str) -> None:
        """Agrega un nuevo mensaje a la bitácora con marca de fecha y hora."""
        marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._eventos.append(f"[{marca}] {mensaje}")


class AlmacenSQLite:
    """Gestiona el respaldo y recuperación de los datos en bases de datos SQLite."""

    def guardar(self, sistema, ruta: str) -> None:
        """Serializa el estado completo del sistema escolar en un archivo SQLite."""
        if not ruta or not str(ruta).strip():
            raise ValueError("La ruta del archivo de guardado no puede estar vacía.")

        conn = sqlite3.connect(ruta)
        cursor = conn.cursor()
        cursor.executescript(
            """
            DROP TABLE IF EXISTS horarios;
            DROP TABLE IF EXISTS calificaciones;
            DROP TABLE IF EXISTS asignaciones;
            DROP TABLE IF EXISTS materias;
            DROP TABLE IF EXISTS miembros;

            CREATE TABLE miembros (
                codigo TEXT PRIMARY KEY,
                tipo TEXT NOT NULL,
                nombre TEXT NOT NULL,
                detalle TEXT NOT NULL,
                password TEXT NOT NULL,
                debe_cambiar INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE materias (
                clave TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                cupo_maximo INTEGER NOT NULL
            );
            CREATE TABLE asignaciones (
                codigo_miembro TEXT NOT NULL,
                clave_materia TEXT NOT NULL,
                PRIMARY KEY (codigo_miembro, clave_materia)
            );
            CREATE TABLE horarios (
                codigo_miembro TEXT NOT NULL,
                clave_materia TEXT NOT NULL,
                dias TEXT NOT NULL,
                bloque TEXT NOT NULL,
                PRIMARY KEY (codigo_miembro, clave_materia)
            );
            CREATE TABLE calificaciones (
                codigo_alumno TEXT NOT NULL,
                clave_materia TEXT NOT NULL,
                calificacion REAL NOT NULL,
                PRIMARY KEY (codigo_alumno, clave_materia)
            );
            """
        )

        for miembro in sistema.obtener_miembros():
            debe_cambiar = 1 if miembro.debe_cambiar_password else 0
            pwd = miembro.obtener_password_almacenada()
            if isinstance(miembro, Alumno):
                cursor.execute(
                    "INSERT INTO miembros VALUES (?, ?, ?, ?, ?, ?);",
                    (miembro.codigo, "Alumno", miembro.nombre, miembro.carrera, pwd, debe_cambiar),
                )
            elif isinstance(miembro, Docente):
                cursor.execute(
                    "INSERT INTO miembros VALUES (?, ?, ?, ?, ?, ?);",
                    (miembro.codigo, "Docente", miembro.nombre, miembro.departamento, pwd, debe_cambiar),
                )

        for materia in sistema.obtener_materias():
            cursor.execute(
                "INSERT INTO materias VALUES (?, ?, ?);",
                (materia.clave, materia.nombre, materia.cupo_maximo),
            )
            for cod in materia.inscritos:
                cursor.execute(
                    "INSERT INTO asignaciones VALUES (?, ?);",
                    (cod, materia.clave),
                )
            for cod, h in materia.horarios.items():
                cursor.execute(
                    "INSERT INTO horarios VALUES (?, ?, ?, ?);",
                    (cod, materia.clave, ",".join(h["dias"]), h["bloque"]),
                )
            for cod_alumno, nota in materia.calificaciones.items():
                cursor.execute(
                    "INSERT INTO calificaciones VALUES (?, ?, ?);",
                    (cod_alumno, materia.clave, nota),
                )

        conn.commit()
        conn.close()

    def cargar(self, sistema, ruta: str) -> None:
        """Reconstruye el estado del sistema desde SQLite; si el archivo no existe, inicia vacío."""
        sistema.limpiar()
        if not ruta or not os.path.exists(ruta):
            return

        conn = sqlite3.connect(ruta)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='miembros';"
            )
            if not cursor.fetchone():
                return

            cursor.execute("PRAGMA table_info('miembros');")
            cols = {c[1] for c in cursor.fetchall()}

            if "password" in cols and "debe_cambiar" in cols:
                cursor.execute(
                    "SELECT codigo, tipo, nombre, detalle, password, debe_cambiar FROM miembros;"
                )
                filas = cursor.fetchall()
            else:
                cursor.execute("SELECT codigo, tipo, nombre, detalle FROM miembros;")
                filas = [(c, t, n, d, c, 1) for c, t, n, d in cursor.fetchall()]

            for codigo, tipo, nombre, detalle, pwd, debe_cambiar in filas:
                if tipo == "Alumno":
                    sistema.registrar(Alumno(codigo, nombre, detalle, pwd, bool(debe_cambiar)))
                elif tipo == "Docente":
                    sistema.registrar(Docente(codigo, nombre, detalle, pwd, bool(debe_cambiar)))

            cursor.execute("SELECT clave, nombre, cupo_maximo FROM materias;")
            for clave, nombre, cupo in cursor.fetchall():
                sistema.registrar(Materia(clave, nombre, int(cupo)))

            horarios_map: dict[tuple[str, str], tuple[list[str], str]] = {}
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='horarios';"
            )
            if cursor.fetchone():
                cursor.execute(
                    "SELECT codigo_miembro, clave_materia, dias, bloque FROM horarios;"
                )
                for cod, clv, dias_str, bloque in cursor.fetchall():
                    dias_list = [d.strip() for d in dias_str.split(",") if d.strip()]
                    horarios_map[(cod, clv)] = (dias_list, bloque)

            cursor.execute("SELECT codigo_miembro, clave_materia FROM asignaciones;")
            for codigo_miembro, clave_materia in cursor.fetchall():
                h = horarios_map.get((codigo_miembro, clave_materia))
                if h:
                    sistema.asignar(codigo_miembro, clave_materia, h[0], h[1])
                else:
                    sistema.asignar(codigo_miembro, clave_materia)

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='calificaciones';"
            )
            if cursor.fetchone():
                cursor.execute(
                    "SELECT codigo_alumno, clave_materia, calificacion FROM calificaciones;"
                )
                for codigo_alumno, clave_materia, nota in cursor.fetchall():
                    sistema.calificar(codigo_alumno, clave_materia, float(nota))
        finally:
            conn.close()

    def importar_desde_bd_previa(self, sistema, ruta_bd: str) -> int:
        """Importa registros de estudiantes desde una base de datos SQLite externa."""
        if not os.path.exists(ruta_bd):
            raise ValueError(f"No se encontró la base de datos '{ruta_bd}'.")

        conn = sqlite3.connect(ruta_bd)
        cursor = conn.cursor()
        importados = 0
        try:
            cursor.execute(
                """
                SELECT e.codigo_estudiante, e.nombre_completo, c.nombre_carrera
                FROM Estudiantes e
                JOIN Carreras c ON e.id_carrera = c.id_carrera;
                """
            )
            for codigo, nombre, carrera in cursor.fetchall():
                try:
                    sistema.registrar(Alumno(codigo, nombre, carrera))
                    importados += 1
                except ValueError:
                    continue
        finally:
            conn.close()
        return importados


def guardar(sistema, ruta: str) -> None:
    """Escribe el estado del sistema en el archivo de base de datos indicado por ruta."""
    AlmacenSQLite().guardar(sistema, ruta)


def cargar(sistema, ruta: str) -> None:
    """Lee el archivo indicado por ruta y reconstruye el estado del sistema."""
    AlmacenSQLite().cargar(sistema, ruta)