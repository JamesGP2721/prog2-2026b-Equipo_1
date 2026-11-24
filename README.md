# Sistema de Control Escolar (CUGDL SIIAU Escolar) — Hito 2

Sistema orientado a objetos desarrollado en Python para la gestión de alumnos, docentes, asignaturas con cupo limitado, asignación de bloques horarios de dos horas (07:00 a 21:00), registro de calificaciones, bitácora de eventos y persistencia en SQLite.

## Estructura de archivos

* `modelo.py`: Define la jerarquía de herencia (`MiembroUniversitario`, `Alumno`, `Docente`) con polimorfismo en `describir()` y la clase `Materia` (contenedor con cupo limitado, horarios y calificaciones).
* `almacen.py`: Contiene la clase `Bitacora`, la clase `AlmacenSQLite` y las funciones `guardar(sistema, ruta)` y `cargar(sistema, ruta)`.
* `sistema.py`: Implementa la clase coordinadora `SistemaEscolar` con los métodos `registrar(objeto)`, `asignar(identificador, clave)`, `listar()`, `guardar(ruta)` y `cargar(ruta)`, además de todas las reglas de validación.
* `main.py`: Punto de entrada principal para consola; carga la base de datos (sin fallar si no existe), registra datos iniciales si está vacía, lista los registros y guarda el estado.
* `pruebas.py`: Suite de pruebas unitarias (`unittest`) que verifica herencia, validaciones, excepciones, horarios y persistencia.

## Requisitos y ejecución

* **Versión recomendada:** Python 3.10 o superior (solo utiliza la biblioteca estándar `sqlite3`, `unittest` y `datetime`).
* **Ejecutar demostración en consola:** `python3 main.py`
* **Ejecutar pruebas unitarias:** `python3 pruebas.py`
